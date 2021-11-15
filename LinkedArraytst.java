import java.lang.reflect.Array;
import java.util.*;
class Cell <T> {
    int len;
    T[] arr;
    public Cell(T[] arr,int len){
        this.arr=arr;
        this.len=len;
    }
}
class Pos {
    int one;
    int two;
    public Pos(int one,int two){
        this.one=one;
        this.two=two;
    }
}
class LinkedArray <T> /* implements List <T> */ {

    LinkedList<Cell> linkedList;
    Class<T> c;
    int pos=-1;

    public LinkedArray(Class<T> c) {
        this.c=c;
        linkedList =new LinkedList<Cell>();
    }

    Object get(int i) {
        if (i>pos){
            throw new IndexOutOfBoundsException("Index out of bounds");
        }else {
            Pos p=getPos(i);
            return linkedList.get(p.one).arr[p.two];
        }
    }

    private Pos getPos(int i){
        int count=0;
        int ans1=0;
        int ans2=0;
        while(i>count){
            count+=linkedList.get(ans1).len;
            if(i>count){
                ans2+=count;
                ans1++;
            }else{
                ans2=i-ans2;
            }
        }
        return new Pos(ans1,ans2);
    }

    boolean isEmpty(){
        return pos==-1;
    }

    void add(T val){
        pos++;
        if(pos%100==0){
            @SuppressWarnings("unchecked")
            final T[] a = (T[]) Array.newInstance(c, 100);
            Cell cl= new Cell(a,100);
            linkedList.add(cl);
        }
        Pos p=getPos(pos);
        linkedList.get(p.one).arr[p.two]=val;
    }

    void addAt(T val,int index){
        Pos p=getPos(index);
        Object[] arr=linkedList.get(p.one).arr;
        Object[] newArr=new Object[linkedList.get(p.one).len+1];
        for (int j = 0, k = 0; j < arr.length; j++) {
            if (j == index) {
                newArr[j]=val;
            }
            newArr[j] = arr[k++];
        }
    }

    int size(){
        return pos;
    }

    Object getLast(){
        Pos p=getPos(pos);
        return linkedList.get(p.one).arr[p.two];
    }

    Object getFirst(){
        return linkedList.getFirst().arr[0];
    }

    boolean contains(T val){
        for(Cell arr:linkedList){
            for(Object v:arr.arr){
                if(v==val){ return true; }
            }
        }
        return false;
    }

    Object[] toArray(){
        @SuppressWarnings("unchecked")
        final Object[] result = (T[]) Array.newInstance(c, pos+1);
        int count=0;
        for(Cell arr:linkedList){
            for(Object v:arr.arr){
                if(v==null){return result;}
                result[count]=v;
                count++;
            }
        }
        return result;
    }

    T[] toArray(T[] a){
        @SuppressWarnings("unchecked")
        int count=0;
        for(Cell arr:linkedList){
            for(Object v:arr.arr){
                if(v==null){return a;}
                a[count]= ((T) v);
                count++;
            }
        }
        return a;
    }

    void removeAt(int i){
        Pos p=getPos(i);
        Object[] arr=linkedList.get(p.one).arr;
        Object[] newArr=new Object[linkedList.get(p.one).len-1];
        for (int j = 0, k = 0; j < arr.length; j++) {
            if (j == i) {
                continue;
            }
            newArr[k++] = arr[j];
        }
        Cell c=new Cell(newArr,newArr.length);
        linkedList.get(p.one).arr=newArr;
        linkedList.get(p.one).len=newArr.length;
    }

    void remove(Object o){
        int p=indexOf(o);
        Object[] arr=linkedList.get(p).arr;
        Object[] newArr=new Object[linkedList.get(p).len-1];
        for (int j = 0, k = 0; j < arr.length; j++) {
            if (j == p) {
                continue;
            }
            newArr[k++] = arr[j];
        }
        Cell c=new Cell(newArr,newArr.length);
        linkedList.get(p).arr=newArr;
        linkedList.get(p).len=newArr.length;
    }

    int indexOf(Object o){
        int count=0;
        for (Cell arr:linkedList){
            for (Object x:arr.arr){
                if(x==o){
                    return count;
                }
                count++;
            }
        }
        return -1;
    }
//    boolean equals(Object o){
//        return o.equals(linkedList);
//    }

}
public class LinkedArraytst{

    public static void main(String[] args) {
        ArrayList<Integer> x=new ArrayList<>();
        //x.
        LinkedArray<String> a= new LinkedArray<String>(String.class);
        System.out.println(a.isEmpty());
        a.add("aha!");
        a.add("lol");
        System.out.println("# "+a.indexOf("lolp"));
        System.out.println(a.isEmpty());
        System.out.println(a.get(0)+" "+a.get(1));
        System.out.println(a.size());
        System.out.println(a.contains("lol"));
        System.out.println(a.contains("boo"));
        Object[] s=a.toArray();
        System.out.println(s.length);
        a.removeAt(0);
        System.out.println(a.get(0));
    }
}
