# app/routes.py
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_socketio import emit
from .socketio_instance import socketio  # Import the shared socketio instance
import random
import socket
import os

main = Blueprint('main', __name__)

choices = []
votes = {}
current_image = None
barcode_dict = {}

# Initialize lists to track images
available_images = []
used_images = []

def load_barcode_data():
    global barcode_dict
    try:
        with open('app/Data.txt', 'r', encoding='utf-8') as file:
            for line in file:
                barcode, text = line.strip().split(' ', 1)
                barcode_dict[barcode] = text
    except Exception as e:
        print(f"Error loading barcode data: {str(e)}")

load_barcode_data()

def get_images():
    images_dir = os.path.join(current_app.root_path, 'static', 'images')
    images = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return images


@main.route('/')
def coordinator():
    return render_template('Coordinator.html')

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public IP, doesn't have to be reachable
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@main.route('/voting')
def voting():
    local_ip = get_local_ip()
    return render_template('Voting.html', local_ip=local_ip)

@main.route('/client')
def client():
    local_ip = get_local_ip()
    return render_template('Client.html', local_ip=local_ip)

@main.route('/submit_choices', methods=['POST'])
def submit_choices():
    global choices, votes
    choices = request.json['choices']
    votes = {choice: 0 for choice in choices}
    # Emit updated choices to all connected clients
    socketio.emit('voting_started', {'choices': choices})
    return jsonify(success=True)

@main.route('/start_voting', methods=['POST'])
def start_voting():
    global current_image, choices, available_images, used_images
    if not choices:
        return jsonify({"error": "No choices available"}), 400

    # Initialize images if first time
    if not available_images and not used_images:
        available_images = get_images()

    # Reset images if all have been used
    if not available_images:
        available_images = used_images
        used_images = []

    # Select a random image and update lists
    if available_images:
        current_image = random.choice(available_images)
        available_images.remove(current_image)
        used_images.append(current_image)
    else:
        return jsonify({"error": "No images available"}), 400

    print('Starting voting with choices:', choices)
    socketio.emit('voting_started', {'choices': choices, 'image': current_image})
    return jsonify(success=True)

@main.route('/start_new_round', methods=['POST'])
def start_new_round():
    global choices, votes, current_image
    choices = []
    votes = {}
    current_image = None
    socketio.emit('new_round_started')
    return jsonify(success=True)

@socketio.on('vote')
def handle_vote(data):
    global votes
    choice = data['choice']
    if choice in votes:
        votes[choice] += 1
        # Emit updated vote counts to all connected clients
        socketio.emit('vote_update', votes)

@socketio.on('update_choices')
def handle_update_choices(updated_choices):
    global choices
    choices = updated_choices
    print('Received updated choices:', choices)
    # Emit updated choices to all connected clients
    socketio.emit('update_choices', choices)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@main.route('/check_barcode', methods=['POST'])
def check_barcode():
    barcode = request.json['barcode']
    if barcode in barcode_dict:
        return jsonify(success=True, text=barcode_dict[barcode])
    return jsonify(success=False)
