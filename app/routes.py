# app/routes.py
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_socketio import emit
from .socketio_instance import socketio
import random
import os
import socket

main = Blueprint('main', __name__)

choices = []
votes = {}
current_image = None
barcode_dict = {}
available_images = []
used_images = []
current_timer = None
round_number = 1

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

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@main.route('/')
def coordinator():
    return render_template('Coordinator.html')

@main.route('/voting')
def voting():
    global current_image, available_images, used_images
    local_ip = get_local_ip()
    if current_image is None:
        # Initialize images if first time
        if not available_images and not used_images:
            available_images = get_images()

        if not available_images:
            available_images = used_images
            used_images = []

        if available_images:
            current_image = random.choice(available_images)
            available_images.remove(current_image)
            used_images.append(current_image)
        else:
            print("No images available.")
            current_image = None
    return render_template('Voting.html', local_ip=local_ip)

@main.route('/client')
def client():
    local_ip = get_local_ip()
    return render_template('Client.html', local_ip=local_ip)

@main.route('/submit_choices', methods=['POST'])
def submit_choices():
    global choices, votes
    choices = request.json['choices']
    votes = {chr(65 + i): 0 for i in range(len(choices))}  # Use labels as keys
    socketio.emit('update_choices', {'choices': choices})
    return jsonify(success=True)

@main.route('/start_voting', methods=['POST'])
def start_voting():
    global current_timer
    data = request.json
    timer = data.get('timer', 30)
    current_timer = timer

    if not choices:
        return jsonify({"error": "No choices available"}), 400

    print('Starting voting with choices:', choices)
    socketio.emit('voting_started', {
        'choices': choices,
        'image': current_image,
        'timer': current_timer,
        'round': round_number
    })
    return jsonify(success=True)

@main.route('/start_new_round', methods=['POST'])
def start_new_round():
    global choices, votes, current_image, current_timer, round_number, available_images, used_images
    choices = []
    votes = {}
    current_timer = None
    round_number += 1

    # Select a new image
    if not available_images:
        if used_images:
            available_images = used_images
            used_images = []
        else:
            available_images = get_images()

    if available_images:
        current_image = random.choice(available_images)
        available_images.remove(current_image)
        used_images.append(current_image)
    else:
        print("No images available.")
        current_image = None

    socketio.emit('new_round_started', {
        'image': current_image,
        'round': round_number
    })
    return jsonify(success=True)

@socketio.on('vote')
def handle_vote(data):
    global votes
    choice_label = data['choice']
    if choice_label in votes:
        votes[choice_label] += 1
        socketio.emit('vote_update', votes)

@socketio.on('update_choices')
def handle_update_choices(data):
    global choices, votes
    updated_choices = data['choices']
    choices = updated_choices
    votes = {chr(65 + i): 0 for i in range(len(choices))}  # Reset votes with labels
    print('Received updated choices:', choices)
    socketio.emit('update_choices', {'choices': choices})

@socketio.on('request_current_state')
def handle_current_state():
    global choices, current_image, current_timer, round_number, votes
    emit('current_state', {
        'choices': choices,
        'image': current_image,
        'timer': current_timer,
        'round': round_number,
        'votes': votes
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@main.route('/check_barcode', methods=['POST'])
def check_barcode():
    barcode = request.json['barcode']
    if barcode in barcode_dict:
        return jsonify(success=True, text=barcode_dict[barcode])
    return jsonify(success=False)
