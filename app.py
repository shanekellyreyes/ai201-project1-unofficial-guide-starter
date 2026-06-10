"""
app.py — Gradio web interface for the CSUEB Unofficial Dining Guide.

Run:
    python app.py
Then open: http://localhost:7860
"""

import gradio as gr
from query import ask


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "No sources — question may be out of scope."
    return result["answer"], sources


with gr.Blocks(title="CSUEB Unofficial Dining Guide") as demo:
    gr.Markdown("""
    # 🍜 CSUEB Unofficial Dining Guide
    Ask anything about food on and around Cal State East Bay.
    Answers are grounded in real student reviews, articles, and official documents.
    """)

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students think of the dining commons? Is the meal plan worth it?"
    )
    btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Sources", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
