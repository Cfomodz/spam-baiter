<div align="center">

# 🎣 Spam Baiter  
![GitHub License](https://img.shields.io/github/license/Cfomodz/spam-baiter)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![GitHub Sponsors](https://img.shields.io/github/sponsors/Cfomodz)
![Discord](https://img.shields.io/discord/425182625032962049)
![GitHub Repo stars](https://img.shields.io/github/stars/cfomodz/spam-baiter?style=flat)

<p align="center"><img width="25%" src="https://github.com/Cfomodz/spam-baiter/assets/31261577/5894d96b-6984-46b1-b6c9-a01bc6f18904"></p>

### Automate interactions with scammers and spammers using Python  

---

🚨 **Why bother talking to scammers/spammers?**  
</div>

What they are doing is illegal, it's wrong, and it hurts real people. This includes both outright scamming such as tech support scams, IRS tax debt scams, and telemarketing practices that violate TCPA including robodialing, pre-recorded messages, non-compliance with the TSR, and just general fraud as is seen in the scammer docs dir of this repo.

A couple of examples of direct scam interventions that illustrate what they intend to do to victims:

https://www.youtube.com/watch?v=tzXRb8PdmJo

https://www.youtube.com/watch?v=FtgynBMUYF4

## What's in this Repository

- `backend/` + `frontend/`: The **Spam Baiter Dashboard** — a FastAPI backend and React frontend for managing calls (mock bridge for now), contacts, a soundboard, and ElevenLabs TTS. This is where active development happens.

- `voice_search_baiter.py` *(legacy)*: The original v0.1 standalone script. It drives a back-and-forth with the spammer following their specific script, using PyAudio to play audio files and listening for silence to determine when the scammer has finished speaking.

- `s3cure_communications.py` *(legacy)*: A standalone generator for challenge-phrase messages to detect compromised text conversations.

- `scammer_soundboard/`: Pre-recorded audio clips, organized by the character who is speaking (currently "Walter Nelson") and further divided into categories based on the type of response. Used by both the legacy script and the dashboard.

- `requirements.txt` *(legacy)*: Dependencies for `voice_search_baiter.py` only. Note: these pins require Python ≤ 3.10; the dashboard backend targets Python 3.12.

## Dashboard Quickstart

Backend (Python 3.11+):

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. Optional configuration goes in a `.env` file at the repo root (see `.env.example`):

- `ELEVENLABS_API_KEY` enables the TTS panel; without it, TTS endpoints return 503 and the rest of the dashboard works normally.
- `PHONE_BRIDGE=mock` is the only working bridge today — real telephony integration is on the roadmap.

Run the backend tests with:

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/
```

## Legacy Script Usage

1. Install the legacy dependencies: `pip install -r requirements.txt` (requires Python ≤ 3.10).

2. Run `voice_search_baiter.py`. The script will start listening for the scammer to speak and will respond with the appropriate pre-recorded audio file when the scammer stops speaking.

Please note that the script is currently set up to use specific input and output devices (indices 5 and 19). You will likely need to adjust the device indices in the `voice_search_baiter()` function to match your system's configuration.

## Roadmap
The script (v0.1) uses pre-recorded audio files to respond to the spammers' prompts.

v0.1.1 Clean things up so they are more easily configurable for a new setup (specifically audio input & output devices + some docs/docstrings)

v0.2 will be implementing a generalized baiter with much more flexibility utilizing Whisper to detect spammers' utterances and pick a response

v0.3 will bring live AI-generated voice responses via ElevenLabs API + Chat GPT 4 via OpenAI API (or Ollama + model of choice).

v0.4 softphone packaged with the repo; probably a customized version of disphone or something 🤷‍♂️ - open to suggestions. Sending commands to a js-based browser softphone API is also an option. This will allow for programmatic dialing (currently you just call it once the call is active)

v0.5 Having the softphone integration will naturally open up the benefits of building out contacts, notes, recordings, categories, and statuses (blocked, OOS, etc) so that you can work more efficiently.

v0.? Twilio integration since that is more accessible than having a SIP trunk.

v0.? TextNow Bot integration - it can text!

v0.? Throughout the versions, we will add more known scam scripts (and associated responses) as supplied by the community.

## How to contribute
This is a free project. Please fork it and play. Open an issue or PR any time. Share what you make.

For less directly scripted conversations, voice line files should still be used to limit the repetitive calling of Elevinlabs API.

If you request voice lines be created for new responses, please ensure they are formatted correctly. For instance, "6130 W N St" becomes "Sixty One Thirty West North Street" and the use of punctuation to convey tone.

## License

[LGPL 2.1](https://choosealicense.com/licenses/lgpl-2.1/)

## Disclaimer

This script is intended for educational purposes only. Please use responsibly.
