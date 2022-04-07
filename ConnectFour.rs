use std::io;


enum Piece{ None, White, Black }


fn main() {
    let mut board = [[&Piece::None; 7]; 6];
    print_board(&board);
    let mut turn = &Piece::Black;
    loop {
        let col = loop {
            println!("Enter a number:");
            let mut input = String::new();
            io::stdin().read_line(&mut input).expect("Failed to read line");
            let input = input.trim();
            if ["exit", "q", "quit"].contains(&input) { return }
            match input.parse::<usize>(){
                Ok(res) => 
                    if res < 7 {
                        if let Piece::None = board[0][res]{
                            break res
                        } else {
                            println!("that col is already full");
                        }
                    } else {
                        println!("number needs to be in range 0-6 (inclusive)");
                    },
                Err(_) => println!("not a valid possitive number")
            };
        };
        let mut row = 0;
        for r in (0..board.len()).rev(){
            if let Piece::None = board[r][col]{
                board[r][col] = &turn;
                row = r;
                break;
            }
        }
        print_board(&board);
        if check_if_won(&board, row, col){
            println!("{} WON!", if let Piece::Black = turn { "X" } else { "O" });
            return
        }
        turn = if let Piece::Black = turn { &Piece::White } else { &Piece::Black };
    }
}

fn print_board(board: &[[&Piece;7];6]){
    for i in 0..board[0].len(){
        print!("{:width$}   ", i, width = 3);
    }
    for (r, row) in board.iter().enumerate() {
        if r != 0 { 
            for _ in 0..7 {    print!("------"); }
        } println!();
        for (c, var) in row.iter().enumerate() {
            print!("{:width$}",
                match *var {
                    Piece::Black => "X",
                    Piece::White => "O",
                    Piece::None => "",
                }, width = 5
            );
            if c != board.len() { print!("|"); }
        }
        println!();
    }
}

fn count_row(board: &[[&Piece;7];6], row: usize, col: usize, cur_color: &Piece) -> usize{
    let mut consecutive = 1;
    for c in col+1..board[0].len() {   
        if is_same(&board[row][c], cur_color) {
            consecutive += 1
        } else {    break; }    
    }
    for c in (0..col).rev() {   
        if is_same(&board[row][c], cur_color) {
            consecutive += 1
        } else {    break; }    
    }
    consecutive
}

fn count_col(board: &[[&Piece;7];6], row: usize, col: usize, cur_color: &Piece) -> usize{
    let mut consecutive = 1;
    for r in row+1..board.len() {   
        if is_same(&board[r][col], cur_color) {
            consecutive += 1
        } else {    break; }    
    }
    for r in (0..row).rev() {   
        if is_same(&board[r][col], cur_color) {
            consecutive += 1
        } else {    break; }    
    }
    consecutive
}

fn count_diagonal_u(board: &[[&Piece;7];6], row: usize, col: usize, cur_color: &Piece) -> usize{
    let mut consecutive = 1;
    let mut r = row + 1;
    let mut c = col + 1;
    while r < board.len() && c < board[0].len(){
        if ! is_same(cur_color, board[r][c]){
            break;
        }
        consecutive += 1;
        r += 1;
        c += 1;
    }
    let mut r = row as i16 - 1;
    let mut c = col as i16 - 1;
    while r >= 0 && c >= 0 {
        if ! is_same(cur_color, board[r as usize][c as usize]){
            break;
        }
        consecutive += 1;
        r -= 1;
        c -= 1;
    }
    consecutive
}

fn count_diagonal_d(board: &[[&Piece;7];6], row: usize, col: usize, cur_color: &Piece) -> usize{
    let mut consecutive = 1;
    let mut r = row + 1;
    let mut c = col as i16 - 1;
    while r < board.len() && c >= 0{
        if ! is_same(cur_color, board[r][c as usize]){
            break;
        }
        consecutive += 1;
        r += 1;
        c -= 1;
    }
    let mut r = row as i16 - 1;
    let mut c = col + 1;
    while r >= 0 && c < board[0].len() {
        if ! is_same(cur_color, board[r as usize][c]){
            break;
        }
        consecutive += 1;
        r -= 1;
        c += 1;
    }
    consecutive
}

fn check_if_won(board: &[[&Piece;7];6], row: usize, col: usize) -> bool {
    let cur_color = board[row][col];
    count_row(board, row, col, cur_color) >= 4 ||
    count_col(board, row, col, cur_color) >= 4 ||
    count_diagonal_d(board, row, col, cur_color) >= 4 ||
    count_diagonal_u(board, row, col, cur_color) >= 4
}

fn is_same(piece1: &Piece, piece2: &Piece) -> bool {
    match (piece1, piece2) {
        (&Piece::Black, &Piece::Black) => true,
        (&Piece::White, &Piece::White) => true,
        _ => false,
    }
}
