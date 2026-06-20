# Voice Cloning PoC

A tiny proof-of-concept: **record your voice, type a sentence, and hear that
sentence spoken back in your voice.**

It uses **zero-shot voice cloning** — an open model
([Chatterbox](https://github.com/resemble-ai/chatterbox) by Resemble AI, MIT
licensed) clones a voice from a few seconds of reference audio with *no
per-voice training step*. That makes the "record → instantly speak" loop
possible in real time.

> Note on the "fine-tune" idea: a per-voice LoRA fine-tune gives higher
> fidelity, but needs minutes–hours of audio plus a GPU training pass, which is
> too heavy for an instant record-and-speak demo. Zero-shot cloning is the right
> starting point; a fine-tune path can be added later as a quality upgrade.

## How it works

```
your voice clip ─┐
                 ├─► TTS model (predicts neural audio-codec tokens) ─► spoken sentence
your sentence ───┘        conditioned on the reference voice
```

Modern TTS is essentially a transformer that predicts neural-audio-codec tokens;
"cloning" means conditioning that model on a reference clip of the target voice.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Gradio web UI: record/upload reference, enter text, play result |
| `tts_engine.py` | Loads the model once; `synthesize(text, reference_path)` |
| `requirements.txt` | Dependencies |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
```

For GPU speed, install the CUDA build of PyTorch from
<https://pytorch.org/get-started/locally/> **before** the line above.

## Run

```bash
python app.py
```

Open the local URL Gradio prints, then:

1. **Record** ~6–10s of clean speech (or upload a clip).
2. **Type** a sentence.
3. Click **Speak** and listen.

## View it on your phone

The app runs on your computer (it loads the model); your phone is just the client.

```bash
python app.py --share
```

This prints a temporary **HTTPS** link like `https://xxxx.gradio.live` — open that on
your phone, then record, type, and Speak.

Why the share link (and not your LAN IP)? Phone browsers only allow **microphone
recording over HTTPS**. Opening the app via `http://192.168.x.x:7860` on the same Wi‑Fi
would load the page but the browser would **block the mic** — so use `--share`.

- The link is **temporary (~72h)** and, while live, **anyone who has it can reach the app**.
- Password-protect it: `GRADIO_AUTH="me:secret" python app.py --share`.
- Env equivalents: `GRADIO_SHARE=1` (same as `--share`), `GRADIO_PORT` (default 7860).

## Caveats

- **First run downloads model weights** from Hugging Face — needs internet.
- **CPU works** for short sentences (slower); a GPU is much faster.
- **Reference quality matters** — ~6–10s of clean, single-speaker audio clones best.
- **Consent:** only clone voices you have the right to use.

## Possible next steps

- Add a LoRA fine-tune path on an open speech-LLM for higher fidelity.
- Swap in an alternative engine (e.g. Coqui XTTS-v2, F5-TTS) behind `tts_engine.synthesize`.
- Build toward a full voice agent (speech-to-text → LLM → this TTS).
