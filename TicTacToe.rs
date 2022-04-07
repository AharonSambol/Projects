use std::io;

fn main() {
    let mut board = [['-'; 3]; 3];
    let mut turn = 'x';
    loop {
        let pos = loop {
            println!("Enter a number:");
            let mut input = String::new();
            io::stdin().read_line(&mut input).expect("Failed to read line");
            if ["exit", "q", "quit"].contains(&input.trim()) { return }
            match input.trim().parse::<usize>(){
                Ok(res) => 
                    if res < 9 {
                        let row = res / 3;
                        let col = res % 3;
                        if board[row][col] == '-'{
                            break (row, col)
                        } else {
                            println!("that space is already full");
                        }
                    } else {
                        println!("number needs to be in range 0-8 (inclusive)");
                    },
                Err(_) => println!("not a valid possitive number")
            };
        };
        board[pos.0][pos.1] = turn;
        turn = if turn == 'x' { 'o' } else { 'x' };
        print_board(&board);
        let winner = check_winner(&board);
        if winner.0{
            println!("{} WON!", winner.1);
            return
        }
    }
}

fn print_board(board: &[[char;3];3]){
    for (r, row) in board.iter().enumerate() {
        if r != 0 { println!("-----"); }
        for (c, var) in row.iter().enumerate() {
            print!("{}",
                if var != &'-'{
                    var.to_string()
                } else {
                    (r * 3 + c).to_string()
                }
            );
            if c != 2 { print!("|"); }
        }
        println!();
    }
}

fn check_winner(board: &[[char;3];3]) -> (bool, char) {
    for row in board {  // 3 in a row
        if row[0] != '-' && row[0] == row[1] && row[0] == row[2]{
            return (true, row[0])
        }
    }
    for col in 0..3{  // 3 in a col
        if board[0][col] != '-' && board[0][col] == board[1][col] && board[0][col] == board[2][col] {
            return (true, board[0][col])
        }
    }
    for i in 0..2 { // 3 in a diagonal 
        if board[1][1] != '-' && board[0][2*i] == board[1][1] && board[1][1] == board[2][2-2*i] {
            return (true, board[0][0])
        }
    }
    (false, '-')
}
