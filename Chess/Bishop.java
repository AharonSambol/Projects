package Chess;

import java.util.LinkedList;

public class Bishop extends Piece{
    public Bishop(int row, int col, Color color){
        super(row, col, color);
        this.img = (color.equals(Color.black) ? '♝' : '♗');
    }
    public LinkedList<Pos> getPossibleDestinations(Piece[][] board){
        var posses = new LinkedList<Pos>();
        getPosses(board, pos, color, posses);
        return posses;
    }
    public static void getPosses(Piece[][] board, Pos curPos, Color color, LinkedList<Pos> posses){
        Rook.checkDir(board, posses, 1, 1, curPos, color);
        Rook.checkDir(board, posses, -1, 1, curPos, color);
        Rook.checkDir(board, posses, 1, -1, curPos, color);
        Rook.checkDir(board, posses, -1, -1, curPos, color);
    }
}
