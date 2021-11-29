package Chess;

import java.util.Arrays;
import java.util.LinkedList;
import java.util.Random;
import java.util.concurrent.TimeUnit;

public class Chess {
    public static Piece[][] board;
    public static LinkedList<Piece> blackPieces, whitePieces;
    Random rand;
    public void initialSetup(){
        blackPieces = new LinkedList<>();
        whitePieces = new LinkedList<>();
        board = new Piece[8][8];
        for (var color : new Color[]{Color.black, Color.white}) {
            var piecesList = color.equals(Color.black) ? blackPieces : whitePieces;
            int row = color.equals(Color.black) ? 0 : 7;
            board[row][0] = new Rook(row, 0, color);
            board[row][7] = new Rook(row, 7, color);
            board[row][1] = new Knight(row, 1, color);
            board[row][6] = new Knight(row, 6, color);
            board[row][2] = new Bishop(row, 2, color);
            board[row][5] = new Bishop(row, 5, color);
            board[row][3] = new Queen(row, 3, color);
            board[row][4] = new King(row, 4, color);
            piecesList.addAll(Arrays.asList(board[row]));
            row = row == 0 ? 1 : 6;
            for (int col = 0; col < board[0].length; col++) {
                board[row][col] = new Pawn(row, col, color);
            }
            piecesList.addAll(Arrays.asList(board[row]));
        }
    }


    private void displayBoard(){
        StringBuilder sb = new StringBuilder("\n\n|");
        for (Piece[] pieces : board) {
            for (Piece piece : pieces) {
                sb.append(piece == null ? "\u2007\u2009\u2009" : piece.getImg()).append('|');
            }
            sb.append("\n----------------------\n|");
        }
        sb.deleteCharAt(sb.length()-1);
        System.out.println(sb);
    }

}
