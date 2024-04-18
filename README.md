# spam-baiter
This repository contains a Python script illustrating the potential to interact with scammers and spammers in an automated manner.

## Files in this Repository

- `voice_search_baiter.py`: This is the main Python script that handles the interaction with the scammer. It uses the PyAudio library to play the audio files and listens for silence to determine when the scammer has finished speaking.

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

## Disclaimer

This script is intended for educational purposes only. Please use responsibly.
