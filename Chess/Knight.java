package Chess;

import java.util.LinkedList;

public class Knight extends Piece{
    public Knight(int row, int col, Color color){
        super(row, col, color);
        this.img = (color.equals(Color.black) ? '♞' : '♘');
    }
    public LinkedList<Pos> getPossibleDestinations(Piece[][] board){
        var posses = new LinkedList<Pos>();
        for(int row : new int[]{-2, 2}){
            for(int col : new int[]{-1, 1}){
                for(Pos pos : new Pos[]{
                        new Pos(getRow() + row, getCol() + col),
                        new Pos(getRow() + col, getCol() +row)}
                ) {
                    if (isValidPos(pos, board, this.getColor())) {
                        posses.add(pos);
                    }
                }
            }
        }
        return posses;
    }
}
