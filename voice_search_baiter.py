import time
import random
from pyaudio import PyAudio, paInt16
import numpy as np


scam_baiter = "Walter Nelson"


class FillerAudioManager:
    def __init__(self):
        # Lists of audio clips for each tier
        self.tier1 = [
            "Yes.wav", "Okay.wav", "Sounds good.wav", "Sure thing.wav", "Right.wav",
            "Got it.wav", "Mmhmm.wav", "I understand.wav", "That works for me.wav"
        ]
        self.tier2 = [
            "Let's go with what you think is best.wav", "I trust your judgment on this.wav",
            "Whatever you recommend.wav", "That sounds like a plan.wav",
            "You're the expert, so I'll follow your lead.wav"
        ]
        self.tier3 = [
            "Funny story about business.wav", "Story about my granddaughter.wav",
            "Interesting question thought.wav", "Hold that thought.wav"
        ]
        # Indexes to track the current position in each list
        self.current_index_tier1 = 0
        self.current_index_tier2 = 0
        self.current_index_tier3 = 0

    def get_next_audio(self, tier):
        # Select the list and index based on the tier
        if tier == 1:
            current_list = self.tier1
            index = self.current_index_tier1
        elif tier == 2:
            current_list = self.tier2
            index = self.current_index_tier2
        elif tier == 3:
            current_list = self.tier3
            index = self.current_index_tier3
        else:
            return None

        # Get the next audio file
        audio_file = current_list[index]
        # Increment the index; wrap around if at the end of the list
        if tier == 1:
            self.current_index_tier1 = (index + 1) % len(self.tier1)
        elif tier == 2:
            self.current_index_tier2 = (index + 1) % len(self.tier2)
        elif tier == 3:
            self.current_index_tier3 = (index + 1) % len(self.tier3)

        return f"./scammer_soundboard/{scam_baiter}/early_question_responses/tier_{tier}/{audio_file}"


# Example of how to use this class
audio_manager = FillerAudioManager()


class Section:
    def __init__(self, audio_file, expected_duration):
        self.audio_file = audio_file
        self.expected_duration = expected_duration


sections = [
    Section(f"./scammer_soundboard/{scam_baiter}/Oh, that sounds fantastic! I had no idea this was an option..wav", 37.5),
    Section(f"./scammer_soundboard/{scam_baiter}/Wow, only two I’m lucky you called!.wav", 15),
    Section(f"./scammer_soundboard/{scam_baiter}/Sure thing, what do you need to know.wav", 7.5),
    Section(f"./scammer_soundboard/{scam_baiter}/Yes, that's perfect. That's exactly how it should be..wav", 10),
    Section(f"./scammer_soundboard/{scam_baiter}/Yep, that's me. Ready to make any decisions needed!.wav", 5),
    Section(f"./scammer_soundboard/{scam_baiter}/It's Walter Nelson. N as in Pneumonia..wav", 5),
    Section(f"./scammer_soundboard/{scam_baiter}/Absolutely, that's the best one for customers to reach me at..wav", 10),
    Section(f"./scammer_soundboard/{scam_baiter}/Just city and state.wav", 10),
    Section(f"./scammer_soundboard/{scam_baiter}/1670 Goldcliff Circle.wav", 12.5),
    Section(f"./scammer_soundboard/{scam_baiter}/Sure, it’s walter nelson at gmail.com..wav", 7.5),
    Section(f"./scammer_soundboard/{scam_baiter}/Definitely, that’s amazing to hear. I can’t believe that many searches! Yes, it’s making sense..wav", 30),
    Section(f"./scammer_soundboard/{scam_baiter}/Hmm, not sure what other keywords. whatever you recommend.wav", 15),
    Section(
        f"./scammer_soundboard/{scam_baiter}/Oh yes, I know them. They're the big names around here. I’ve always wanted to get ahead of them somehow..wav",
        25),
    Section(f"./scammer_soundboard/{scam_baiter}/Well, I'd say 10 miles is good. That’s where most of my customers come from anyway..wav", 15),
    Section(
        f"./scammer_soundboard/{scam_baiter}/I see, it’s all about getting in the door, huh Ok then, let's go ahead and get that application in. What do we do next.wav",
        50),
    Section(
        f"./scammer_soundboard/{scam_baiter}/No, I haven't put in any application before. This is the first time I'm hearing about this opportunity. Let's make sure it gets done right!.wav",
        50),
    Section(
        f"./scammer_soundboard/{scam_baiter}/That sounds great! I’m looking forward to seeing how it all comes together. Just let me know when the appointment is scheduled..wav",
        50),
    Section(f"./scammer_soundboard/{scam_baiter}/Oh, that's wonderful news! And the price is really reasonable, especially with the discount.wav", 50),
    Section(f"./scammer_soundboard/{scam_baiter}/That's a great price! And no contract Even better..wav", 10)
]

current_index = 0
consecutive_early_calls = 0
last_call_time = time.time()


def play_next(output_stream):
    global current_index, last_call_time, consecutive_early_calls
    now = time.time()
    print(f"Last call time (in): {last_call_time}")

    if current_index < len(sections):
        section = sections[current_index]
        time_since_last_call = now - last_call_time
        min_time_needed = section.expected_duration * 0.75

        if time_since_last_call >= min_time_needed:
            # If enough time has passed, play the next planned audio
            respond_to_scammer(section.audio_file, output_stream)
            current_index += 1
            consecutive_early_calls = max(0, consecutive_early_calls - 1)  # Decrement early calls, but never below 0
        else:
            # Not enough time has passed, indicating a potentially off-script question
            consecutive_early_calls += 1
            current_tier = min(consecutive_early_calls, 3)  # Cap the tier at 3

            # Play a filler from the appropriate tier
            filler_audio = audio_manager.get_next_audio(current_tier)
            respond_to_scammer(filler_audio, output_stream)

    else:
        print("End of script reached")
        return 0

    last_call_time = now
    print(f"Last call time (out): {last_call_time}")
    return 1


def listen_to_output_device(input_stream, p):
    print("Listening...")
    silence_duration = 0  # To keep track of the silence duration
    frames = []
    # while relatively silent (low input), clear the frames list and continue recording
    while True:
        data = input_stream.read(1024)

        ioriginal = np.frombuffer(data, dtype=np.int16)
        if random.randint(0, 100) == 0:
            print(max(ioriginal))
        if max(ioriginal) < 1150:
            frames = []
        else:
            print(max(ioriginal))
            frames.append(data)
            print("Scammer started speaking, recording...")
            break
    # record until the line goes quiet (they are done speaking)
    while True:
        data = input_stream.read(1024)
        ioriginal = np.frombuffer(data, dtype=np.int16)
        if random.randint(0, 100) == 0:
            print(max(ioriginal))
        if max(ioriginal) < 500:  # you can adjust this if the scammer isn't using a background noise track
            silence_start_time = time.time()  # current time

            # Check next few sets of samples to confirm if it's silence
            for _ in range(int(1.0 * 44100 / 1024)):  # approx. 1.0 sec of samples
                data = input_stream.read(1024)
                ioriginal = np.frombuffer(data, dtype=np.int16)

                if max(ioriginal) < 500:  # similarly can be adjusted per background level of scam call center
                    silence_duration = time.time() - silence_start_time  # duration of silence so far
                else:
                    silence_duration = 0  # reset silence duration if sound is detected

            if silence_duration > 1.0:  # if silence lasts more than 1.0 sec, break
                print(max(ioriginal))
                print("Scammer stopped speaking, finishing recording...")
                break
        else:
            silence_duration = 0  # reset silence duration
            frames.append(data)
    return frames


def respond_to_scammer(response_audio, output_stream):
    print(f"Playing response...{response_audio}")
    with open(response_audio, 'rb') as f:
        response_audio = f.read()
    output_stream.write(response_audio)


def voice_search_baiter():
    p = PyAudio()
    device_info = p.get_device_info_by_index(5)
    print("Device Info: ", device_info)

    device_id = device_info['index']
    device_name = device_info['name']

    print("Device ID: ", device_id)
    print("Device Name: ", device_name)
    input_stream = p.open(format=paInt16,
                          channels=1,
                          rate=44100,
                          input=True,
                          frames_per_buffer=1024,
                          input_device_index=device_id)

    # for i in range(p.get_device_count()):
    #     print(p.get_device_info_by_index(i))
    output_device_info = p.get_device_info_by_index(19)
    print("Output Device Info: ", output_device_info)

    output_device_id = output_device_info['index']
    output_device_name = output_device_info['name']

    print("Output Device ID: ", output_device_id)
    print("Output Device Name: ", output_device_name)

    output_stream = p.open(format=paInt16,
                           channels=1,
                           rate=44100,
                           output=True,
                           frames_per_buffer=1024,
                           output_device_index=output_device_id,
                           )
    while True:
        # wait for scammer to stop speaking
        listen_to_output_device(input_stream, p)

        response = play_next(output_stream)
        if not response:
            print("End of script reached")
            break

    # Close the PyAudio instance
    input_stream.stop_stream()
    input_stream.close()
    output_stream.stop_stream()
    output_stream.close()
    p.terminate()


if __name__ == "__main__":
    print("Starting the voice search baiter...")
    voice_search_baiter()
