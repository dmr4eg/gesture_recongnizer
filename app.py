import os
import signal
import sys
import threading
from flask import Flask, request, jsonify
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from gestures.gesture_callback_manager import GestureCallbackManager, gesture_callback
from gestures.gesture_operating import GestureRecognitionHub

# Flask app setup
app = Flask(__name__)

# Spotify authentication setup
sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-modify-playback-state,user-read-playback-state"
))

# Gesture manager setup
manager = GestureCallbackManager(gesture_callback, sp, delay=2)

@app.route('/gesture', methods=['POST'])
def gesture():
    """
    Endpoint to handle gesture recognition requests.
    
    :return: JSON response with status and recognized gesture name.
    """
    data = request.get_json()
    gesture_name = data.get('gesture_name')
    manager.call_callback_based_on_gesture(gesture_name)
    return jsonify({"status": "success", "gesture": gesture_name})

# Gesture recognition hub class
class App:
    def __init__(self):
        """
        Initialize the GestureRecognitionHub and set up signal handling.
        """
        self.app = GestureRecognitionHub()
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        """
        Handle SIGINT signal for graceful shutdown.
        """
        print('SIGINT received, shutting down...')
        self.app.destroy()
        sys.exit(0)

    def run_gesture_recognition(self):
        """
        Run the gesture recognition application.
        """
        try:
            self.app.start_recognition()
            self.app.mainloop()
        except KeyboardInterrupt:
            self.app.destroy()

# Run Flask app in a separate thread
def run_flask_app():
    """
    Function to run the Flask app in a separate thread.
    """
    app.run(host='0.0.0.0', port=5000)

# Main entry point
if __name__ == '__main__':
    # Start the Flask app thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Start the gesture recognition
    gesture_app = App()
    gesture_app.run_gesture_recognition()
