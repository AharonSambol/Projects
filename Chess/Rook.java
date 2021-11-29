package Chess;

import java.util.LinkedList;

public class Rook extends Piece{
    public Rook(int row, int col, Color color){
        super(row, col, color);
        this.img = (color.equals(Color.black) ? '♜' : '♖');
    }
    public LinkedList<Pos> getPossibleDestinations(Piece[][] board){
        var posses = new LinkedList<Pos>();
        getPosses(board, pos, color, posses);
        return posses;
    }
    public static void getPosses(Piece[][] board, Pos curPos, Color color, LinkedList<Pos> posses){
        checkDir(board, posses, 1, 0, curPos, color);
        checkDir(board, posses, -1, 0, curPos, color);
        checkDir(board, posses, 0, 1, curPos, color);
        checkDir(board, posses, 0, -1, curPos, color);
    }
    public static void checkDir(
            Piece[][] board, LinkedList<Pos> posses, int rowChange, int colChange, Pos curPos, Color color){
        for(int i = 1;; i++){
            Pos pos = new Pos(curPos.getRow() + rowChange * i, curPos.getCol() + colChange * i);
            if (isEmptyPos(pos, board)) { posses.add(pos); }
            else {
                if (isValidPos(pos, board, color)) { posses.add(pos); } // capture
                break;
            }
        }
    }
}
