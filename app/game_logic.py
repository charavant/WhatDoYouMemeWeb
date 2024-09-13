import random
import os
from collections import defaultdict

class GameManager:
    def __init__(self, image_folder='app/static/images', response_file='data/responses.txt'):
        self.image_folder = image_folder
        self.response_file = response_file
        self.images = self.load_images()
        self.responses = self.load_responses()
        self.current_image = None
        self.current_responses = []
        self.votes = defaultdict(int)
        self.players = set()
        self.round = 0
        self.game_active = False

    def load_images(self):
        return [img for img in os.listdir(self.image_folder) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    def load_responses(self):
        responses = {}
        with open(self.response_file, 'r') as f:
            for line in f:
                barcode, text = line.strip().split(' ', 1)
                responses[barcode] = text
        return responses

    def start_game(self):
        self.game_active = True
        self.round = 0
        self.next_round()

    def next_round(self):
        if not self.images:
            self.end_game()
            return False
        self.round += 1
        self.current_image = random.choice(self.images)
        self.images.remove(self.current_image)
        self.current_responses = []
        self.votes = defaultdict(int)
        return True

    def add_player(self, player_id):
        self.players.add(player_id)

    def remove_player(self, player_id):
        self.players.remove(player_id)

    def add_response(self, player_id, response):
        if response in self.responses:
            text = self.responses[response]
        else:
            text = response
        self.current_responses.append((player_id, text))

    def get_responses(self):
        return [response for _, response in self.current_responses]

    def add_vote(self, response_index):
        self.votes[response_index] += 1

    def get_votes(self):
        return dict(self.votes)

    def end_game(self):
        self.game_active = False

    def get_game_state(self):
        return {
            'round': self.round,
            'current_image': self.current_image,
            'responses': self.get_responses(),
            'votes': self.get_votes(),
            'game_active': self.game_active,
            'players': list(self.players)
        }
