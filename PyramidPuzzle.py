import time

same_layer = [(0, -1, 0), (0, -1, 1), (0, 0, -1), (0, 0, 1), (0, 1, -1), (0, 1, 0)]
up_layer = [(1, 0, 0), (1, -1, 0), (1, 0, -1)]
down_layer = [(-1, 0, 0), (-1, +1, 0), (-1, 0, +1)]
ROTATIONS = same_layer + up_layer + down_layer


def solve(pieces):
    board = [[[True for _ in range(4)] for _ in range(4)] for _ in range(4)]
    posses = []
    for dimension in range(4):
        for row in range(4 - dimension):
            for col in range(4 - row - dimension):
                board[dimension][row][col] = False
                posses.append((dimension, row, col))
    return recurse(pieces, 0, board, posses)


def recurse(pieces, index, board, posses):
    if index == len(pieces):
        return board
    cur_piece = pieces[index]
    for dimension, row, col in posses:
        if board[dimension][row][col]:
            continue
        for _ in range(2):
            cur_piece = cur_piece[::-1]
            if not fits(cur_piece[0], (dimension, row, col), board):
                continue
            for rotation in ROTATIONS:
                new_pos = (dimension + rotation[0], row + rotation[1], col + rotation[2])
                if not in_range(new_pos):
                    continue
                if board[new_pos[0]][new_pos[1]][new_pos[2]]:
                    continue
                if not fits(cur_piece[1], new_pos, board):
                    continue
                board[dimension][row][col] = (cur_piece[0], index)
                board[new_pos[0]][new_pos[1]][new_pos[2]] = (cur_piece[1], index)
                posses.remove((dimension, row, col))
                posses.remove(new_pos)
                ans = recurse(pieces, index + 1, board, posses)
                if ans is not None:
                    return ans
                posses.append((dimension, row, col))
                posses.append(new_pos)
                board[dimension][row][col] = False
                board[new_pos[0]][new_pos[1]][new_pos[2]] = False
    return None


def in_range(arr):
    return all(0 <= x < 4 for x in arr)


def fits(piece, pos, board):
    for rotation in ROTATIONS:
        new_pos = [p + r for p, r in zip(pos, rotation)]
        if in_range(new_pos):
            neighbor = board[new_pos[0]][new_pos[1]][new_pos[2]]
            if type(neighbor) is tuple and neighbor[0] == piece:
                return False
    return True


def print_board(board):
    if board is None:
        print(None)
        return
    for d in board:
        for r in d:
            to_print = [x for x in r if type(x) is tuple]
            if len(to_print) > 0:
                print(to_print)
        print()


def main():
    t = time.time()
    _ = solve(['BW', 'LR', 'OR', 'BL', 'OW', 'OB', 'RW', 'OL', 'WL', 'BR'])
    _ = solve(['WR', 'WB', 'RO', 'LB', 'WL', 'WO', 'LR', 'OB', 'OL', 'RB'])
    _ = solve(['LR', 'OR', 'OB', 'RB', 'BL', 'OW', 'RW', 'LO', 'LW', 'WB'])
    _ = solve(['OL', 'BW', 'RL', 'OR', 'OW', 'OB', 'RW', 'LW', 'BL', 'BR'])
    _ = solve(['WB', 'OR', 'BL', 'WO', 'OB', 'LR', 'LW', 'OL', 'RW', 'BR'])
    print((time.time() - t) / 5)


if __name__ == '__main__':
    main()
