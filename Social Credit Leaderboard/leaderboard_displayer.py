from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import logging
from rich import print

SOCIAL_CREDIT_FILE = r"SOCIAL_CREDIT.txt"

socketio = SocketIO
app = Flask(__name__)
app.config['SERVER_NAME'] = "127.0.0.1:5555"
socketio = SocketIO(app, async_mode="threading")
log = logging.getLogger('werkzeug') # Sets flask app to only print error messages, rather than all info logs
log.setLevel(logging.ERROR)
 
@app.route("/")
def home():
    return render_template('index.html') #redirects to index.html in templates folder

@socketio.event
def connect(): #when socket connects, send data confirming connection
    print("[green]SOCIAL CREDIT LEADERBOARD")

class LeaderboardBot():
    def __init__(self):
        print("Leaderboard bot running!")

    def run(self):
        while True:
            print("...Checking leaderboard...")
            # Get leaderboard
            try:
                with open(SOCIAL_CREDIT_FILE, 'r') as file:
                    # Read all lines and parse scores
                    scores = []
                    for line in file:
                        if line.strip():  # Skip empty lines
                            username, score = line.strip().split()
                            scores.append((username, int(score)))
                    
                    # Sort scores in descending order
                    scores.sort(key=lambda x: x[1], reverse=True)
                    
                    # Get top 5 and bottom 5
                    top_5 = [f"{username} {score}" for username, score in scores[:5]]
                    bottom_5 = [f"{username} {score}" for username, score in scores[-5:]]
                    
                    # Emit the leaderboard data
                    socketio.emit('top_5', {'text': top_5})
                    socketio.emit('bottom_5', {'text': bottom_5})
                    
            except FileNotFoundError:
                print("[red]Social credit file not found!")
            except Exception as e:
                print(f"[red]Error processing social credit file: {str(e)}")

            # Sleep for a short duration to prevent excessive file reading
            socketio.sleep(3)  # Update every 5 seconds

            # IF NOT, WAIT AROUND AGAIN


def start_bot(bot):
    bot.run()

if __name__=='__main__':

    leaderboard_bot = LeaderboardBot()
    leaderboard_bot_thread = threading.Thread(target=start_bot, args=(leaderboard_bot,))
    leaderboard_bot_thread.start()
    
    socketio.run(app)
