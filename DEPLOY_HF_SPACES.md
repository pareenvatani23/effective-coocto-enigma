# Deploying to Hugging Face Spaces

This app is Spaces-ready: the config lives in the frontmatter at the top of
`README.md` (`sdk: gradio`, `app_file: app.py`). Spaces gives you a persistent
**HTTPS** URL, which is exactly what a phone needs to record from the mic.

> Why not deploy from the Claude session container? Its network policy blocks
> `huggingface.co`, so it can neither push to a Space nor download the model.
> Run the steps below from your own machine (or straight in the HF web UI).

## 1. Create the Space

1. Go to <https://huggingface.co/new-space>.
2. **Owner / Space name:** e.g. `your-name/voice-cloning-poc`.
3. **SDK:** Gradio.
4. **Hardware:** `CPU basic` (free) is enough to try it; pick a GPU tier for speed.
5. **Visibility:** Public, or Private if you want it locked down.
6. Click **Create Space**.

## 2. Push the code to the Space

A Space is a git repo on Hugging Face. Push this project's files into it.

```bash
# from a clone of this GitHub repo
git remote add space https://huggingface.co/spaces/<owner>/<space-name>
git push space main
```

When prompted for credentials:
- **Username:** your Hugging Face username
- **Password:** a **write** access token from <https://huggingface.co/settings/tokens>

> Prefer no terminal? In the Space, use **Files → Add file → Upload files** and
> upload `app.py`, `tts_engine.py`, `requirements.txt`, and `README.md`.

## 3. Wait for the build

The Space installs `requirements.txt` (torch + chatterbox-tts — a few minutes)
and then starts `app.py`. The first time you click **Speak**, it downloads the
model weights from Hugging Face (one-time, on the Space).

## 4. Test on your phone

Open the Space URL (`https://huggingface.co/spaces/<owner>/<space-name>`) on your
phone. Because it is HTTPS, the browser lets you record:

1. **Record** ~6–10s of clean speech (or upload a clip).
2. **Type** a sentence.
3. Tap **Speak** and listen.

## Notes

- **Free CPU is slow.** Synthesis on `CPU basic` can take many seconds; upgrade
  the Space hardware (Settings → Hardware) for a snappier demo.
- **Lock it down** by making the Space private, or set a `GRADIO_AUTH=user:pass`
  variable (Settings → Variables and secrets) to password-protect a public Space.
- **`sdk_version`** in the README frontmatter pins the Gradio runtime; bump it if
  you want a newer Gradio.
