from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit
from . import socketio
import random
import socket
import requests
import os

main = Blueprint('main', __name__)

choices = []
votes = {}
current_image = None
barcode_dict = {}

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

@main.route('/')
def coordinator():
    return render_template('coordinator.html')

@main.route('/voting')
def voting():
    return render_template('voting.html')

@main.route('/client')
def client():
    return render_template('client.html')

@main.route('/submit_choices', methods=['POST'])
def submit_choices():
    global choices, votes
    choices = request.json['choices']
    votes = {choice: 0 for choice in choices}
    return jsonify(success=True)

@main.route('/start_voting', methods=['POST'])
def start_voting():
    global current_image, choices
    images = get_images()
    
    if not choices:
        return jsonify({"error": "No choices available"}), 400
    
    if images:
        current_image = random.choice(images)
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

@main.route('/get_images', methods=['GET'])
def get_available_images():
    images_dir = os.path.join('app', 'static', 'images')
    try:
        images = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        return jsonify(images=images)
    except Exception as e:
        return jsonify(images=[]), 500

def get_available_images():
    images_dir = os.path.join('app', 'static', 'images')
    return [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

@socketio.on('vote')
def handle_vote(data):
    choice = data['choice']
    if choice in votes:
        votes[choice] += 1
        emit('vote_update', votes, broadcast=True)

@main.route('/check_barcode', methods=['POST'])
def check_barcode():
    barcode = request.json['barcode']
    if barcode in barcode_dict:
        return jsonify(success=True, text=barcode_dict[barcode])
    return jsonify(success=False)

@main.route('/get_images', methods=['GET'])
def get_images():
    image_dir = os.path.join(app.static_folder, 'images')
    images = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return jsonify(images)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception:
        return None  # Return None if unable to get public IP

@socketio.on('start_voting')
def handle_start_voting():
    choices = ['Choice 1', 'Choice 2', 'Choice 3']  # Replace with your actual choices
    socketio.emit('voting_started', {'choices': choices})
