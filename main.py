from flask import Flask, render_template, request, jsonify
from game_logic import GameManager

app = Flask(__name__)
game_manager = GameManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/player')
def player_view():
    return render_template('player.html')

@app.route('/audience')
def audience_view():
    return render_template('audience.html')

@app.route('/submit_response', methods=['POST'])
def submit_response():
    player_id = request.form['player_id']
    response = request.form['response']
    game_manager.add_response(player_id, response)
    return jsonify(success=True)

@app.route('/vote', methods=['POST'])
def vote():
    response_id = request.form['response_id']
    game_manager.add_vote(response_id)
    return jsonify(success=True)

@app.route('/game_state')
def game_state():
    return jsonify(game_manager.get_game_state())

if __name__ == '__main__':
    app.run(debug=True)