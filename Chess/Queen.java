package Chess;

import java.util.LinkedList;

public class Queen extends Piece{
    public Queen(int row, int col, Color color){
        super(row, col, color);
        this.img = (color.equals(Color.black) ? '♛' : '♕');
    }
    public LinkedList<Pos> getPossibleDestinations(Piece[][] board){
        var posses = new LinkedList<Pos>();
        Rook.getPosses(board, pos, color, posses);
        Bishop.getPosses(board, pos, color, posses);
        return posses;
    }
}
