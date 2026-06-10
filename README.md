# The Unofficial Guide — Project 1

---

## Domain

This guide covers dining at Cal State East Bay — on-campus spots, nearby off-campus restaurants, and meal plan info. CSUEB's dining options are limited and the useful stuff (honest reviews, whether the meal plan is worth it, what's actually open) is scattered across Yelp, Reddit, and a student newspaper most incoming students don't even know exists. There's no single place that pulls it all together, and the official university website only gives you sanitized descriptions with no student perspective.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit: Best Food Spots | Student forum thread | https://www.reddit.com/r/CSUEB/comments/1gw7iil/best_food_spots/ |
| 2 | Reddit: Restaurant Recs After Graduation | Student forum thread | https://www.reddit.com/r/CSUEB/comments/1tdyp39/restaurant_recs_for_after_graduation/ |
| 3 | Pioneer Online: The Cuisine Congestion of CSUEB | Student newspaper opinion | https://thepioneeronline.com/28223/opinions/the-cuisine-congestion-of-csueb/ |
| 4 | Pioneer Online: Five Local Spots to Grab Food Off Campus | Student newspaper article | https://thepioneeronline.com/22787/campus/five-local-spots-to-grab-food-off-campus/ |
| 5 | Yelp: Dining Commons at Cal State East Bay | Student reviews | https://www.yelp.com/biz/dining-commons-at-cal-state-east-bay-hayward |
| 6 | Yelp: Wild Blue Hayward | Student reviews | https://www.yelp.com/biz/wild-blue-hayward |
| 7 | Yelp: Einstein Bros Bagels Hayward | Student reviews | https://www.yelp.com/biz/einstein-bros-bagels-hayward |
| 8 | Dine On Campus: CSUEB Official Dining Hours | Official hours portal | https://dineoncampus.com/csueb/hours-of-operation |
| 9 | CSUEB Meal Plans (official PDF) | Official document | documents/04_meal_plans.txt |
| 10 | CSUEB Food Recommendations Guide (official PDF) | Official document | documents/01_on_campus_food_guide.txt |

---

## Chunking Strategy

**Chunk size:** ~400 characters

**Overlap:** ~80 characters

**Why these choices fit your documents:** About 80% of my content is short — Yelp reviews and Reddit comments are typically 1–3 sentences each. A 400-character chunk size keeps individual reviews intact rather than merging multiple unrelated opinions into one chunk. If chunks were too large, a question about Wild Blue might retrieve a chunk that's half about Panda Express, diluting the answer. The 80-character overlap protects the directory-style documents (like the on-campus food guide), where a restaurant's name might land at the end of one chunk and its location at the start of the next — the overlap carries the name across the boundary so neither chunk loses context. For longer documents like the meal plan PDF and the Pioneer Online articles, the chunks naturally pack a few paragraphs together, which is fine since those documents have concentrated facts that don't need to be broken up. Preprocessing: stripped stray HTML tags, decoded HTML entities, and collapsed excess whitespace before chunking.

**Final chunk count:** 88 chunks across 10 documents

### Sample Chunks

**Chunk 1** — `01_on_campus_food_guide.txt` (chunk 1)
```
PIONEER KITCHEN (Dining Commons)
Location: Pioneer Heights residential area
Description: The main dining commons at CSUEB. Offers all-you-care-to-eat meals during
the week from morning to evening. Menu includes healthy foods and vegetarian selections,
a variety of salads, hot foods, desserts, and a rotating Chef's Special that highlights
foods from different cultures. Accepts meal plan swipes. Freshmen living on campus are
required to purchase a meal plan.
```

**Chunk 2** — `01_on_campus_food_guide.txt` (chunk 3)
```
TAQUERIA ANGELICA'S
Location: Old University Union (enter from main walkway, walk to back of building)
Description: Mexican food. Menu includes tacos, burritos, burrito bowls, and other
Mexican-American options. Replaced the previous Fry Shack location.
Hours (regular semester): Thursday 10:30am–4pm, Friday 10:30am–2pm, Saturday Closed
```

**Chunk 3** — `04_meal_plans.txt` (chunk 2)
```
BLACK 15 PLAN
- 15 meal swipes per week (usable at Pioneer Kitchen for breakfast, lunch, dinner, or late night)
- $100 Flex Dollars per semester
- 5 Meal Exchange swipes per week
- 5 Guest meal swipes per semester
Cost: Fall semester $3,102 / Spring semester $3,153
```

**Chunk 4** — `05_yelp_dining_commons.txt` (chunk 3)
```
Super hit or miss. Sometimes it's great but sometimes there's hardly anything edible.
Cookies always hit though and the soft serve is good when it works. Kind of not cool
that they force residents to get a meal plan and then have limited hours and food options.
```

**Chunk 5** — `10_reddit_food_threads.txt` (chunk 2)
```
Mujiri is my favorite sushi in the East Bay, located in downtown Hayward. If you're okay
going a bit further in the same direction, in Castro Valley there's Lucca Deli. Right at
the bottom of the hill on Mission there's La Vic's for burritos. World Famous HotBoys
Chicken truck on Mission. Right behind the school there's Bronco Billy's pizza.
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via ChromaDB's built-in ONNX embedding function. Runs entirely locally — no API key, no rate limits, no cost.

**Production tradeoff reflection:** For a real deployment I'd consider a larger model like OpenAI's `text-embedding-3-large` for better accuracy on informal, slang-heavy text like Reddit comments and Yelp reviews — the kind of casual language that all-MiniLM-L6-v2 sometimes struggles to match semantically. I'd also weigh local vs. API tradeoffs: running locally is free and keeps user data private, but an API-hosted model is easier to scale and typically faster under load. For a multilingual campus community a model like `paraphrase-multilingual-MiniLM-L12-v2` would be worth exploring, though the CSUEB corpus is all English so it wasn't a priority here. Context length is less of a concern for this corpus since most chunks are under 400 characters, well within any model's limits.

---

## Grounded Generation

**System prompt grounding instruction:**
```
You are a helpful assistant for the CSUEB Unofficial Dining Guide.
Answer the user's question using ONLY the information provided in the context below.
Do not use any outside knowledge.
If the context does not contain enough information to answer, respond with exactly:
"I don't have enough information on that."
Always be concise and cite which document your answer comes from.
```

Temperature is set to `0.1` to minimize the model deviating from the retrieved context.

**How source attribution is surfaced in the response:** Source filenames are appended programmatically from chunk metadata after generation — they are never left to the model to generate or invent. If the model returns a refusal, the sources list is set to empty automatically in code.

### Example Responses

**Example 1 — Factual, single source:**
> **Q:** What are the hours for Einstein Bros Bagels during the regular semester?
>
> **A:** The hours for Einstein Bros. Bagels during the regular semester are: Thursday 7:30am–6pm, Friday 7:30am–4pm, Saturday Closed. [Source: 01_on_campus_food_guide.txt]
>
> **Sources:** 01_on_campus_food_guide.txt, 03_official_hours_summer2026.txt, 06_yelp_einstein_bros.txt

**Example 2 — Opinion synthesis across multiple sources:**
> **Q:** What do students say about the Dining Commons at CSUEB?
>
> **A:** Students express negative opinions about the Dining Commons, with one warning others to "run the other way" if invited, calling it a "trap" (05_yelp_dining_commons.txt). Additionally, students have dealt with the dining situation for too long, implying long-standing dissatisfaction (08_article_cuisine_congestion.txt).
>
> **Sources:** 01_on_campus_food_guide.txt, 05_yelp_dining_commons.txt, 08_article_cuisine_congestion.txt

**Example 3 — Out-of-scope refusal:**
> **Q:** What is the best gym near CSUEB?
>
> **A:** I don't have enough information on that.
>
> **Sources:** No sources — question may be out of scope.

---

## Query Interface

**Tool:** Gradio web app (`app.py`)
**Run:** `python app.py` then open http://localhost:7860

**Input field:** "Your question" — a free-text box where the user types any dining-related question

**Output fields:**
- "Answer" — the grounded LLM response
- "Sources" — a bullet list of document filenames the answer was drawn from

**Sample interaction transcript:**
> **Input:** Does the meal plan roll over unused swipes to the next week?
>
> **Answer:** No, unused meal swipes do NOT roll over week to week. (Source: 04_meal_plans.txt)
>
> **Sources:** 04_meal_plans.txt

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the hours for Einstein Bros Bagels during the regular semester? | Thursday 7:30am–6pm, Friday 7:30am–4pm, Saturday closed | "The hours are: Thursday 7:30am–6pm, Friday 7:30am–4pm, Saturday Closed." | Relevant | Accurate |
| 2 | What is the cost of the Black 15 meal plan per semester? | Fall $3,102 / Spring $3,153 | "Not explicitly stated in the Black 15 description, but mentioned elsewhere: Fall $3,102 / Spring $3,153." | Relevant | Partially accurate |
| 3 | What do students say about the Dining Commons at CSUEB? | Mixed — limited options, crowded, but convenient for residents | "Students express negative opinions — one called it a trap, another cited long-standing dissatisfaction." | Relevant | Accurate |
| 4 | What off-campus restaurants do CSUEB students recommend? | Los Dos Hermanos, Le Paradis, Bronco Billy's, others | "Buon Appetito (Italian), Chef's Experience (Chinese), Hinata Sushi, Mexico Tipico." | Partially relevant | Partially accurate |
| 5 | Does the meal plan roll over unused swipes to the next week? | No — unused swipes not refunded or held in reserve | "No, unused meal swipes do NOT roll over week to week." | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "Is the food at Einstein Bros fresh?"

**What the system returned:** "I don't have enough information on that."

**Root cause (tied to a specific pipeline stage):** This is a retrieval failure. The
corpus contains an entire document of Einstein Bros reviews (`06_yelp_einstein_bros.txt`)
that directly address food quality — one reviewer mentions "bagels sitting in a container
box for who knows how long," another describes them as "doughy," and one reports possible
food poisoning. The answer is clearly in the documents. The failure happened because the
query used the word "fresh" directly, while reviewers described the same concept
indirectly — "sitting in a container box," "didn't taste fresh out the skillet," "doughy."
The embedding model couldn't bridge that gap in phrasing, the similarity scores came back
too low, and the LLM had no retrieved context to work with, so it correctly refused rather
than hallucinating.

**What you would change to fix it:** Query expansion — automatically rewriting the user's
question into multiple phrasings before retrieval ("Is the food fresh?" → also search "food
quality," "how do the bagels taste," "are the bagels good") — would increase the chance of
matching the indirect language reviewers actually use. A larger embedding model with better
semantic coverage of informal food-review language would also help.

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the chunking strategy in planning.md before touching any code forced a real decision about why 400 characters made sense for this specific corpus. That choice — keeping Yelp reviews as whole chunks rather than splitting mid-sentence — came directly from noticing during document collection that 80% of the content was 1–3 sentences long. Without the spec that decision would have been arbitrary.

**One way your implementation diverged from the spec, and why:** The spec assumed sentence-transformers would be installed directly to load all-MiniLM-L6-v2. Instead ChromaDB's built-in ONNX embedding function was used, which runs the same model without requiring a separate PyTorch installation. This was faster to set up and avoided a large dependency, with no difference in embedding output quality.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* My Chunking Strategy and Documents sections from planning.md, plus the 10 raw source documents
- *What it produced:* `ingest.py` with a paragraph-aware chunker using 400-character chunks and 80-character overlap, a `clean()` function that strips HTML and normalizes whitespace, and a ChromaDB ingestion loop that attaches source metadata to every chunk
- *What I changed or overrode:* Reviewed the 5 sample chunks printed by the script and confirmed they were self-contained before moving on. The overlap logic was kept as-is because the chunks correctly carried context across boundaries.

**Instance 2**

- *What I gave the AI:* Screenshots of all 5 evaluation question responses from the live Gradio app, plus the starter README template
- *What it produced:* A fully filled README matching the template, including the evaluation table with accuracy judgments and the failure case analysis for Question 4
- *What I changed or overrode:* The failure case explanation accurately reflects what actually happened — the system genuinely pulled from the graduation thread instead of the off-campus guide — so it was kept as written. The AI usage section was written to accurately reflect what happened during the project.

---

## How to Run

```bash
# 1. Clone and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install chromadb groq gradio python-dotenv

# 3. Add your Groq API key
cp .env.example .env
# Edit .env: set GROQ_API_KEY=your_key_here

# 4. Build the vector store
python ingest.py

# 5. Launch the app
python app.py
# Open http://localhost:7860
```
