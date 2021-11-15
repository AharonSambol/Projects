from flask import Flask, request
from random import randint
import re
import json

class Game:
    allGames = dict()

    def __init__(self, numOfPlyrs, oid=False):
        if not oid:
            self.id = randint(0, 1000000)
            while self.id in self.allGames:
                self.id = randint(0, 1000000)
            self.allGames[self.id] = self

        self.amountOfPlayers = numOfPlyrs
        self.board = [[{}]*150]*150
        self.playersNames = []
        self.playersIDs = {}
        self.scores = {}
        self.turn = 0
        self.tiles = allshapes()
        self.hands = {}
        self.points = {}  # 5!!!!!!!!!!!!!!!!!!!!1!!!!!!!!!!!!!!!!!!!!!2!!!!!!!!!!!!!!!!!!!!!!!3!!!!!!!!!!!!!!!!!!!!!!4

    def add_player(self, name):
        if len(self.playersNames) == 4:
            return False, None
        self.playersNames.append(name)
        self.scores[name] = 0

        player_id = randint(1000000, 9999999)
        while self.playersIDs.__contains__(player_id):
            player_id = randint(1000000, 9999999)

        # 1 not sure if should be id to name or name to id!
        self.playersIDs[str(player_id)] = name
        self.hands[str(player_id)] = []
        return True, player_id

    def play(self, player_id, colors, shapes, rows, cols):
        # 2 check that the player actually has those pieces
        for c, s in zip(colors, shapes):
            if (c, s) not in self.hands[player_id]:
                return "you don't have those tiles! your hand is:" + str(self.hands[player_id])

        # 2 make sure that those places are empty
        for r, c in zip(rows, cols):
            if self.board[int(r)][int(c)] != {}:
                return "place is taken"

        # 2 no duplicates
        if len(shapes) != len(set(shapes)) or len(colors) != len(set(colors)):
            return "different numbers of each parameter in move is invalid"

        # # 2 all valid moves
        # # 3 probably pretty slow...
        # for s, clr, r, c in zip(shapes, colors, rows, cols):
        #     if not self.is_safe(s, clr, r, c):
        #         return "not valid move"

        # 2 place into board
        for s, clr, r, c in zip(shapes, colors, rows, cols):
            self.board[int(r)][int(c)] = {"color": clr, "shape": s}
            # 2 remove from hand
            self.hands[player_id].remove({"color": clr, "shape": s})

        # 2 all valid moves
        # 3 probably pretty slow...
        for s, clr, r, c in zip(shapes, colors, rows, cols):
            if not self.is_safe(s, clr, int(r), int(c)):
                # 2 unplace the tiles
                for s2, clr2, r2, c2 in zip(shapes, colors, rows, cols):
                    # 2 put back in hand
                    self.hands[player_id].append(self.board[r2][c2])
                    self.board[int(r2)][int(c2)] = {}

                return "not valid move"

        # 2 change the turn
        self.turn += 1
        self.turn %= self.amountOfPlayers

        # 2 returns new pieces
        pieces = {}
        for i in colors:
            piece = self.get_piece()
            pieces["tile"+str(i)] = piece
            # 3 add to hand
            self.hands[player_id].append(piece)
        return pieces

    def is_safe(self, shape, color, row_plc, col_plc):
        row = []
        col = []

        # 2 get col
        for i in range(row_plc, 215):
            tile = self.board[i][col_plc]
            if tile is None:
                break
            col.append(tile)
        for i in range(1, 215):
            tile = self.board[row_plc-i][col_plc]
            if tile is None:
                break
            col.append(tile)

        # 2 get row
        for i in range(col_plc, 215):
            tile = self.board[row_plc][i]
            if tile is None:
                break
            row.append(tile)
        for i in range(1, 215):
            tile = self.board[row_plc][col_plc-i]
            if tile is None:
                break
            row.append(tile)

        kind_of_groups = ["", ""]
        # 2 group one
        if len(row) > 1:
            if row[0]["color"] == row[1]["color"]:
                kind_of_groups[0] = "sameColor"
            elif row[0]["shape"] == row[1]["shape"]:
                kind_of_groups[0] = "sameShape"
            else:
                kind_of_groups[0] = "dif"
        # 2 group two
        if len(row) > 1:
            if row[0]["color"] == row[1]["color"]:
                kind_of_groups[1] = "sameColor"
            elif row[0]["shape"] == row[1]["shape"]:
                kind_of_groups[1] = "sameShape"
            else:
                kind_of_groups[1] = "dif"

        for i, kind in enumerate(kind_of_groups):

            group = row if i == 0 else col

            if kind == "sameColor":
                if color != group[0]["color"]:
                    return False
                if contains(group, shape, "shape"):
                    return False

            elif kind == "sameShape":
                if shape != group[0]["shape"]:
                    return False
                if contains(group, color, "color"):
                    return False

            elif kind == "dif":
                if contains(group, color, "color") or contains(group, shape, "shape"):
                    return False

        return True

    def get_piece(self):
        i = randint(0, len(self.tiles)-1)
        tile = self.tiles[i]
        del self.tiles[i]
        return tile["shape"]+tile["color"]


def contains(group, compare, compare_st):
    for x in group:
        if x[compare_st] == compare:
            return True
    return False

def allshapes():
    clrs = ["r", "o", "y", "g", "b", "p"]
    shapes = ["!", "@", "#", "$", "%", "^"]
    tiles = []
    for c in clrs:
        for s in shapes:
            tiles.append({"color": c, "shape": s})
    return tiles

# 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2 --------------------------------------------------------------------------------------------------------------------
# 3 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 2 --------------------------------------------------------------------------------------------------------------------
# 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


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
    return instructions()


@app.route("/newgame")  # 5 amount of players?
def create_game():
    numOfPlyrs = request.args['amountOfPlayers']
    if numOfPlyrs is None or numOfPlyrs == "":
        return "amountOfPlayers is required"
    if not numOfPlyrs.isnumeric():
        return "amountOfPlayers needs to be a number"
    g = Game(numOfPlyrs)
    return str(g.id)


@app.route("/register")
def register():
    game, message = get_game(request.args['game'])
    if game is None:
        return message

    try:
        name = request.args['newPlayer']
    except:
        return "newPlayer is required"
    added, p_id = game.add_player(name)
    if added:
        tiles = {"id": p_id}
        for i in range(5):
            tile = game.get_piece()
            tiles["tile"+str(i)] = tile
            game.hands[str(p_id)].append(tile)
        return json.dumps(tiles)
    return "Game already full"


@app.route("/entermove")
def play():
    game, message = get_game(request.args['game'])
    if game is None:
        return message

    colors = request.args['colors']
    if colors is None or colors == "":
        return "colors are required"
    if not re.match(r'^[roygbp]*$', "".join(colors)):
        return "colors must consist of only: r o y g b p" + "!" + "".join(colors)

    # 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # 5 not url encoded !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    shapes = request.args['shapes']
    if shapes is None or shapes == "":
        return "shapes are required"
    if not re.match(r'^[!@#$%^]*$', "".join(shapes)):
        return "shapes must consist of only one: ! @ # $ % ^ \n you entered:" + "".join(shapes)

    rows = request.args['rows'].split(",")
    if rows is None or rows == "":
        return "row is required"
    if not "".join(rows).isnumeric():
        return "rows must be valid numbers \n you entered: " + "".join(rows)

    cols = request.args['cols'].split(",")
    if cols is None or cols == "":
        return "col is required"
    if not "".join(cols).isnumeric():
        return "cols must be valid numbers \n you entered: " + "".join(cols)

    player_id = request.args['player']
    if player_id is None or player_id == "":
        return "player id is required"
    if player_id not in game.playersIDs:
        return "invalid player id \n you entered: " + player_id

    if len(colors) != len(shapes) or len(colors) != len(rows) or len(colors) != len(cols):
        return """the amount of shapes needs to equal the amount of colors and to the amount of rows and cols
        you entered: 
        colors:""" + str(len(colors)) + """
        shapes:""" + str(len(shapes)) + """
        rows:""" + str(len(rows)) + """
        cols:""" + str(len(cols))

    result = game.play(player_id, colors, shapes, rows, cols)
    if type(result) == str:
        return result
    return json.dumps(result)

# 4 get score
# 5 get scores


@app.route("/getboard")
def get_board():
    game, message = get_game(request.args['game'])
    if game is None:
        return message
    return str(game.board)


@app.route("/getturn")
def get_turn():
    game, message = get_game(request.args['game'])
    if game is None:
        return message

    # 2 if game has started
    if len(game.playersNames) == game.amountOfPlayers:
        return str(game.playersNames[game.turn])
    return "game hasn't started"


@app.route("/restart")
def restart():
    # 1 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # 1 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # 6 !!!! will forget players names and all that !!!!
    # 1 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # 1 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    game, message = get_game(request.args['game'])
    if game is None:
        return message

    g = Game(game.amountOfPlayers, True)
    return str(g.id)


def instructions():
    return "hi there"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8082', debug=True)
