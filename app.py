"""
app.py — Gradio web interface for The Unofficial Guide: ND Professor Reviews.

Run with:
    python app.py

Then open http://localhost:7860 in your browser.
"""

import gradio as gr
from generator import ask


def handle_query(question: str):
    """Wrapper called by Gradio on each submission."""
    question = question.strip()
    if not question:
        return "Please enter a question.", ""

    result = ask(question)

    answer = result["answer"]

    # Format sources as a readable list
    if result["sources"]:
        sources_text = "\n".join(
            f"• {src.replace('_rmp.txt', '').replace('prof_', 'Prof. ').replace('_', ' ').title()}"
            f"  ({src})"
            for src in result["sources"]
        )
    else:
        sources_text = "No sources retrieved."

    return answer, sources_text


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="ND Professor Unofficial Guide") as demo:
    gr.Markdown(
        """
        # 🎓 Notre Dame Professor Unofficial Guide
        Ask questions about Notre Dame CSE/IT professors based on real Rate My Professors reviews.

        **Examples:**
        - *What is Katherine Walden's grading system?*
        - *How hard are Peter Bui's exams in Systems Programming?*
        - *Is Ramzi Bualuan good for students with no CS experience?*
        - *What do students say about Tijana Milenkovic's grading?*
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            question_box = gr.Textbox(
                label="Your Question",
                placeholder="e.g. Does Daniel Cedre require office hours to pass CSE10001?",
                lines=2,
            )
            ask_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        with gr.Column(scale=2):
            answer_box = gr.Textbox(
                label="Answer",
                lines=8,
                interactive=False,
            )
        with gr.Column(scale=1):
            sources_box = gr.Textbox(
                label="Retrieved from",
                lines=8,
                interactive=False,
            )

    gr.Markdown(
        "_Answers are grounded in collected RMP reviews only. "
        "If the documents don't cover your question, the system will say so._"
    )

    # Wire up both button click and Enter key
    ask_btn.click(handle_query, inputs=question_box, outputs=[answer_box, sources_box])
    question_box.submit(handle_query, inputs=question_box, outputs=[answer_box, sources_box])


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
