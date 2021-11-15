
//TODO                  ░▓▓███████▓▒░   ▒██░
//                   ▒██▓▒▒▒▒▒▒▒▒▒▓▓█▒▒██████
//                 ███████   ░░░░░░░░▓███░ ███
//                ▒████████▓  ░░░░░░ ███▒▒  ███
//              ░██▒     ████  ░░░░░░██  ▒▓░ █░
//             ░█▓░░░░░░  ░███  ░░░░░   ▒██▓▒
//            ░█▓░░░░░░░░░  ███ ░░░░░  ██████▒
//            █▓░ ░░░░░░░░░  ███ ░░░  ███ ▒███▒
//           ▓▓░░░░░░░░░░░░░  ██ ░░░ ▒██    ██▓▒
//          ▒█▒░░░░░░░░░░░░░░   ░░░░ ██     ███▓
//          █▓ ░░░░░░░░░░░░░░░░░░░░░ ██     ░██▓▓
//         ▒█░░░░░░░      ░░░░░░░░░ ░█▓     ░██░█
//         █▓░░░░░░ █████▒  ░░░░░░░ ▒█░ ███ ░██░█
//        ░█▒░░░░░░ ███████▓  ░░░░░ ▒█▓█████ ██░▓█
//        ▒▓░░░░░░░░   ░▓████  ░░░░ ░███████░██░▒█
//        ▓▒░░░░░░░░░░░   ░███▒ ░░░  ███████▓██░▒█
//        ▓▒░░░░░░░░░░░░░░  ███░░░░░ █████████▒░▒▓
//        █▒░░░░░░░░░░░░░░░  ▒░░░░░░ ░████████░▒▒▓
//        ▓▒░░░░░░░░░░░░░░░░░░░░░░░░░ ███████▒░▒░▓
//        █▒░░░░░░░░░░░░░░░░░░░░░░░░░  ▓████▒░▒▒▒▒
//        █▒░▒░░░░░░░░░░░░░░░░░░░░░░░░░ ░▒▒░░▒▒▒▒▓
//        █▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒▒▒▓
//        █▒░▒░░░░░░░░██ ░░░░░░░░░░░░░░░░▒░▒▒▒▒▒▒▓
//        █▓░▒▒░░░░░░ ██░ ░░░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒█
//        ██░▒▒▒░░░░░ ██▒ ░░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒█
//        ▓█▒░▒▒░░░░░ ▒██ ░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▓█
//        ░█▒░▒▒░▒░░░░ ██▒ ░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▓█
//         ██░▒▒▒▒▒░░░ ░██░ ░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▒█▒
//         ▓█▒░▒▒▒▒▒░░░ ▓██░ ░░░░▒░▒▒▒▒▒▒▒▒▒▒▒░██
//          ██▒▒▒▒▒▒▒░▒░ ███▓ ░░░░▒▒▒▒▒▒░░▒▒▒░▒█▓
//          ▒█▓▒▒▒▒▒▒▒▒▒░ ▓███▓░░░░░░░░░▓█▓▒▒▒██
//           ██▒▒▒▒▒▒▒▒▒▒░░▒█████▓▓▒▓▓█████░▒▓█░
//            ██▒▒▒▒▒▒▒▒▒▒▒░░▒███████████▓░▒▓█▒
//             ██▒▒▒▒▒▒▒▒▒▒▒▒░░░▓█████▓▒░░░▓█▓
//             ░██▓▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░▒░▒██▓
//               ███▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▓██▓
//                ▓███▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒▒███░
//                 ░████▓▒▒▒▒▒▒░▒▒▒▒▓███▓
//                   ░▓██████▓▓███████▒
//                      ░▓█████████▒░

import java.io.*;
import java.util.Scanner;

/***
 * Java in Hebrew
 */

class CheckInput extends Thread
{
    public static Scanner reader = new Scanner(System.in);
    public void run()
    {
        while(true) {
            Process proc = ReadFromFile.getProc();
            BufferedWriter procOut = new BufferedWriter(new OutputStreamWriter(proc.getOutputStream()));
            try {
                procOut.write(reader.next() + "\r");
                procOut.flush();
            } catch (Exception e) {
                // Throwing an exception
                System.out.println("Exception is caught in class CheckInput");
            }
        }
    }
}


public class ReadFromFile {
    static Process proc;
    public static Process getProc(){
        return proc;
    }
    private static String translateWords(String st){
        st  = st.replace("הפשטה","abstract")
                .replace("טען","assert")
                .replace("בוליאני","boolean")
                .replace("שבור","break")
                .replace("ביט","byte")
                .replace("מקרה","case")
                .replace("תפוס","catch")
                .replace("תו","char")
                .replace("כיתה","class")
                .replace("המשך","continue")
                .replace("בררת_מחדל","default")
                .replace("עשה","do")
                .replace("מכפל","double")
                .replace("אחרת","else")
                .replace("סופר","enum")//???
                .replace("אקספורט","exports")
                .replace("מתארך","extends")
                .replace("סופי","final")
                .replace("סופסופ","finally")
                .replace("רחף","float")
                .replace("לכל","for")
                .replace("אם","if")
                .replace("מישם","implements")
                .replace("הכנס","import")
                .replace("דוגמה","instanceof")
                .replace("מס","int")
                .replace("ממשק","interface")
                .replace("ארוך","long")
                .replace("בית","main")
                .replace("מודול","module")
                .replace("מקומי","native")
                .replace("חדש","new")
                .replace("חבילה","package")
                .replace("ציבורי","public")
                .replace("פרטי","private")
                .replace("מוגן","protected")
                .replace("זקוק","requires")
                .replace("החזר","return")
                .replace("קצר","short")
                .replace("סטטי","static")
                .replace("מגבילנצ","strictfp")
                .replace("אדיר","super")
                .replace("החלף","switch")
                .replace("מסונכרן","synchronized")
                .replace("זה","this")
                .replace("זרוק","throw")
                .replace("זורק","throws")
                .replace("זמני","transient")
                .replace("נסה","try")
                .replace("משתנה","var")
                .replace("כלום","void")
                .replace("נדיף","volatile")
                .replace("ככלש","while")


                .replace("אמת","true")
                .replace("שקר","false")


                .replace("int_הבא","nextInt")
                .replace("הבא","next")
                .replace("char_במיקום","charAt")
                .replace("גווה","java")
                .replace("יוטיל","util")
                .replace("מתמטיקה","Math")
                .replace("רנדומלי","random")
                .replace("מערכת","System")
                .replace("חוץ","out")
                .replace("הדפס_שורה","println")
                .replace("הדפס","print")
                .replace("מחרוזת","String")
                .replace("פרמ","args")
                .replace("סורק","Scanner")
                .replace("פנימה","in")
                .replace("פורמט","format")
                .replace("ערךשל","valueOf");
        return st;
    }
    private static String translateLetters(String st){
        st =  st.replace("פ","p")
                .replace("ם","o")
                .replace("ן","i")
                .replace("ו","u")
                .replace("ט","y")
                .replace("א","t")
                .replace("ר","r")
                .replace("ק","e")
                .replace("ף","w")
                .replace("ך","q")
                .replace("ל","l")
                .replace("ח","k")
                .replace("י","j")
                .replace("ע","h")
                .replace("כ","g")
                .replace("ג","f")
                .replace("ד","d")
                .replace("ש","s")
                .replace("ץ","a")
                .replace("ת","m")
                .replace("צ","n")
                .replace("מ","b")
                .replace("נ","v")
                .replace("ה","c")
                .replace("ב","x")
                .replace("ס","z")
                .replace("ז","Z");
        return st;
    }

    public static void main(String args[]) {
        int counter=0;
        boolean doTranslate=true;
        boolean switchDoTranslate=false;
        String fileName=translateLetters(args[0])+ ".java";
        try {
            proc = Runtime.getRuntime().exec("C:\\Program Files (x86)\\Java\\jdk-13.0.1\\bin\\java.exe -cp D:\\Aharon\\code " + fileName);
        }catch (IOException e) {
            System.out.println("Couldn't set proc!!!!!!!!!");
        }
        try {
            FileReader fr = new FileReader(args[0]);
            BufferedReader reader = new BufferedReader(fr);

            FileWriter fw = new FileWriter(fileName);
            BufferedWriter writer = new BufferedWriter(fw);

            String line = reader.readLine();
            String result="";
            int from=0;
            while (line != null) {
                from=0;
                counter=0;
                while(counter<line.length()) {
                    for (int i = from; i < line.length(); i++) {
                        counter++;
                        if (line.charAt(i) == '"') {
                            switchDoTranslate=true;
                            break;
                        }

                    }
                    if(doTranslate) {
                        result +=translateLetters(translateWords(line.substring(from, counter)));
                    }else{
                        result+=line.substring(from, counter);
                    }
                    from=counter;
                    if(switchDoTranslate) {
                        doTranslate = !doTranslate;
                        switchDoTranslate=false;
                    }
                }
                writer.write(result);
                writer.newLine();
                line = reader.readLine();
                result="";
            }
            System.out.println("done reading the file.");
            writer.close();
            fw.close();
        } catch (Exception e) {
            System.out.println("Ugh barf I'm dying!");
            System.out.println(e.getMessage());
            System.out.println(e.getStackTrace());
            System.exit(-1);
        }

        try {
            Process proc =  Runtime.getRuntime().exec("javac " + fileName);
            BufferedReader procIn = new BufferedReader(new InputStreamReader(proc.getInputStream()));


            String line = procIn.readLine();
            while (line != null) {
                System.out.println(line);
                line = procIn.readLine();
            }

            procIn = new BufferedReader(new InputStreamReader(proc.getErrorStream()));
            line = procIn.readLine();
            while (line != null) {
                System.out.println("Got this from running program (Err): " + line);
                line = procIn.readLine();
            }

        } catch (IOException e) {
            System.out.println("Error compiling: " + e.getMessage());
            e.printStackTrace();
        }
        try {
            BufferedReader procIn = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            BufferedWriter procOut = new BufferedWriter(new OutputStreamWriter(proc.getOutputStream()));

            CheckInput object = new CheckInput();
            object.start();

            String line = procIn.readLine();
            while (line != null) {
                System.out.println(line);
                line = procIn.readLine();
            }

            procIn = new BufferedReader(new InputStreamReader(proc.getErrorStream()));
            line = procIn.readLine();
            while (line != null) {
                System.out.println("2Got this from running program (Err): " + line);
                line = procIn.readLine();
            }
        }catch (IOException e) {
            System.out.println("Error running: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
