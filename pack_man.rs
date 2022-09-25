use console::Term;
use std::{fmt::Write, isize};

const BOARD_H: usize = 29;
const BOARD_W: usize = 28;
const UP:    DirCords = DirCords { row: -1, col:  0 };
const DOWN:  DirCords = DirCords { row:  1, col:  0 };
const LEFT:  DirCords = DirCords { row:  0, col: -1 };
const RIGHT: DirCords = DirCords { row:  0, col:  1 };
fn main() {
    println!("{:?}", Block::Ghost);
    let stdout = Term::buffered_stdout();

    let mut board = make_board();
    let mut player_pos = Pos {
        row: BOARD_H / 2, col: 2
    };
    board[player_pos.row][player_pos.col] = Block::Player;
    let mut score: usize= 0;

    print_board(&board, score);
    'game_loop: loop {
        if let Ok(character) = stdout.read_char() {
            move_player(&mut board, &mut player_pos, &mut score,
                match character {
                    'w' | 'W' => UP,   'a' | 'A' => LEFT,
                    's' | 'S' => DOWN, 'd' | 'D' => RIGHT,
                    _ => break 'game_loop,
                }
            );
            print_board(&board, score);
        }
    }
}

fn move_player(board: &mut [[Block; BOARD_W]; BOARD_H], player_pos: &mut Pos, score: &mut usize, dir: DirCords) {
    let new_row = (player_pos.row as isize + dir.row) as usize;
    let new_col =  player_pos.col as isize + dir.col;
    let new_col = if new_col == -1 { BOARD_W - 1 } else { new_col as usize % BOARD_W };
    if let Block::None | Block::Dot_ = board[new_row][new_col] {
        if let Block::Dot_ = board[new_row][new_col] {
            *score += 1;
        }
        board[player_pos.row][player_pos.col] = Block::None;
        board[new_row][new_col] = Block::Player;
        *player_pos = Pos { row: new_row, col: new_col};
    } 
}

fn make_board() -> [[Block; 28]; 29]{
    [
        [Block::Wall; 28],
        [Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        /*todo door*/[Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        
        [Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::Dot_, Block::None, Block::None, Block::None, Block::Wall, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::Wall, Block::None, Block::None, Block::None, Block::Dot_, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None],
        // bottom is supposed to be different
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::None, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        [Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::None, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall, Block::Wall, Block::Wall, Block::Wall, Block::Dot_, Block::Wall],
        [Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall, Block::Wall, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Dot_, Block::Wall],
        [Block::Wall; 28]
    ]
}

fn print_board(board: &[[Block; BOARD_W]; BOARD_H], score: usize){
    let mut res = String::new();
    write!(&mut res, "{esc}[2J{esc}[1;1HScore: {}\n", score, esc = 27 as char).unwrap(); //? clears the screen
    for line in board.iter(){
        for block in line.iter(){
            write!(&mut res, "{}", match block {
                Block::Dot_ => '∘',      Block::None => ' ',
                Block::Ghost => '⛄',    Block::Player => '▷',
                Block::Wall => '█'
            }).unwrap();
        } write!(&mut res, "\n").unwrap();
    }
    print!("{}", res);
}

#[derive(Debug, Copy, Clone)]
enum Block {    None, Wall, Dot_, Ghost, Player, }

struct DirCords {   row: isize, col: isize, }
struct Pos {    row: usize, col: usize, }
