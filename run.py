# run.py
from app import create_app
from app.socketio_instance import socketio
import webbrowser
import threading
import time

app = create_app()

def open_browser():
    time.sleep(1)
    webbrowser.open('http://localhost:5000/')
    webbrowser.open('http://localhost:5000/voting')

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
