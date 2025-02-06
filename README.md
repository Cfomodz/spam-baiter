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

## Files in this Repository

- `voice_search_baiter.py`: This Python script drives a back-and-forth with the spammer following their specific script. It uses the PyAudio library to play the audio files and listens for silence to determine when the scammer has finished speaking.

- `requirements.txt`: This file lists the Python dependencies that need to be installed for the script to run.

- Audio Files: The audio files are located in the `scammer_soundboard` directory. They are organized by the character who is speaking (in this case, "Walter Nelson") and further divided into different categories based on the type of response.

## How to Use

1. Clone this repository to your local machine.

2. Install the required Python dependencies by running `pip install -r requirements.txt`.

3. Run the `voice_search_baiter.py` script. The script will start listening for the scammer to speak and will respond with the appropriate pre-recorded audio file when the scammer stops speaking.

Please note that the script is currently set up to use specific input and output devices. You may need to adjust the device indices in the `voice_search_baiter()` function to match your system's configuration.

## Dependencies

- Python
- PyAudio
- numpy

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
