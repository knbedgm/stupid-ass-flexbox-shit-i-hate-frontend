from twitchio.ext import commands
from twitchio import *
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
import threading
import time
import os
import asyncio
import unicodedata
from pydub import AudioSegment
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dd_openai_chat import OpenAiManager
from dd_azure_text_to_speech import AzureTTSManager
from dd_obs_websockets import OBSWebsocketsManager
from dd_eleven_labs import ElevenLabsManager
from dd_audio_player import AudioManager
from dd_amazon_polly import PollyManager
import keyboard
import html
import logging
from rich import print

CHEERS_TXT_FILE = r"E:\Dropbox\Livestream Assets\Web Apps\Cheers - Custom TTS\Cheers_RewardInfo.txt"
QUEUE_COUNT_TXT_FILE = r"E:\Dropbox\Livestream Assets\Web Apps\Cheers - Custom TTS\Cheers_QueueCount.txt"
STREAMERBOT_TRIGGER_FILE = r"E:\Dropbox\Livestream Assets\Web Apps\Cheers - Custom TTS\Streamerbot_Trigger.txt"
SOCIAL_CREDIT_FILE = r"E:\Dropbox\Livestream Assets\Web Apps\Cheers - Social Credit TTS\SOCIAL_CREDIT.txt"

socketio = SocketIO
app = Flask(__name__)
app.config['SERVER_NAME'] = "127.0.0.1:5252"
socketio = SocketIO(app, async_mode="threading")
log = logging.getLogger('werkzeug') # Sets flask app to only print error messages, rather than all info logs
log.setLevel(logging.ERROR)
 
alerts_paused = False
alerts_muted = False
pause_lock = threading.Lock()
mute_lock = threading.Lock()

@app.route("/")
def home():
    return render_template('index.html')

@socketio.event
def connect():
    print("[italic green]~~CONNECTED!~~\nTTS... may begin.")

# Updates the trigger txt file to make Streamerbot unpause cheers queue
def UpdateTriggerTxt():
    # Open file and append '1' to trigger file change event
    with open(STREAMERBOT_TRIGGER_FILE, "a") as f:
        f.write("1")

who_has_voted = set()
listening_to_chat = False
points_scored = 0

class ChatBot(commands.Bot):
    def __init__(self):
        #connects to twitch channel
        super().__init__(token=os.getenv('TWITCH_ACCESS_TOKEN'), prefix='?', initial_channels=['dougdoug'])
        self.current_user_1 = "dougdoug"
        self.obswebsocket_manager = OBSWebsocketsManager()
    
    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        await self.process_message(message)

    async def process_message(self, message: Message):
        global points_scored, who_has_voted
        # print("We got a message from this person: " + message.author.name)
        # print("Their message was " + message.content)
        if listening_to_chat:
            # AT THIS POINT WE'VE GOT A CHAT MESSAGE
            # Check if message contains "+2" string
            if "+2" in message.content and message.author.name not in who_has_voted:
                print(f"Found +2 in message from {message.author.name}: {message.content}")
                points_scored += 2
                who_has_voted.add(message.author.name)
                if message.author.name == "dougdoug":
                    points_scored += 18
            # Check if message contains "-2" string
            if "-2" in message.content and message.author.name not in who_has_voted:
                print(f"Found -2 in message from {message.author.name}: {message.content}")
                points_scored -= 2
                who_has_voted.add(message.author.name)
                if message.author.name == "dougdoug":
                    points_scored -= 18
            if points_scored >= 0:
                self.obswebsocket_manager.change_text_color("??? Left Description ???", "#00FF00")
            else:
                self.obswebsocket_manager.change_text_color("??? Left Description ???", "#FF0000")
            self.obswebsocket_manager.set_text("??? Left Description ???", f"SCORE: {points_scored}")


# No longer used, we use a trigger txt file instead
def UnpauseHotKey():
    # Press Streamerbot hotkey to make it unpause the Cheers queue
    # NOTE: My HoldKey() functions don't seem to trigger Streamerbot hotkey. Just use keyboard module instead.
    # NOTE: Ctrl doesn't seem to register on Streamerbot. Just use Shift or Alt as modifiers instead.
    print("pressing hotkey")
    keyboard.press("left shift")
    keyboard.press("left alt")
    keyboard.press("[")
    time.sleep(0.1)
    keyboard.release("left shift")
    keyboard.release("left alt")
    keyboard.release("[")

# No longer used, we use a trigger txt file instead
def PauseHotKey():
    # Press Streamerbot hotkey to make it unpause the Cheers queue
    # NOTE: My HoldKey() functions don't seem to trigger Streamerbot hotkey. Just use keyboard module instead.
    # NOTE: Ctrl doesn't seem to register on Streamerbot. Just use Shift or Alt as modifiers instead.
    print("pressing hotkey")
    keyboard.press("left shift")
    keyboard.press("left alt")
    keyboard.press("]")
    time.sleep(0.1)
    keyboard.release("left shift")
    keyboard.release("left alt")
    keyboard.release("]")

# Class that listens for changes in a specific file
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, input_queue, file_to_watch):
        self.input_queue = input_queue
        self.file_to_watch = file_to_watch
        self.previous_data = None

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.file_to_watch):
            with open(self.file_to_watch, 'r', encoding='utf-8') as f:
                new_input = f.read().strip()
                new_input = unicodedata.normalize('NFKC', new_input) # Normalize Unicode characters
                new_input = new_input.replace('\\', '')
                # Check that the new data isn't empty, and that it is actually different
                if new_input and new_input != self.previous_data:
                    self.previous_data = new_input
                    self.input_queue.put(new_input)

# Listens to hotkey presses from doug
class KeyPressBot():
    def __init__(self):
        self.obswebsockets_manager = OBSWebsocketsManager()
    def run(self):
        global alerts_paused, alerts_muted
        while True:
            # Pause alerts
            if keyboard.is_pressed('left alt') and keyboard.is_pressed('left shift') and keyboard.is_pressed(']'):
                print(f"[italic red]Pausing alerts - {time.time()}")
                with pause_lock:
                    alerts_paused = True
                self.obswebsockets_manager.set_source_visibility("/// TTS Queue", "TTS Queue Icon - Paused", True)
                time.sleep(0.5) # Quick pause to prevent this from firing multiple times in a row
            # Unpause alerts
            if keyboard.is_pressed('left alt') and keyboard.is_pressed('left shift') and keyboard.is_pressed('['):
                print(f"[italic green]Unpausing alerts - {time.time()}")
                with pause_lock:
                    alerts_paused = False
                self.obswebsockets_manager.set_source_visibility("/// TTS Queue", "TTS Queue Icon - Paused", False)
                time.sleep(0.5) # Quick pause to prevent this from firing multiple times in a row
            # Mute alerts
            if keyboard.is_pressed('left alt') and keyboard.is_pressed('left shift') and keyboard.is_pressed('='):
                print(f"[italic red]Muting alerts - {time.time()}")
                with mute_lock:
                    alerts_muted = True
                self.obswebsockets_manager.set_source_visibility("/// TTS Queue", "TTS Queue Icon - Muted", True)
                time.sleep(0.5) # Quick pause to prevent this from firing multiple times in a row
            # Umute alerts
            if keyboard.is_pressed('left alt') and keyboard.is_pressed('left shift') and keyboard.is_pressed('-'):
                print(f"[italic green]Unmuting alerts - {time.time()}")
                with mute_lock:
                    alerts_muted = False
                self.obswebsockets_manager.set_source_visibility("/// TTS Queue", "TTS Queue Icon - Muted", False)
                time.sleep(0.5) # Quick pause to prevent this from firing multiple times in a row
            # Exit program
            if keyboard.is_pressed('left alt') and keyboard.is_pressed('left shift') and keyboard.is_pressed('q'):
                print(f"[italic red]Exiting program - {time.time()}")
                os._exit(0)  # Force exits the program and closes the terminal
            time.sleep(0.05) # Add this to reduce CPU usage

# Processes any updates to the QueueCount txt file
class QueueCountBot():
    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.obswebsockets_manager = OBSWebsocketsManager()
        print("Queue Count Bot initialized!")

    def run(self):
        while True:
            if self.input_queue.empty(): # Wait until we see a new message
                time.sleep(0.1) # Add this to reduce CPU usage
                continue

            new_input = self.input_queue.get()
            print(f"[italic green] We received a new queue count: {new_input}")
            self.obswebsockets_manager.set_text("??? TTS Queue Count ???", new_input)
            ###########################

class TTSBot():
    voice_name = "en-US-DavisNeural"
    voice_style = "shouting"

    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.openai_manager = OpenAiManager()
        self.azuretts_manager = AzureTTSManager()
        self.obswebsockets_manager = OBSWebsocketsManager()
        self.elevenlabs_manager = ElevenLabsManager()
        self.audio_manager = AudioManager()
        self.pollytts_manager = PollyManager()
        print("TTSBot initialized!")

    # Turns donation text into audio files and len
    def process_tts(self, text, bits):

        tts_file = self.pollytts_manager.text_to_audio(text)
        
        # Adjust volume of the audio file
        # In general, we reduce the TTS volume by about 4db to hit a good level
        audio = AudioSegment.from_file(tts_file)
        adjusted_audio = audio - 10  # Change volume by X dB
        adjusted_audio.export(tts_file, format="mp3", bitrate="320k")

        return tts_file

    def run(self):
        global alerts_paused, alerts_muted
        while True:
            # Wait until we see a new message and alerts are unpaused
            if self.input_queue.empty() or alerts_paused:
                time.sleep(0.1) # Add this to reduce CPU usage
                continue

            new_input = self.input_queue.get()
            print(f"[italic green] We received a cheer: {new_input}\n")
            # Format: [username] [bits] [isSubscribed] [message]
            try:
                input_list = new_input.split()
                username = input_list[0]
                bits = input_list[1]
                is_subscribed = input_list[2]
                if len(input_list) > 3:
                    donation_msg = ' '.join(input_list[3:])
                    donation_msg = html.escape(donation_msg, quote=False)
                    donation_msg = donation_msg.replace("â", "")
                else:
                    donation_msg = "3 billion bits, zoop zoop"
            except:
                print(f"[red]SOMETHING HAPPENED WITH THIS MESSAGE: {input_list}")
                donation_msg = "I'm really sorry something in my code broke and so I scammed you but here's a free message from me to make up for it"

            # We check upfront whether alerts are currently muted, so that this specific TTS will stay "muted" even if Doug changes the overall mute state
            with mute_lock:
                muted = alerts_muted

            ##############################################################
            #               Turn message into audio                      #
            ##############################################################
            if not muted:
                tts_file = self.process_tts(donation_msg, bits)
            ##############################################################

            # Display the TTS message
            socketio.emit('new_message', {'message': f"{donation_msg}", 'username': f"{username}", 'bits': f"{bits}"})

            print("[italic red]this shit bussin frfr")

            # Display the TTS pepper character
            self.obswebsockets_manager.set_source_visibility("/// Custom TTS", "TTS - Wario Pepper", True)

            # If the alerts are muted, we wait for 5 seconds.
            # Otherwise, we play the audio
            if muted:
                time.sleep(5)
            else:
                time.sleep(0.5) # Wait a half second for the images to fade in before audio plays
                self.audio_manager.play_audio(tts_file, True, True, True)

            # Let text sit on screen for a few seconds after TTS is done
            time.sleep(1)

            # Tell client to clear the text
            socketio.emit('clear_message', {})

            # Hide the TTS pepper character
            self.obswebsockets_manager.set_source_visibility("/// Custom TTS", "TTS - Wario Pepper", False)
            

            # THIS IS THE POINT THAT THE TTS IS DONE:

            # (1) - Play audio that we're starting vote
            self.audio_manager.play_audio("BeginEvaluation.mp3", True, False, True)

            # (2) - Activate a thread that reads chat messages and collects a score
            global points_scored, listening_to_chat
            points_scored = 0
            listening_to_chat = True
            self.obswebsockets_manager.set_source_visibility("*** Mid Monitor", "??? Left Description ???", True)

            # (3) - Wait 20 seconds
            time.sleep(20)
            listening_to_chat = False

            # (4) - Play audio, announce final score
            if points_scored >= 0:
                self.audio_manager.play_audio("SocialCreditImproved.mp3", True, False, True)
            elif points_scored < 0:
                self.audio_manager.play_audio("SocialCreditDeducted.mp3", True, False, True)
            self.obswebsockets_manager.set_source_visibility("*** Mid Monitor", "??? Left Description ???", False)

            # (5) - Write updated final scores to a txt file
            user_scores = {}
            try:
                with open(SOCIAL_CREDIT_FILE, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            user = parts[0]
                            score = int(parts[1])
                            user_scores[user] = score
            except FileNotFoundError:
                pass  # File doesn't exist yet, will create it
            
            # Update or add the current user's score
            if username in user_scores:
                user_scores[username] += points_scored
            else:
                user_scores[username] = points_scored
            
            # Write all scores back to the file
            with open(SOCIAL_CREDIT_FILE, "w") as f:
                for user, score in user_scores.items():
                    f.write(f"{user} {score}\n")

            # If the alerts are paused, the function ends here.
            # If they aren't paused, then we tell Streamerbot to unpause the queue and send us another alert.
            with pause_lock:
                if not alerts_paused:
                    # Delay before starting the next alert
                    time.sleep(3) 
                    # Update the trigger txt file to make Streamerbot unpause cheers queue, this kicks off the next cheer
                    UpdateTriggerTxt()
            
            ###########################

def startTwitchBot():
    global twitchbot
    asyncio.set_event_loop(asyncio.new_event_loop()) # Create and set the event loop for this thread
    twitchbot = ChatBot()
    twitchbot.run() # Kicks off the Twitchio connection

def start_bot(bot):
    bot.run()

if __name__ == '__main__':
    # Main bot that listens to RewardInfo.txt file and processes new cheers info
    cheers_input_queue = Queue()
    tts_bot = TTSBot(cheers_input_queue)
    cheers_observer = Observer()
    cheers_event_handler = FileChangeHandler(cheers_input_queue, CHEERS_TXT_FILE)
    cheers_observer.schedule(cheers_event_handler, path=os.path.dirname(os.path.abspath(CHEERS_TXT_FILE)), recursive=False)
    cheers_observer.start()
    tts_bot_thread = threading.Thread(target=start_bot, args=(tts_bot,))
    tts_bot_thread.start()

    # Bot that listens for changes to the QueueCount.txt file
    counter_input_queue = Queue()
    queue_count_bot = QueueCountBot(counter_input_queue)
    counter_observer = Observer()
    counter_event_handler = FileChangeHandler(counter_input_queue, QUEUE_COUNT_TXT_FILE)
    counter_observer.schedule(counter_event_handler, path=os.path.dirname(os.path.abspath(QUEUE_COUNT_TXT_FILE)), recursive=False)
    counter_observer.start()
    queue_count_bot_thread = threading.Thread(target=start_bot, args=(queue_count_bot,))
    queue_count_bot_thread.start()

    # Thread that listens for hotkey presses from Doug
    keypress_bot = KeyPressBot()
    keypress_bot_thread = threading.Thread(target=start_bot, args=(keypress_bot,))
    keypress_bot_thread.start()

    chat_bot_thread = threading.Thread(target=startTwitchBot)
    chat_bot_thread.start()
    
    socketio.run(app)

    cheers_observer.stop()
    counter_observer.stop()
    cheers_observer.join()
    counter_observer.join()
    tts_bot_thread.join()
    queue_count_bot_thread.join()
    keypress_bot_thread.join()
