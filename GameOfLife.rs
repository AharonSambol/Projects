use std::collections::HashMap;
use std::{thread, time};


fn main() {
    let mut cells = HashMap::new();
    for piece in [(0, 0), (0, 1), (0, 2), (1, -1), (1, 0), (1, 1)]{
        cells.insert(piece, true);
    }
    while cells.len() > 0 {
        print_board(&cells);
        thread::sleep(time::Duration::from_millis(1000));
        cells = grow(cells);
    }
}

fn grow(cells: HashMap<(i32, i32), bool>) -> HashMap<(i32, i32), bool> {
    let mut cells_with_neighbors = HashMap::new();
    let mut new_cells = HashMap::new();
    for (key, _) in &cells {
        for row in -1..=1 {
            for col in -1..=1 {
                if row == col && row == 0 {
                    continue;
                }
                let neighbor = (key.0 + row, key.1 + col);
                cells_with_neighbors.insert(neighbor, cells.contains_key(&neighbor));
            }
        }
    }
    for (key, is_allive) in &cells_with_neighbors {
        let neighbors = count_neighbors(&cells, &key);
        if *is_allive {
            if neighbors == 2 || neighbors == 3 {
                new_cells.insert(*key, true);
            }
        } else {
            if neighbors == 3 {
                new_cells.insert(*key, true);
            }
        }
    }
    new_cells
}

fn count_neighbors(cells: &HashMap<(i32, i32), bool>, pos: &(i32, i32)) -> u16 {
    let mut count = 0;
    for row in -1..=1 {
        for col in -1..=1 {
            if row == col && row == 0 {
                continue;
            }
            if cells.contains_key(&(pos.0 + row, pos.1 + col)){
                count += 1
            }
        }
    }
    count
}

fn print_board(cells: &HashMap<(i32, i32), bool>){
    let first = cells.keys().next().unwrap();
    let (mut min_c, mut min_r, mut max_r, mut max_c) = (first.1, first.0, first.0, first.1);
    for key in cells.keys(){
        min_c = min_c.min(key.1);
        min_r = min_r.min(key.0);
        max_c = max_c.max(key.1);
        max_r = max_r.max(key.0);
    }
  
    for row in min_r..=max_r{
        for col in min_c..=max_c{
            print!("{}", if cells.contains_key(&(row, col)) { "ם" } else { " " })
        }
        println!()
    }

    println!("\n");
    for _ in 0..=max_c-min_c{     print!("-"); }
    println!("\n");
}
