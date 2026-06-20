# Running the PoC in a GitHub Codespace

A [Codespace](https://github.com/features/codespaces) is a cloud dev container
GitHub spins up for this repo. It has **full internet** (so it can download the
model from Hugging Face — this is the piece the Claude session container can't do)
and **HTTPS port forwarding** (so your phone's browser will let you use the mic).

The repo ships a `.devcontainer/` config that builds from the project `Dockerfile`,
so the Codespace comes up with `ffmpeg`, `libsndfile`, and all Python deps
(`torch`, `chatterbox-tts`, `gradio`) already installed.

## Steps

1. On GitHub: **Code ▸ Codespaces ▸ Create codespace on `main`**.
   (First build takes a few minutes — it installs torch + chatterbox.)
2. In the Codespace terminal:
   ```bash
   python app.py
   ```
3. Open the **PORTS** tab. You'll see port **7860** forwarded.
4. **Right-click port 7860 ▸ Port Visibility ▸ Public.**
   This is required so your phone can reach it without a GitHub login.
5. Copy the `https://...app.github.dev` URL for port 7860 and open it **on your
   phone**. Because it's HTTPS, the browser allows mic recording.
6. Record ~6–10s of speech (or upload a clip), type a sentence, tap **Speak**.

## Notes

- **First Speak is slow.** It downloads model weights once, then synthesizes on
  CPU. A default 2-core Codespace works but isn't fast; bump the machine type
  (Codespace menu ▸ Change machine type) for more cores/RAM.
- **Make the port private again** when you're done (Port Visibility ▸ Private), or
  just stop/delete the Codespace — public ports are reachable by anyone with the URL.
- **Codespaces uses your free monthly hours**; stop the Codespace when idle.
- Prefer a permanent URL instead of a running Codespace? See `DEPLOY_HF_SPACES.md`.
