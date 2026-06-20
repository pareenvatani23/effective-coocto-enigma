"""Voice cloning PoC — record your voice, type a sentence, hear it in your voice.

Run locally:
    python app.py

View it on your phone (creates a temporary HTTPS link the mic can use):
    python app.py --share

Then open the URL Gradio prints. Record ~6-10s of clean speech, type a
sentence, and click "Speak".
"""

from __future__ import annotations

import argparse
import os
import shutil
import uuid

import gradio as gr

import tts_engine

VOICES_DIR = "voices"


def save_reference(recorded_path: str | None) -> str:
    """Copy the recorded/uploaded clip into voices/ so it persists, return its path."""
    if not recorded_path:
        raise gr.Error("No reference audio yet — record or upload a clip first.")
    os.makedirs(VOICES_DIR, exist_ok=True)
    ext = os.path.splitext(recorded_path)[1] or ".wav"
    dest = os.path.join(VOICES_DIR, f"{uuid.uuid4().hex}{ext}")
    shutil.copyfile(recorded_path, dest)
    return dest


def speak(recorded_path: str | None, text: str):
    """Clone the recorded voice and synthesize ``text`` in it."""
    if not recorded_path:
        raise gr.Error("Record or upload a reference voice clip first.")
    if not text or not text.strip():
        raise gr.Error("Type a sentence for the app to speak.")

    reference = save_reference(recorded_path)
    try:
        out_path = tts_engine.synthesize(text, reference)
    except Exception as exc:  # surface engine errors in the UI
        raise gr.Error(f"Synthesis failed: {exc}")
    return out_path


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Voice Cloning PoC") as demo:
        gr.Markdown(
            "# 🎙️ Voice Cloning PoC\n"
            "1. **Record** ~6–10s of your voice (or upload a clip).\n"
            "2. **Type** a sentence.\n"
            "3. Click **Speak** to hear it in your voice.\n\n"
            "_Only clone voices you have permission to use._"
        )
        with gr.Row():
            reference = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="Your voice (reference clip)",
            )
            with gr.Column():
                text = gr.Textbox(
                    label="Sentence to speak",
                    placeholder="Hello — this is my cloned voice.",
                    lines=3,
                )
                speak_btn = gr.Button("Speak", variant="primary")
        output = gr.Audio(label="Generated speech", autoplay=True)

        speak_btn.click(fn=speak, inputs=[reference, text], outputs=output)

    return demo


def _parse_auth(value: str | None):
    """Turn 'user:pass' into a Gradio auth tuple, or None if unset/blank."""
    if not value or ":" not in value:
        return None
    user, _, password = value.partition(":")
    return (user, password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice cloning PoC")
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a temporary public HTTPS link (needed to use the mic on a phone).",
    )
    args = parser.parse_args()

    build_ui().launch(
        share=args.share or os.getenv("GRADIO_SHARE") == "1",
        server_name="0.0.0.0",  # reachable on the LAN too (desktop on same Wi-Fi)
        server_port=int(os.getenv("GRADIO_PORT", "7860")),
        auth=_parse_auth(os.getenv("GRADIO_AUTH")),  # set GRADIO_AUTH=user:pass to lock it
    )
