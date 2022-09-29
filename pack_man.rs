use console::Term;
use crossterm::style::Stylize;
use std::process::exit;
use std::{fmt::Write, isize};
use std::time::{Duration, Instant};
use std::thread;
use std::sync::mpsc;
use std::collections::HashSet;

const BOARD_H: usize = 31;
const BOARD_W: usize = 28;
const UP:    DirCords = DirCords { row: -1, col:  0 };
const DOWN:  DirCords = DirCords { row:  1, col:  0 };
const LEFT:  DirCords = DirCords { row:  0, col: -1 };
const RIGHT: DirCords = DirCords { row:  0, col:  1 };

type Board = [[Block; BOARD_W]; BOARD_H];

#[derive(Copy, Clone, Debug)] 
enum Block { Empty, Wall, Dot, GhostP, GhostB, GhostR, GhostO, Player, Door }

struct DirCords {   row: isize, col: isize, }

#[derive(Debug, Copy, Clone, PartialEq)] 
struct Pos { row: usize, col: usize, }
struct Ghost {   typ: GhostType, pos: Pos, over: Block }

#[derive(Copy, Clone)] 
enum GhostType { Red, Pink, Orange, Blue }
enum Dir { Up, Dowm, Right, Left }

fn main() { 
    let (mut board, mut player_pos, mut ghost_posses) = make_board();
    let mut score = 0;
    let mut player_dir = Dir::Right;
    let (key_input_sender, key_input_reciever) = mpsc::channel();
    let (ghost_move_sender, ghost_move_reciever) = mpsc::channel();
    
    print_board(&board, score);
    thread::spawn(move || {
        let stdout = Term::buffered_stdout();
        let mut last = Instant::now();
        loop {
            if let Ok(chr) = stdout.read_char() {
                if last.elapsed().as_millis() > 50 {
                    key_input_sender.send(chr).unwrap();
                    last = Instant::now();
                }
            }
        }
    });
    thread::spawn(move || {
        let delay = Duration::from_millis(400);
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
            player_dir = match chr {
                'w' | 'W' => Dir::Up,   'a' | 'A' => Dir::Left,
                's' | 'S' => Dir::Dowm, 'd' | 'D' => Dir::Right,
                _ => panic!()
            };
            print_board(&board, score);
        }
        
        if let Ok(_) = ghost_move_reciever.try_recv() {
            move_ghosts(&mut ghost_posses, &mut board, player_pos, &player_dir);
            print_board(&board, score);
        }
    }
}

fn move_ghosts(ghost_posses: &mut Vec<Ghost>, board: &mut Board, player_pos: Pos, player_dir: &Dir) {
    fn clamp(pos: isize, max: usize) -> usize {
        if pos < 0 { 0 } else if pos as usize > max { max } else { pos as usize }
    }
    for ghost in ghost_posses.iter(){
        board[ghost.pos.row][ghost.pos.col] = ghost.over;
    }
    let red_ghost_pos = ghost_posses[0].pos;
    for ghost in ghost_posses.iter_mut(){
        let end = match ghost.typ {
            GhostType::Red => player_pos,
            GhostType::Pink => Pos {
                row: clamp(player_pos.row as isize + match *player_dir {
                    Dir::Up => -2, Dir::Dowm => 2, _ => 0
                }, BOARD_H),
                col: clamp(player_pos.col as isize + match *player_dir {
                    Dir::Left => -2, Dir::Right => 2, _ => 0
                }, BOARD_W)
            },
            GhostType::Blue => {
                Pos {
                    row: clamp(player_pos.row as isize + (player_pos.row as isize - red_ghost_pos.row as isize), BOARD_H),
                    col: clamp(player_pos.col as isize + (player_pos.col as isize - red_ghost_pos.col as isize), BOARD_W),
                }
            },
            GhostType::Orange => {
                let dist 
                    = clamp(player_pos.row as isize - ghost.pos.row as isize, BOARD_H).pow(2) 
                    + clamp(player_pos.col as isize - ghost.pos.col as isize, BOARD_W).pow(2);
                if dist > 8 * 8 { player_pos } else { Pos {row: BOARD_H - 2, col: 2 } }
            },
        };
        if let Option::Some(new_pos) = path_finding(&board, ghost.pos, end) {
            ghost.pos = new_pos;
            ghost.over = board[ghost.pos.row][ghost.pos.col];
        }
    }
    for ghost in ghost_posses.iter(){
        board[ghost.pos.row][ghost.pos.col] = match ghost.typ {
            GhostType::Blue =>      Block::GhostB,
            GhostType::Red =>       Block::GhostR,
            GhostType::Orange =>    Block::GhostO,
            GhostType::Pink =>      Block::GhostP,
        };
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
######.## # R  B # ##.######
@     .   #      #   .      
######.## # O  P # ##.######
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
                'R' | 'O' | 'B' | 'P' => {
                    ghosts.push(Ghost { 
                        typ: match char {
                            'R' => GhostType::Red,    'O' => GhostType::Orange,
                            'B' => GhostType::Blue,   'P' | _ => GhostType::Pink,
                        }, 
                        pos: Pos { row: r, col: c },
                        over: Block::Empty
                    });
                    match char {
                        'R' => Block::GhostR,   'O' => Block::GhostO,
                        'B' => Block::GhostB,   'P' | _ => Block::GhostP,
                    }
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
    for (i, line) in board.iter().enumerate() {
        if i == 0 || i == BOARD_H - 1 {
            write!(&mut res, "████████████████████████████\n").unwrap();
            continue;
        }
        for block in line.iter() {
            match block {
                Block::GhostB | Block::GhostR | Block::GhostP 
                | Block::GhostO | Block::Player => write!(&mut res, "{}", match block {
                    Block::GhostB => format!("@").blue(),       Block::GhostR => format!("@").red(), 
                    Block::GhostP => format!("@").magenta(),    Block::GhostO => format!("@").dark_yellow(),   
                    Block::Player => format!("▷").yellow(),
                    _ => panic!()
                }).unwrap(),
                _ => write!(&mut res, "{}", match block {
                    Block::Dot => '∘',      Block::Empty => ' ',
                    Block::Wall => '█',     Block::Door => '=',
                    _ => panic!()
                }).unwrap()
            };
        } write!(&mut res, "\n").unwrap();
    }
    print!("{}", res);
}

fn path_finding(board: &Board, start: Pos, end: Pos) -> Option<Pos> {
    // ? brute force - cuz it's good enough
    let mut visited = HashSet::new();
    visited.insert((start.row, start.col));
    let mut calc_next = vec![(start, Option::None)];
    while !calc_next.is_empty() {
        let cur_calc = calc_next;
        calc_next = vec![];
        for (pos, parent_dir) in cur_calc {
            for dir in [(0, 1), (1, 0), (0, -1), (-1, 0)]{
                let new_row = (pos.row as isize + dir.0) as usize;
                let new_col = pos.col as isize + dir.1;
                let new_col = if new_col == -1 { BOARD_W - 1 } else { new_col as usize % BOARD_W }; 
                if let Block::Wall = board[new_row][new_col] {}
                else {
                    if !visited.contains(&(new_row, new_col)){
                        let pos = Pos{ row: new_row, col: new_col};
                        calc_next.push((pos, if let None = parent_dir { Option::Some(Pos{ row: new_row, col: new_col }) } else { parent_dir }));
                        visited.insert((new_row, new_col));
                    }
                }
                if end.row == new_row && end.col == new_col {
                    return parent_dir;
                }
            }
        }
    }
    Option::None
}
