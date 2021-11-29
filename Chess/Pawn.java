package Chess;

import java.util.LinkedList;

public class Pawn extends Piece{
    public Pawn(int row, int col, Color color){
        super(row, col, color);
        this.img = (color.equals(Color.black) ? '♟' : '♙');
    }
    public LinkedList<Pos> getPossibleDestinations(Piece[][] board){
        var posses = new LinkedList<Pos>();
        int dir = getColor().equals(Color.black) ? 1 : -1;
        Pos forward = new Pos(getRow() + dir , getCol());
        if(isEmptyPos(forward, board)){
            posses.add(forward);
            if(getRow() == (getColor().equals(Color.black) ? 1 : 6)) { //if at starting pos
                Pos forward2 = new Pos(getRow() + dir * 2, getCol());
                if (isEmptyPos(forward2, board)) {
                    posses.add(forward2);
                }
            }
        }
        for(int side: new int[]{-1, 1}){
            Pos pos = new Pos(getRow()+dir, getCol()+side);
            if(isInRange(pos, board)){
                var pieceAtPos = board[pos.getRow()][pos.getCol()];
                if(pieceAtPos != null && !pieceAtPos.getColor().equals(getColor())){
                    posses.add(pos);
                }
            }
        }
        return posses;
    }

}
