package kata

func SolveSnafooz(pcs [6][6][6]int) [6][6][6]int {
	var board [6][6][6]int
	_, board = place(board, pcs[0], 0)
	_, ans := solve(pcs, board, []int{1, 2, 3, 4, 5}, 1)
	return generateAns(ans)
}

func solve(pieces [6][6][6]int, board [6][6][6]int, postitions []int, pieceNum int) (bool, [6][6][6]int) {
	if pieceNum == 6 {
		return true, board
	}
	piece := pieces[pieceNum]
	for posPos, posVal := range postitions {
		for j := 0; j < 2; j++ {
			if j == 1 {
				piece = flip(piece)
			}
			for i := 0; i < 4; i++ {
				if i != 0 {
					piece = rotate(piece)
				}
				fits, newBoard := place(board, piece, posVal)

				if fits {
					newPositions := remove(postitions, posPos)
					solved, ans := solve(pieces, newBoard, newPositions, pieceNum+1)
					if solved {
						return true, ans
					}
				}
			}
		}
	}
	return false, board
}

func remove(s []int, i int) []int {
	cpy := make([]int, len(s))
	copy(cpy, s)
	cpy[i] = cpy[len(s)-1]
	return cpy[:len(s)-1]
}

func place(board [6][6][6]int, piece [6][6]int, pos int) (bool, [6][6][6]int) {
	for row := 0; row < 6; row++ {
		for col := 0; col < 6; col++ {
			if piece[row][col] != 0 {
				x, y, z := pieceToPos(row, col, pos)
				if board[z][x][y] != 0 {
					return false, board
				}
				board[z][x][y] = pos + 1
			}
		}
	}
	return true, board
}

func pieceToPos(row int, col int, pos int) (int, int, int) {
	switch pos {
	case 0:
		return row, col, 0
	case 1:
		return 0, col, row
	case 2:
		return col, 0, row
	case 3:
		return row, col, 5
	case 4:
		return 5, col, row
	case 5:
		return col, 5, row
	}
	return -1, -1, -1
}

func generateAns(board [6][6][6]int) [6][6][6]int {
	var ans [6][6][6]int
	posses := []int{2, -1, 3, 1, 6, -1, 5, -1, 4, -1}
	actual := []int{0, -1, 1, 2, 3, -1, 4, -1, 5, -1}
	for len(posses) > 0 {
		for row := 0; row < 6; row++ {
			for tt, pos := range posses {
				if pos == -1 {
					break
				}
				a, b, c := pieceToPos(3, 3, pos-1)
				clr := board[a][b][c]

				for col := 0; col < 6; col++ {
					var x, y, z int
					if pos == 3 { // ? rotate
						x, y, z = pieceToPos(5-col, row, pos-1)
					} else if pos == 6 { // ? flip
						x, y, z = pieceToPos(col, row, pos-1)
					} else if pos == 2 || pos == 4 { //? pivot
						x, y, z = pieceToPos(5-row, col, pos-1)
					} else { //? normal
						x, y, z = pieceToPos(row, col, pos-1)
					}

					if board[x][y][z] == clr {
						ans[actual[tt]][row][col] = 1
					} else {
						ans[actual[tt]][row][col] = 0
					}
				}
			}
		}
		for posses[0] != -1 {
			posses = posses[1:]
			actual = actual[1:]
		}
		posses = posses[1:]
		actual = actual[1:]
	}
	return ans
}

func rotate(piece [6][6]int) [6][6]int {
	var ans [6][6]int
	for row := 0; row < len(piece); row++ {
		for col := 0; col < len(piece); col++ {
			ans[col][len(piece)-1-row] = piece[row][col]
		}
	}
	return ans
}

func flip(piece [6][6]int) [6][6]int {
	var ans [6][6]int
	for row := 0; row < len(piece); row++ {
		for col := 0; col < len(piece); col++ {
			ans[len(piece)-1-row][col] = piece[row][col]
		}
	}
	return ans
}
