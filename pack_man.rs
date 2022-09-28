use console::Term;
use std::process::exit;
use std::{fmt::Write, isize};
use std::time::Duration;
use std::thread;
use std::sync::mpsc;


const BOARD_H: usize = 31;
const BOARD_W: usize = 28;
const UP:    DirCords = DirCords { row: -1, col:  0 };
const DOWN:  DirCords = DirCords { row:  1, col:  0 };
const LEFT:  DirCords = DirCords { row:  0, col: -1 };
const RIGHT: DirCords = DirCords { row:  0, col:  1 };
const GHOST_COLORS: [GhostType; 4] = [GhostType::Blue, GhostType::Orange, GhostType::Pink, GhostType::Red];

type Board = [[Block; BOARD_W]; BOARD_H];

#[derive(Copy, Clone)] 
enum Block { Empty, Wall, Dot, Ghost, Player, Door }

struct DirCords {   row: isize, col: isize, }

#[derive(Copy, Clone)] 
struct Pos { row: usize, col: usize, }

struct Ghost {   typ: GhostType, pos: Pos, }

#[derive(Copy, Clone)] 
enum GhostType { Red, Pink, Orange, Blue }

fn main() { 
    let (mut board, mut player_pos, mut ghost_posses) = make_board();
    let mut score = 0;
    
    let (key_input_sender, key_input_reciever) = mpsc::channel();
    let (ghost_move_sender, ghost_move_reciever) = mpsc::channel();
    
    print_board(&board, score);
    thread::spawn(move || {
        let stdout = Term::buffered_stdout();
        loop {
            if let Ok(chr) = stdout.read_char() {
                key_input_sender.send(chr).unwrap();
            }
        }
    });
    thread::spawn(move || {
        let delay = Duration::from_millis(1000);
        loop {
            thread::sleep(delay);
            ghost_move_sender.send(true).unwrap()
        }
    });
    loop {
        if let Ok(chr) = key_input_reciever.try_recv() {
            move_player(&mut board, &mut player_pos, &mut score,
                match chr {
                    'w' | 'W' => UP,   'a' | 'A' => LEFT,
                    's' | 'S' => DOWN, 'd' | 'D' => RIGHT,
                    _ => exit(0),
                }
            );
            print_board(&board, score);
        }
        if let Ok(_) = ghost_move_reciever.try_recv() {
            for ghost in ghost_posses.iter_mut(){
                // todo
                match ghost.typ {
                    GhostType::Blue => {
                        board[ghost.pos.row][ghost.pos.col] = Block::Empty;
                        board[ghost.pos.row - 1][ghost.pos.col] = Block::Ghost;
                        ghost.pos.row -= 1;
                    }
                    GhostType::Orange => {}
                    GhostType::Red => {}
                    GhostType::Pink => {}
                }
            }
            print_board(&board, score);
        }
    }
}

fn move_player(board: &mut Board, player_pos: &mut Pos, score: &mut usize, dir: DirCords) {
    let new_row = (player_pos.row as isize + dir.row) as usize;
    let new_col =  player_pos.col as isize + dir.col;
    let new_col = if new_col == -1 { BOARD_W - 1 } else { new_col as usize % BOARD_W };
    if let Block::Empty | Block::Dot = board[new_row][new_col] {
        if let Block::Dot = board[new_row][new_col] {
            *score += 1;
        }
        board[player_pos.row][player_pos.col] = Block::Empty;
        board[new_row][new_col] = Block::Player;
        *player_pos = Pos { row: new_row, col: new_col};
    } 
}

fn make_board() -> (Board, Pos, Vec<Ghost>) {
    let board_rep = 
"############################
#............##............#
#.####.#####.##.#####.####.#
#.####.#####.##.#####.####.#
#.####.#####.##.#####.####.#
#..........................#
#.####.##.########.##.####.#
#.####.##.########.##.####.#
#......##....##....##......#
######.##### ## #####.######
######.##### ## #####.######
######.##          ##.######
######.## ###--### ##.######
######.## #      # ##.######
@     .   #  ^^  #   .      
######.## #  ^^  # ##.######
######.## ######## ##.######
######.##          ##.######
######.## ######## ##.######
######.## ######## ##.######
#............##............#
#.####.#####.##.#####.####.#
#.####.#####.##.#####.####.#
#...##................##...#
###.##.##.########.##.##.###
###.##.##.########.##.##.###
#......##....##....##......#
#.##########.##.##########.#
#.##########.##.##########.#
#..........................#
############################";
    let mut player_pos = Pos { row: 0, col: 0 };
    let mut ghosts = vec![];
    let mut ghost_c = 0;
    let mut res = [[Block::Empty; BOARD_W]; BOARD_H];
    for (r, line) in board_rep.split('\n').enumerate(){
        for (c, char) in line.chars().enumerate(){
            res[r][c] = match char {
                '#' => Block::Wall,     '.' => Block::Dot,
                ' ' => Block::Empty,    '-' => Block::Door,
                '@' => {
                    (player_pos.row, player_pos.col) = (r, c);
                    Block::Player
                },
                '^' => {
                    ghosts.push(Ghost { 
                        typ: GHOST_COLORS[ghost_c], 
                        pos: Pos { row: r, col: c }
                    });
                    ghost_c += 1;
                    Block::Ghost
                },
                _ => panic!(),
            };
        }
    }
    (res, player_pos, ghosts)
}

fn print_board(board: &Board, score: usize){
    let mut res = String::new();
    write!(&mut res, "{esc}[2J{esc}[1;1HScore: {}\n", score, esc = 27 as char).unwrap(); //? clears the screen
    for line in board.iter(){
        for block in line.iter(){
            write!(&mut res, "{}", match block {
                Block::Dot => '∘',      Block::Empty => ' ',
                Block::Ghost => '^',   Block::Player => '▷',
                Block::Wall => '█',     Block::Door => '='
            }).unwrap();
        } write!(&mut res, "\n").unwrap();
    }
    print!("{}", res);
}
