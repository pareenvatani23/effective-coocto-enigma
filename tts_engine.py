"""Zero-shot voice cloning engine.

Wraps an open zero-shot text-to-speech model behind a single ``synthesize``
function so the UI never needs to know which model is in use. The default
engine is Chatterbox (Resemble AI, MIT licensed), which clones a voice from a
short reference clip with no per-voice training step.

Swapping the engine: keep the ``synthesize(text, reference_path) -> wav_path``
signature and the rest of the app keeps working.
"""

from __future__ import annotations

import os
import uuid

OUTPUT_DIR = "outputs"

# The model is heavy to load, so we keep a single instance alive for the
# process and build it lazily on first use.
_model = None
_device = None


def _select_device() -> str:
    """Pick the best available compute device."""
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        # Apple Silicon
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def _get_model():
    """Load (once) and return the cloning model."""
    global _model, _device
    if _model is not None:
        return _model

    from chatterbox.tts import ChatterboxTTS

    _device = _select_device()
    print(f"[tts_engine] loading Chatterbox on device={_device} (first run downloads weights)...")
    _model = ChatterboxTTS.from_pretrained(device=_device)
    print("[tts_engine] model ready.")
    return _model


def synthesize(text: str, reference_path: str) -> str:
    """Speak ``text`` in the voice from ``reference_path``.

    Args:
        text: The sentence to speak.
        reference_path: Path to a short (~6-10s) reference wav of the target voice.

    Returns:
        Path to the generated wav file under ``outputs/``.
    """
    if not text or not text.strip():
        raise ValueError("Please enter a sentence to speak.")
    if not reference_path or not os.path.exists(reference_path):
        raise ValueError("Please record or upload a reference voice clip first.")

    model = _get_model()

    # Chatterbox returns a torch tensor of audio at model.sr.
    wav = model.generate(text.strip(), audio_prompt_path=reference_path)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4().hex}.wav")

    import torchaudio

    torchaudio.save(out_path, wav, model.sr)
    return out_path
