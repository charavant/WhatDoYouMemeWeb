from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    current_round = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    current_image = db.Column(db.String(255), nullable=True)

    players = db.relationship('Player', back_populates='game')
    responses = db.relationship('Response', back_populates='game')

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.utcnow)

    game = db.relationship('Game', back_populates='players')
    responses = db.relationship('Response', back_populates='player')

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    submission_time = db.Column(db.DateTime, default=datetime.utcnow)

    game = db.relationship('Game', back_populates='responses')
    player = db.relationship('Player', back_populates='responses')
    votes = db.relationship('Vote', back_populates='response')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'), nullable=False)
    voter_ip = db.Column(db.String(45), nullable=False)  # Store IP address of voter
    vote_time = db.Column(db.DateTime, default=datetime.utcnow)

    response = db.relationship('Response', back_populates='votes')

class PredefinedResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
