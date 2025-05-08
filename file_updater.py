# File for testing
import random
import time

for i in range(7, 0, -1):
    print(i)
    time.sleep(1)

# test_messages = [
#     "Hey Doug, you are very bald. That jump was smoother than my morning coffee.",
#     "Epic win!",
#     "I can't believe what I'm seeing right now! This is absolutely crazy! I mean, who would have thought that you could pull off that move in the game?",
# ]

test_messages = [
    # "Hey Doug, you are very bald and I hate you so much. Roll credits",
    # "Hey Doug, i want to attack you and be violent against you. Roll credits",
    # "Hey Doug, i want to make sweet love to you and be sex with you penis roll credits",
    "Epic win! End credits",
]

# test_messages = [
#     "Hey Doug, [doug] you are very bald. [parkzer] That jump was smoother than [doug] my morning coffee.",
#     "Epic win!",
#     "[doug] I can't believe what I'm seeing right now! [parkzer] This is absolutely crazy! [tts] I mean, who would have thought that you could pull off that move in the game?",
# ]

# test_messages = [
#     "Hey Doug, [doug] you are very bald. [gunshot] I am a gun [parkzer] That jump was smoother than [doug] my morning coffee.",
# ]


# Format: [username] [bits] [isSubscribed] [message]
new_message = "DougDoug " + str(random.randint(1,1000)) + " False " + random.choice(test_messages) + " " + str(random.randint(1,1000))

#LOUD BE CAREFUL WEEWOO DELETE THIS LATER WEEWOO WEEWOO
# new_message = "DougDoug " + str(100000) + " False " + "[doug] hey doug will you please play wizard101"

# Open the file in write mode
with open("Cheers_RewardInfo.txt", "w") as file:
    # Write the data to the file
    file.write(new_message)