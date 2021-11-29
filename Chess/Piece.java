package Chess;

import java.util.LinkedList;

public abstract class Piece {
    Color color;
    Pos pos;
    char img;
    public Piece(int row, int col, Color color){
        pos = new Pos(row, col);
        this.color = color;
    }
    public Color getColor(){    return color; }
    public int getRow(){    return pos.getRow(); }
    public int getCol(){    return pos.getCol(); }
    public char getImg(){  return img; }
    public abstract LinkedList<Pos> getPossibleDestinations(Piece[][] board);
    public boolean move(Pos pos, Piece[][] board){
        if(!contains(getPossibleDestinations(board), pos)){ return false; }
        Chess.board[this.pos.getRow()][this.pos.getCol()] = null;
        this.pos = pos;
        if(Chess.board[pos.getRow()][pos.getCol()] != null){
            Chess.board[pos.getRow()][pos.getCol()].onDestroy();
        }
        Chess.board[pos.getRow()][pos.getCol()] = this;
        return true;
    }
    public void onDestroy(){
        if (color.equals(Color.black))  {  Chess.blackPieces.remove(this); }
        else                            {  Chess.whitePieces.remove(this); }
    }
    public static boolean isValidPos(Pos pos, Piece[][] board, Color color){
        if(!isInRange(pos, board)){ return false; }
        var pieceAtPos = board[pos.getRow()][pos.getCol()];
        return pieceAtPos == null || !pieceAtPos.getColor().equals(color);
    }
    public static boolean isEmptyPos(Pos pos, Piece[][] board){
        if(!isInRange(pos, board)){ return false; }
        return board[pos.getRow()][pos.getCol()] == null;
    }
    public static boolean isInRange(Pos pos, Piece[][] board){
        return pos.getCol() >= 0 && pos.getCol() < board.length && pos.getRow() >= 0 && pos.getRow() < board.length;
    }
    private static boolean contains(LinkedList<Pos> ll, Pos val){
        for(Pos pos : ll){
            if(pos.getRow() == val.getRow() && pos.getCol() == val.getCol()){   return true; }
        } return false;
    }
}
