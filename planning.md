# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

This guide covers dining at Cal State East Bay — on-campus spots, nearby off-campus restaurants, and meal plan info. CSUEB's dining options are limited and the useful stuff (honest reviews, whether the meal plan is worth it, what's actually open) is scattered across Yelp, Reddit, and a student newspaper most incoming students don't even know exists. There's no single place that pulls it all together.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or File Path |
|---|--------|-------------|-----------------|
| 1 | Reddit: Best Food Spots | Student thread recommending food spots on and near campus | https://www.reddit.com/r/CSUEB/comments/1gw7iil/best_food_spots/ |
| 2 | Reddit: Restaurant Recs After Graduation | Student thread with off-campus restaurant recommendations | https://www.reddit.com/r/CSUEB/comments/1tdyp39/restaurant_recs_for_after_graduation/ |
| 3 | Pioneer Online: The Cuisine Congestion of CSUEB | Student opinion piece on limited and crowded campus dining | https://thepioneeronline.com/28223/opinions/the-cuisine-congestion-of-csueb/ |
| 4 | Pioneer Online: Five Local Spots to Grab Food Off Campus | Student journalism piece recommending nearby off-campus restaurants | https://thepioneeronline.com/22787/campus/five-local-spots-to-grab-food-off-campus/ |
| 5 | Yelp: Dining Commons at CSUEB | Student and visitor reviews of the main campus dining hall | https://www.yelp.com/biz/dining-commons-at-cal-state-east-bay-hayward |
| 6 | Yelp: Wild Blue Hayward | Student reviews of the on-campus poke bar | https://www.yelp.com/biz/wild-blue-hayward |
| 7 | Yelp: Einstein Bros Bagels Hayward | Student reviews of the on-campus bagel shop | https://www.yelp.com/biz/einstein-bros-bagels-hayward |
| 8 | Dine On Campus: CSUEB Official Dining | Official dining portal with hours, locations, and menus | https://dineoncampus.com/csueb |
| 9 | CSUEB Meal Plans PDF | Official document covering meal plan options, costs, flex dollars, and swipe rules | documents/04_meal_plans.txt |
| 10 | CSUEB Food Recommendations PDF | Campus-produced guide to on-campus and off-campus food options with hours and locations | documents/01_on_campus_food_guide.txt |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

Most of my documents are short — Yelp reviews and Reddit comments are usually
1–3 sentences, so about 80% of my content is already pretty bite-sized. Because
of that, I'm using a chunk size of ~400 characters with ~80 characters of overlap.

The small chunk size keeps individual reviews from getting merged together — if
chunks were too big, a question about Wild Blue might pull back a chunk that's
half about Panda Express. The overlap exists mainly to protect the directory-style
documents (like the food recommendations PDF), where a restaurant's name might
land in one chunk and its location in the next. The overlap makes sure key
identifiers like the name carry across boundaries so neither chunk is missing
context.

For longer documents like the meal plan PDF and the Pioneer Online articles, the
chunks will naturally stack a few paragraphs together, which is fine — those
documents have concentrated facts that don't need to be broken up much anyway.

Method: paragraph-aware splitting — split on blank lines first to keep whole
reviews intact, hard-split on character count only when a paragraph exceeds 400
characters.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

I'm using the all-MiniLM-L6-v2 embedding model via ChromaDB's built-in ONNX
function — it runs locally with no API key and no rate limits, which keeps
things simple.

For top-k I'm retrieving 4 chunks per query. That's enough to cover a question
that might need a couple of different sources (like "what's good to eat on
campus?") without flooding the LLM with loosely related content that pulls the
answer off track. Too few and you miss relevant info; too many and you dilute it.

Semantic search works here even when the query doesn't share exact words with
the document — it matches on meaning, not keywords. So "is the dining hall worth
it" can still find a review that says "the meal swipes go to waste if you don't
use them every week" because the underlying meaning is close.

If I were deploying this for real users, I'd consider a larger model like
text-embedding-3-large from OpenAI for better accuracy on informal, slang-heavy
text like Reddit comments. I'd also weigh the tradeoff between running locally
(free, private, slower) versus an API (costs money, faster, easier to scale).
For a multilingual campus I'd look at a multilingual model too, but for CSUEB
this corpus is all English so it's not a priority.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected Answer |
|---|----------|-----------------|
| 1 | What are the hours for Einstein Bros Bagels during the regular semester? | Thursday 7:30am–6pm, Friday 7:30am–4pm, Saturday closed |
| 2 | What is the cost of the Black 15 meal plan per semester? | Fall $3,102 / Spring $3,153 |
| 3 | What do students say about the Dining Commons at CSUEB? | Reviews are mixed — limited options, can get crowded, but convenient for on-campus residents |
| 4 | What off-campus restaurants do CSUEB students recommend? | Los Dos Hermanos, Le Paradis, and others from the Pioneer Online article and Reddit threads |
| 5 | Does the meal plan roll over unused swipes to the next week? | No — unused weekly meal swipes are not refunded or held in reserve |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Thin Yelp content:** Several of the on-campus Yelp pages have very few
   reviews — Wild Blue and Einstein Bros might only have a handful. If those
   documents are sparse, retrieval for questions about those spots will either
   return weak matches or pull from unrelated sources instead.

2. **Seasonal hours confusion:** The official hours document reflects summer 2026,
   when most locations are closed. If a student asks "is Panda Express open today?"
   during the regular semester, the system might confidently return the wrong
   answer because it's grounded in summer data. The system has no way to know
   what time of year it's being used.

3. **Short chunks losing context:** Because most reviews are 1–3 sentences, some
   chunks will be very short and stripped of context — a review that says "totally
   worth it" with no subject will be hard to match to any specific query.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
Raw Documents (.txt, scraped web content)
        |
        v
[ Document Ingestion ]
  - Load .txt files from /documents
  - Clean: strip HTML, normalize whitespace
  - Tool: Python (open, re)
        |
        v
[ Chunking ]
  - Paragraph-aware splitting
  - Chunk size: ~400 chars, Overlap: ~80 chars
  - Tool: Python (custom chunk_text())
        |
        v
[ Embedding + Vector Store ]
  - Embed each chunk
  - Store with source metadata
  - Tool: ChromaDB + all-MiniLM-L6-v2 (ONNX)
        |
        v
[ Retrieval ]
  - Semantic similarity search
  - Return top-4 chunks + source names
  - Tool: ChromaDB (cosine distance)
        |
        v
[ Generation ]
  - Grounded response from retrieved context only
  - Source attribution appended programmatically
  - Tool: Groq (llama-3.3-70b-versatile)
        |
        v
[ Query Interface ]
  - Input: user question
  - Output: answer + sources
  - Tool: Gradio
```
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

1. **Ingestion and chunking (ingest.py):** I'll give Claude my Chunking Strategy
   section and the Documents list and ask it to implement the document loading,
   cleaning, and chunk_text() function matching my 400-character / 80-character
   overlap spec.

2. **Embedding and retrieval (query.py):** I'll give Claude my Retrieval Approach
   section and ask it to implement the ChromaDB setup, the embedding step using
   all-MiniLM-L6-v2, and a retrieve() function that returns top-4 chunks with
   source metadata.

3. **Grounded generation (query.py):** I'll give Claude the grounding requirement
   from the project instructions and ask it to write the Groq API call and system
   prompt that forces the model to answer only from retrieved context and refuse
   out-of-scope questions.

4. **Gradio interface (app.py):** I'll give Claude the interface requirements and
   ask it to build a simple two-output Gradio app showing the answer and source
   list separately.

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
