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


def synthesize(
    text: str,
    reference_path: str,
    exaggeration: float = 0.4,
    cfg_weight: float = 0.3,
    temperature: float = 0.7,
) -> str:
    """Speak ``text`` in the voice from ``reference_path``.

    Args:
        text: The sentence to speak.
        reference_path: Path to a short (~10-20s) reference wav of the target voice.
        exaggeration: Emotion/expressiveness intensity. Lower values stay closer
            to the reference speaker's natural delivery (better for similarity);
            higher values are more dramatic. Chatterbox default is 0.5.
        cfg_weight: Classifier-free guidance weight. Lower values track the
            reference voice more faithfully (and slow the pace slightly);
            higher values push toward the text/prosody. Chatterbox default 0.5.
        temperature: Sampling randomness. Lower is more stable and consistent;
            higher is more varied. Chatterbox default 0.8.

    Returns:
        Path to the generated wav file under ``outputs/``.
    """
    if not text or not text.strip():
        raise ValueError("Please enter a sentence to speak.")
    if not reference_path or not os.path.exists(reference_path):
        raise ValueError("Please record or upload a reference voice clip first.")

    model = _get_model()

    # Chatterbox returns a torch tensor of audio at model.sr. The defaults above
    # lean toward speaker similarity rather than Chatterbox's more expressive
    # out-of-the-box defaults.
    wav = model.generate(
        text.strip(),
        audio_prompt_path=reference_path,
        exaggeration=exaggeration,
        cfg_weight=cfg_weight,
        temperature=temperature,
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4().hex}.wav")

    import torchaudio

    torchaudio.save(out_path, wav, model.sr)
    return out_path
