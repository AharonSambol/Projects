package Chess;

import java.util.LinkedList;

public class King extends Piece{
    public King(int row, int col, Color color){
        super(row, col, color);
        this.img = (color.equals(Color.black) ? '♚' : '♔');
    }
    public LinkedList<Pos> getPossibleDestinations(Piece[][] board){
        var posses = new LinkedList<Pos>();
        for (int row = -1; row <= 1; row++) {
            for (int col = -1; col <= 1; col++) {
                if(row == 0 && col == 0){   continue; }
                var pos = new Pos(getRow() + row, getCol() + col);
                if(isValidPos(pos, board, this.getColor())){
                    posses.add(pos);
                }
            }
        }
        return posses;
    }
}
