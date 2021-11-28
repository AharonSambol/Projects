import threading
import tkinter
from time import sleep


class Stop:
    def __init__(self):
        self.is_stopped = False

    def stop(self):
        self.is_stopped = True


class GameOfLife:
    def __init__(self, btn_board, stop):
        self.button_board = btn_board
        self.life_posses = set()
        self.stop = stop

    def add_button(self, button, row, col):
        self.button_board[row][col] = button

    def add(self, row, col):
        was_alive = (row, col) in self.life_posses
        if was_alive:
            self.life_posses.remove((row, col))
        else:
            self.life_posses.add((row, col))
        btn = self.button_board[row][col]
        btn.configure(bg='white' if was_alive else 'black')

    def start(self):
        while len(self.life_posses) > 0:
            new_life_cells = set()
            count_board = [[0 for _ in range(AMOUNT_OF_BUTTONS)] for _ in range(AMOUNT_OF_BUTTONS)]
            for cell_row, cell_col in self.life_posses:
                for row_add in [-1, 0, 1]:
                    for col_add in [-1, 0, 1]:
                        if row_add == col_add == 0:
                            continue
                        new_row, new_col = cell_row + row_add, cell_col + col_add
                        new_cell = (new_row, new_col)
                        if new_row not in range(AMOUNT_OF_BUTTONS) or new_col not in range(AMOUNT_OF_BUTTONS):
                            continue
                        count_board[new_row][new_col] += 1
                        amount_of_neighbors = count_board[new_row][new_col]

                        is_alive = new_cell in self.life_posses
                        if (is_alive and amount_of_neighbors == 2) or amount_of_neighbors == 3:
                            new_life_cells.add(new_cell)
                        elif new_cell in new_life_cells:
                            new_life_cells.remove(new_cell)

            self.recolor_buttons(self.life_posses, new_life_cells)
            self.life_posses = new_life_cells

            sleep(0.5)
            if self.stop():
                break

    def recolor_buttons(self, old_live_cells, new_live_cells):
        for row, col in old_live_cells:
            self.button_board[row][col].configure(bg='white')
        for row, col in new_live_cells:
            self.button_board[row][col].configure(bg='black')

    def rand(self):
        pass


def set_up_board():
    root = tkinter.Tk()
    size = AMOUNT_OF_BUTTONS * 26
    root.geometry(f"{size}x{size+60}")

    btn_board = []
    for row in range(AMOUNT_OF_BUTTONS):
        btn_board.append([])
        for col in range(AMOUNT_OF_BUTTONS):
            button = tkinter.Button(root, text="     ", bg='white', command=lambda r=row, c=col: game.add(r, c))
            button.grid(row=row, column=col)
            btn_board[-1].append(button)

    stop = Stop()
    game = GameOfLife(btn_board, lambda: stop.is_stopped)

    start_button = tkinter.Button(root, text="Start", bg='green', command=lambda: start_thread(game))
    start_button.grid(row=AMOUNT_OF_BUTTONS, column=AMOUNT_OF_BUTTONS//2-1, columnspan=2)
    end_button = tkinter.Button(root, text="Stop", bg='red', command=lambda: stop.stop())   # todo only kinda works
    end_button.grid(row=AMOUNT_OF_BUTTONS + 1, column=AMOUNT_OF_BUTTONS//2-1, columnspan=2)
    root.mainloop()


def start_thread(game):
    thread = threading.Thread(target=game.start)
    thread.start()


AMOUNT_OF_BUTTONS = 20
set_up_board()
