use console::Term;
use crossterm::style::Stylize;
use std::process::exit;
use std::{fmt::Write, isize};
use std::time::Duration;
use std::thread;
use std::sync::mpsc;

const BOARD_H: usize = 31;
const BOARD_W: usize = 28;
struct Dir; impl Dir {
    pub const UP:    DirCords = DirCords { row: -1, col:  0 };
    pub const DOWN:  DirCords = DirCords { row:  1, col:  0 };
    pub const LEFT:  DirCords = DirCords { row:  0, col: -1 }; 
    pub const RIGHT: DirCords = DirCords { row:  0, col:  1 };
}

type Board = [[Block; BOARD_W]; BOARD_H];
#[derive(Copy, Clone)]
enum Block { Empty, Wall, Dot, GhostP, GhostB, GhostR, GhostO, Player, Door }
#[derive(PartialEq, Eq)]
struct DirCords {   row: isize, col: isize, }

#[derive(PartialEq)] 
struct Pos { row: usize, col: usize, }
struct Ghost {   
    typ: GhostType, 
    pos: Pos, 
    over: Block,
    dir: DirCords,
    in_cage: bool,
    wait: usize
}
enum GhostType { Red, Pink, Orange, Blue }

fn main() { 
    let (mut board, mut player_pos, mut ghost_posses) = make_board();
    let mut score = 0;
    let mut player_dir = Dir::RIGHT;
    let (key_input_sender, key_input_receiver) = mpsc::channel();

    print_board(&board, score);
    thread::spawn(move || {
        let stdout = Term::buffered_stdout();
        loop {
            if let Ok(chr) = stdout.read_char() {
                key_input_sender.send(chr).unwrap();
            }
        }
    });

    let mut frame: u8 = 0;
    let delay = Duration::from_millis(50);
    const MOVE_DELAY: u8 = 5; const GHOST_MOVE_DELAY: u8 = 6;
    loop {
        thread::sleep(delay);
        frame += 1;
        let is_move_frame = frame % MOVE_DELAY == 0;
        let is_ghost_move_frame = frame % GHOST_MOVE_DELAY == 0;
        if is_move_frame {
            move_player(&mut board, &mut player_pos, &mut score, &player_dir);
        }
        if let Ok(chr) = key_input_receiver.try_recv() {
            let new_dir = match chr {
                'w' | 'W' => Dir::UP,   'a' | 'A' => Dir::LEFT,
                's' | 'S' => Dir::DOWN, 'd' | 'D' => Dir::RIGHT,
                _ => exit(0)
            };
            let pos = get_pos_in_dir(&player_pos, &new_dir);
            if !matches!(board[pos.row][pos.col], Block::Door | Block::Wall) {
                player_dir = new_dir;
            }
        }
        if is_ghost_move_frame {
            move_ghosts(&mut ghost_posses, &mut board, &player_pos, &player_dir);
        }
        if is_move_frame || is_ghost_move_frame {
            if is_move_frame && is_ghost_move_frame {   frame = 0; }
            print_board(&board, score);
        }
    }
}

fn clamp(pos: isize, max: usize) -> usize {
    if pos < 0 { 0 } else if pos as usize > max { max } else { pos as usize }
}

fn move_ghosts(
    ghost_posses: &mut Vec<Ghost>, board: &mut Board, player_pos: &Pos, player_dir: &DirCords
) {
    for ghost in ghost_posses.iter(){
        board[ghost.pos.row][ghost.pos.col] = ghost.over;
    }
    let red_ghost_pos = Pos { ..ghost_posses[0].pos };
    for ghost in ghost_posses.iter_mut(){
        if ghost.wait != 0 {
            place_ghost(board, ghost);
            ghost.wait -= 1;
            continue;
        }
        let mut should_move = true;
        if is_at_intersection(board, &ghost.pos, &ghost.dir) {
            let dest = get_dest(player_pos, player_dir, &red_ghost_pos, ghost);
            let calced_dir = path_finding(&board, &ghost, &dest);
            should_move = calced_dir != None;
            if let Some(new_dir) = calced_dir {
                ghost.dir = new_dir;
            }
        }
        if should_move {
            let new_pos = get_pos_in_dir(&ghost.pos, &ghost.dir);
            if !matches!(board[new_pos.row][new_pos.col], // not a great solution
                Block::GhostB | Block::GhostO | Block::GhostR | Block::GhostP
            ) {
                ghost.pos = Pos { ..new_pos };
                if new_pos == *player_pos {
                    print!("You Died");
                    exit(0);
                }
            }
        }
        place_ghost(board, ghost);
    }
}

fn get_dest(player_pos: &Pos, player_dir: &DirCords, red_ghost_pos: &Pos, ghost: &mut Ghost) -> Pos {
    if ghost.in_cage {
        if ghost.pos.row <= 12 {
            ghost.in_cage = false;
        }
        Pos { row: 0, col: BOARD_W / 2 }
    } else {
        match ghost.typ {
            GhostType::Red => Pos { ..*player_pos },
            GhostType::Pink => Pos {
                row: clamp(player_pos.row as isize + player_dir.row * 2, BOARD_H),
                col: clamp(player_pos.col as isize + player_dir.col * 2, BOARD_W)
            },
            GhostType::Blue => Pos {
                row: clamp(player_pos.row as isize * 2 - red_ghost_pos.row as isize, BOARD_H),
                col: clamp(player_pos.col as isize * 2 - red_ghost_pos.col as isize, BOARD_W),
            },
            GhostType::Orange => {
                let dist
                    = clamp(player_pos.row as isize - ghost.pos.row as isize, BOARD_H).pow(2)
                    + clamp(player_pos.col as isize - ghost.pos.col as isize, BOARD_W).pow(2);
                if dist > 8 * 8 { Pos { ..*player_pos } } else { Pos { row: BOARD_H - 2, col: 2 } }
            },
        }
    }
}

fn place_ghost(board: &mut Board, ghost: &mut Ghost) {
    ghost.over = match board[ghost.pos.row][ghost.pos.col] {
        Block::GhostB | Block::GhostO | Block::GhostP | Block::GhostR => Block::Empty,
        _ => board[ghost.pos.row][ghost.pos.col]
    };
    board[ghost.pos.row][ghost.pos.col] = match ghost.typ {
        GhostType::Blue => Block::GhostB,
        GhostType::Red => Block::GhostR,
        GhostType::Orange => Block::GhostO,
        GhostType::Pink => Block::GhostP,
    };
}

fn is_at_intersection(board: &Board, pos: &Pos, dir: &DirCords) -> bool {
    let other_dirs 
        = if *dir == Dir::UP || *dir == Dir::DOWN 
            {   [Dir::RIGHT,    Dir::LEFT]  } 
        else{   [Dir::UP,       Dir::DOWN]  };
    for dir in other_dirs {
        let pos_in_dir = get_pos_in_dir(pos, &dir);
        if !matches!(board[pos_in_dir.row][pos_in_dir.col], Block::Wall){
            return true;
        }
    }
    false
}

fn move_player(board: &mut Board, player_pos: &mut Pos, score: &mut usize, dir: &DirCords) {
    let new_pos = get_pos_in_dir(player_pos, &dir);
    if let Block::Empty | Block::Dot = board[new_pos.row][new_pos.col] {
        if let Block::Dot = board[new_pos.row][new_pos.col] {
            *score += 1;
        }
        board[player_pos.row][player_pos.col] = Block::Empty;
        board[new_pos.row][new_pos.col] = Block::Player;
        *player_pos = Pos { row: new_pos.row, col: new_pos.col };
    } 
}

fn get_pos_in_dir(player_pos: &Pos, dir: &DirCords) -> Pos {
    let new_row = (player_pos.row as isize + dir.row) as usize;
    let new_col =  player_pos.col as isize + dir.col;
    let new_col = if new_col == -1 { BOARD_W - 1 } else { new_col as usize % BOARD_W };
    Pos { row: new_row, col: new_col }
}

fn make_board() -> (Board, Pos, Vec<Ghost>) {
    const BOARD_REP: &str =
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
######.## # R  P # ##.######
@     .   #      #   .      
######.## # O  B # ##.######
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
    for (r, line) in BOARD_REP.split('\n').enumerate(){
        for (c, char) in line.chars().enumerate(){
            res[r][c] = match char {
                '#' => Block::Wall,     '.' => Block::Dot,
                ' ' => Block::Empty,    '-' => Block::Door,
                '@' => {
                    (player_pos.row, player_pos.col) = (r, c);
                    Block::Player
                },
                'R' | 'O' | 'B' | 'P' => {
                    let (typ, wait, block) = match char {
                        'R'     => (GhostType::Red,     0,  Block::GhostR),
                        'O'     =>  (GhostType::Orange, 50, Block::GhostO), // todo third of dots
                        'B'     =>  (GhostType::Blue,   20, Block::GhostB), // todo 30 dots
                        'P' | _ =>  (GhostType::Pink,   3,  Block::GhostP),
                    };
                    ghosts.push(Ghost {
                        typ, wait,
                        pos: Pos { row: r, col: c },
                        over: Block::Empty,
                        dir: Dir::UP,
                        in_cage: true,
                    });
                    block
                },
                _ => panic!(),
            };
        }
    }
    (res, player_pos, ghosts)
}

fn print_board(board: &Board, score: usize) {
    let mut res = String::new();
    writeln!(&mut res,
            //? clears the screen
            "{esc}[2J{esc}[1;1HScore: {}\n████████████████████████████",
            score, esc = 27 as char
    ).unwrap();
    for line in board[1..board.len()-1].iter() {
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
    writeln!(&mut res, "████████████████████████████").unwrap();
    print!("{}", res);
}

fn path_finding(board: &Board, ghost: &Ghost, dest: &Pos) -> Option<DirCords> {
    let back = match ghost.dir {
        Dir::UP => Dir::DOWN,       Dir::DOWN => Dir::UP,
        Dir::RIGHT => Dir::LEFT,    Dir::LEFT => Dir::RIGHT,
        _ => panic!()
    };
    let mut res = None;
    let mut min_dist: isize = 0;
    for dir in [Dir::UP, Dir::DOWN, Dir::RIGHT, Dir::LEFT]{
        if dir == back {    continue; }
        let pos_in_dir = get_pos_in_dir(&ghost.pos, &dir);
        if matches!(board[pos_in_dir.row][pos_in_dir.col], Block::Wall)
            || (!ghost.in_cage && matches!(board[pos_in_dir.row][pos_in_dir.col], Block::Door)) {
            continue;
        }
        
        if let None = res { 
            res = Some(dir);
            min_dist = 
                (dest.row as isize - pos_in_dir.row as isize).pow(2) 
                + (dest.col as isize - pos_in_dir.col as isize).pow(2);
        } else {
            let dist =
                (dest.row as isize - pos_in_dir.row as isize).pow(2) 
                + (dest.col as isize - pos_in_dir.col as isize).pow(2);
            if dist < min_dist {
                min_dist = dist;
                res = Some(dir);
            }
        }
    }
    res
}
