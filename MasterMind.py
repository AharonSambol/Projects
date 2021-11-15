from flask import Flask, request
from random import randint
import re


class Game:
    allGames = dict()

    def __init__(self, pattern):
        self.id = randint(0, 10)
        while self.id in self.allGames:
            self.id = randint(0, 1000)
        self.allGames[self.id] = self

        self.pattern = pattern
        self.turns_left = 10
        self.board = ""

    def guess(self, pattern):
        if self.turns_left == 0:
            return "Game has ended"

        response = []
        new_pattern = ""
        new_real = ""
        for guess, real in zip(pattern, self.pattern):
            if guess == real:
                response.append('b')
                new_real += "-"
                new_pattern += '-'
            else:
                new_real += real
                new_pattern += guess

        for counter, num_in_guess in enumerate(new_pattern):
            if num_in_guess in new_real and num_in_guess != '-':
                response.append('w')
                new_real.replace(num_in_guess, '-')

        for _ in range(len(response), 4):
            response.append('0')    # theres a better way to do this- rjust im just lazy...

        self.turns_left -= 1

        if len(self.board) != 0:
            self.board += ","
        self.board += pattern + " " + "".join(response)
        return "".join(response) + " " + str(self.turns_left)

    def restart(self, pattern):
        self.pattern = pattern
        self.turns_left = 10


app = Flask(__name__)


def get_game(game_id):
    if game_id is None or not game_id.isnumeric():
        return None, "game parameter is required and must be a number."
    try:
        return Game.allGames[int(game_id)], ""
    except KeyError:
        return None, "No such game"


@app.route("/")
def route():
    r = instructions()
    return r


@app.route("/newgame")
def create_game():
    try:
        pattern = request.args['pattern']
    except:
        return "pattern is required"
    if pattern == "random":
        pattern = ""
        for _ in range(4):
            pattern += str(randint(1, 6))
    if len(pattern) != 4 or not re.match(r'[1-6]*', pattern):
        return "Pattern must consist only of 4 numbers in the range of 1 to 6"
    g = Game(pattern)
    return str(g.id)


@app.route("/getBoard")
def get_board():
    game, message = get_game(request.args['game'])
    if game is None:
        return message
    return game.board


@app.route("/play")
def play():
    game, message = get_game(request.args['game'])
    if game is None:
        return message

    guess = request.args['pattern']
    if guess is None or guess == "":
        return "Guess is required"
    if len(guess) != 4 or not re.match(r'[1-6]*', guess):
        return "Guess must consist only of 4 numbers in the range of 1 to 6"

    return str(game.guess(guess))


@app.route("/restart")
def restart():
    game, message = get_game(request.args['game'])
    if game is None:
        return message
    try:
        pattern = request.args['newpattern']
    except:
        return "pattern is required"

    if len(pattern) != 4 or not re.match(r'[1-6]*', pattern):
        return "Pattern must consist only of 4 numbers in the range of 1 to 6"
    game.restart(pattern)
    return "ok"


def instructions():
    return "hi there"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8088', debug=True)
