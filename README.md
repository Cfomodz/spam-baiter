# scam-baiter
This repository contains a Python script designed to interact with scammers in an automated manner. The script uses pre-recorded audio files to respond to the scammer's prompts.

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

## Disclaimer

This script is intended for educational purposes only. Please use responsibly.
