import random

challenge_phrases = [
    "The sky is blue",
    "The cat is on the roof",
    "The sun is shining",
    "The river is flowing",
    "The stars are twinkling",
    "The ocean is vast",
    "The mountains are tall",
    "The forest is dense",
    "The desert is dry",
    "The sky is clear",
    "The moon is bright",
    "The wind is howling",
    "The rain is falling",
    "The snow is drifting",
    "The clouds are fluffy",
    "The birds are singing",
    "The bees are buzzing",
    "The flowers are blooming",
    "The trees are swaying",
    "The leaves are rustling",
    "The waves are crashing",
    "The tide is rising",
    "The sand is shifting",
    "The rocks are solid",
    "The grass is dewy",
    "The fields are golden",
    "The hills are rolling",
    "The valleys are peaceful",
    "The cliffs are steep",
    "The caves are dark",
    "The stars are distant",
    "The planets are orbiting",
    "The galaxy is infinite",
    "The universe is expanding",
    "The sun is setting",
    "The moon is rising",
    "The night is silent",
    "The day is bright",
    "The dawn is breaking",
    "The dusk is falling",
    "The horizon is endless",
    "The rainbow is colorful",
    "The storm is brewing",
    "The lightning is flashing",
    "The thunder is rumbling",
    "The fog is thick",
    "The mist is light",
    "The frost is forming",
    "The ice is cracking",
    "The fire is burning"
]

challenge_responses = [
    "And the grass is green",
    "And the dog is in the yard",
    "And the moon is glowing",
    "And the wind is blowing",
    "And the planets are orbiting",
    "And the waves are crashing",
    "And the valleys are deep",
    "And the trees are tall",
    "And the sand is hot",
    "And the clouds are white",
    "And the stars are distant",
    "And the rain is soothing",
    "And the snow is cold",
    "And the clouds are gray",
    "And the birds are chirping",
    "And the flowers are fragrant",
    "And the trees are strong",
    "And the leaves are colorful",
    "And the waves are powerful",
    "And the tide is receding",
    "And the sand is warm",
    "And the rocks are ancient",
    "And the grass is soft",
    "And the fields are endless",
    "And the hills are serene",
    "And the valleys are lush",
    "And the cliffs are majestic",
    "And the caves are mysterious",
    "And the stars are infinite",
    "And the planets are aligned",
    "And the galaxy is vast",
    "And the universe is mysterious",
    "And the sun is warm",
    "And the moon is serene",
    "And the night is calm",
    "And the day is cheerful",
    "And the dawn is hopeful",
    "And the dusk is tranquil",
    "And the horizon is vast",
    "And the rainbow is magical",
    "And the storm is fierce",
    "And the lightning is bright",
    "And the thunder is loud",
    "And the fog is eerie",
    "And the mist is refreshing",
    "And the frost is delicate",
    "And the ice is slippery",
    "And the fire is warm"
]

# List of varied phrasings for the challenge requests
initial_phrases = [
    "Before we proceed, I need to make sure your account hasn’t been compromised. Could you please include a challenge phrase and challenge response with each message? For example, you could say ‘{challenge_phrase}’ and I would respond ‘{challenge_response}.’ This way, I’ll know it’s really you. Thanks!",
    "To ensure your account hasn’t been compromised, I’d like to set up a challenge phrase and response system. For this message, your challenge phrase is ‘{challenge_phrase}.’ Please include that in your next message, and I’ll respond with ‘{challenge_response}.’ Thanks for understanding!"
]

follow_up_phrases = [
    "Your challenge phrase was ‘{previous_challenge_phrase},’ so my challenge response is ‘{previous_challenge_response}.’ Now, for your next message, please include the challenge phrase ‘{challenge_phrase}.’ This is just to make sure your account hasn’t been compromised. Thanks!",
    "Your challenge phrase was ‘{previous_challenge_phrase},’ so my challenge response is ‘{previous_challenge_response}.’ For security purposes, your challenge phrase for this message is ‘{challenge_phrase}.’ Please include that in your next message, and I’ll respond with ‘{challenge_response}.’ Thanks!",
    "Your challenge phrase was ‘{previous_challenge_phrase},’ so my challenge response is ‘{previous_challenge_response}.’ To verify your identity, your challenge phrase for this message is ‘{challenge_phrase}.’ Please include that in your next message, and I’ll respond with ‘{challenge_response}.’ This is just to confirm it’s really you. Thanks!",
    "Your challenge phrase was ‘{previous_challenge_phrase},’ so my challenge response is ‘{previous_challenge_response}.’ Just a reminder, your challenge phrase for this message is ‘{challenge_phrase}.’ Please include that in your next message, and I’ll respond with ‘{challenge_response}.’ This is just to ensure your account hasn’t been compromised. Thanks!",
    "Your challenge phrase was ‘{previous_challenge_phrase},’ so my challenge response is ‘{previous_challenge_response}.’ For added security, your challenge phrase for this message is ‘{challenge_phrase}.’ Please include that in your next message, and I’ll respond with ‘{challenge_response}.’ This is just to confirm it’s really you. Thanks!"
]

# Function to generate challenge messages
def generate_challenge_message(step, previous_challenge_phrase=None, previous_challenge_response=None):
    if step == 0:
        # Initial message
        phrase = random.choice(initial_phrases)
    else:
        # Follow-up messages
        phrase = random.choice(follow_up_phrases)
    
    # Select a challenge phrase and response
    index = step % len(challenge_phrases)
    challenge_phrase = challenge_phrases[index]
    challenge_response = challenge_responses[index]
    
    # Format the message
    if step == 0:
        message = phrase.format(challenge_phrase=challenge_phrase, challenge_response=challenge_response)
    else:
        message = phrase.format(
            previous_challenge_phrase=previous_challenge_phrase,
            previous_challenge_response=previous_challenge_response,
            challenge_phrase=challenge_phrase,
            challenge_response=challenge_response
        )
    
    return message, challenge_phrase, challenge_response

# Example usage
previous_challenge_phrase = None
previous_challenge_response = None

for step in range(20):  # Generates 20 messages as an example
    print(f"Step {step + 1}:")
    message, previous_challenge_phrase, previous_challenge_response = generate_challenge_message(
        step, previous_challenge_phrase, previous_challenge_response
    )
    print(message)
    print()