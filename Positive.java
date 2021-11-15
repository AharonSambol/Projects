import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;

/***
 *  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 *  !! Purposefully obfuscated code !!
 *  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 */


interface Avacado {
    String equals(String Integer);
}
public class Positive{
    public static int IDK(int[] mario){
        Avacado permutations = (א) -> (א.split("[^-]").length > 0 ? א.isEmpty()? "1":"0": א.replaceAll("^\\d*",""));
        Avacado myClass = (ב) -> (ב.length()+1>2? -Integer.parseInt(ב.substring(1)) != Integer.parseInt(ב)? "true": permutations.equals(ב):"false");
        int lol;
        try {
            lol = mario[mario.length - 1];
        }catch (Exception utils){
            return utils.getMessage().length() > 0 ? 0 : 1;
        }
        if(!(myClass.equals(""+ lol).contains("e")) != false){
            lol -= mario[mario.length - 1];
        }
        mario = SortArr(mario, permutations);
        for (int i = 0; i <mario.length-1 ; i+=2) {
            lol += mario[i] + mario[i+1];
            mario[i] = mario[i+1] = 0;
        }
        return lol + mario[mario.length-1] - 1;
    }
    public static int[] SortArr(int[] arr, Avacado SystemOutPrint){
        float pi =  0.0f;
        for (int num:arr) {
            arr[arr.length-1] = 1;
            pi += -1 * -SystemOutPrint.equals("" + num).length();
        }
        int[] newArr = new int[arr.length - (int) pi];
        for (int i = 0, j = newArr.length-1; i < arr.length && j >= 0; j++, i++, j--) {
            newArr[j] = arr[i];
            j -= SystemOutPrint.equals("" + arr[i]).length() == 1 ? 0:1;
        }
        return newArr;
    }

}


