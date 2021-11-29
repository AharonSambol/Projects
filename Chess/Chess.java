package Chess;

import javax.swing.*;
import java.awt.*;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.Random;
import java.util.concurrent.TimeUnit;

public class Chess extends JFrame {
    public static Piece[][] board;
    public static LinkedList<Piece> blackPieces, whitePieces;
    Random rand;
    static JLabel jLabel;
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
        JFrame window = new JFrame("Chess");
        window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        window.setLayout(new BorderLayout());
        jLabel = new JLabel(boardToStr());
        window.add(jLabel, BorderLayout.CENTER);
        window.pack();
        window.setVisible(true);
        window.setLocationRelativeTo(null);
    }


    private String boardToStr(){
        StringBuilder sb = new StringBuilder("<html><br><br>|");
        for (Piece[] pieces : board) {
            for (Piece piece : pieces) {
                sb.append(piece == null ? "\u2007\u2007" : piece.getImg()).append('|');
            }
            sb.append("<br>-------------------------------<br>|");
        }
        sb.deleteCharAt(sb.length()-1);
        sb.append("</html>");
        return sb.toString();
    }
    private Piece findPiece(Color color){
        var pieces = color.equals(Color.black) ? blackPieces : whitePieces;
        Piece piece;
        do {
            piece = pieces.get(rand.nextInt(pieces.size()));
        } while (piece.getPossibleDestinations(board).size() == 0);
        return piece;
    }

    public static void main(String[] args) throws InterruptedException {
        var game = new Chess();
        game.rand = new Random();
        game.initialSetup();
        var turn = Color.black;
        while(true) {
            jLabel.setText(game.boardToStr());
            var piece = game.findPiece(turn);
            var dests = piece.getPossibleDestinations(board);
            var randomDest = dests.get(game.rand.nextInt(dests.size()));
            piece.move(randomDest);
            turn = turn.equals(Color.black) ? Color.white : Color.black;
            TimeUnit.SECONDS.sleep(1);
        }
    }
}
