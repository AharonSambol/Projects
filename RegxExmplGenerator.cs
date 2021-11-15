using System;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Linq;

static class LevenshteinDistance{
    public static int Compute(string s, string t){
        int n = s.Length;
        int m = t.Length;
        int[,] d = new int[n + 1, m + 1];

        // Step 1
        if (n == 0){    return m; }
        if (m == 0){    return n; }

        // Step 2
        for (int i = 0; i <= n; d[i, 0] = i++){}
        for (int j = 0; j <= m; d[0, j] = j++){}

        // Step 3
        for (int i = 1; i <= n; i++){
            //Step 4
            for (int j = 1; j <= m; j++){
                // Step 5
                int cost = (t[j - 1] == s[i - 1]) ? 0 : 1;
                // Step 6
                d[i, j] = Math.Min(
                    Math.Min(d[i - 1, j] + 1, d[i, j - 1] + 1),
                    d[i - 1, j - 1] + cost);
            }
        }
        // Step 7
        return d[n, m];
    }
}
public class RegxExmplGenerator {
    static Random rnd = new Random();
    const int VARIETY = 5;
    const string SLASH = "\\\\";
    static readonly Regex rangesRX = new Regex($"(?<!{ SLASH })-", RegexOptions.Compiled);
    static void Main(string[] args){
        Console.WriteLine("input regex: ");
        var pat = Console.ReadLine();
        Console.WriteLine("\n--------------------------------");
        var printed = new LinkedList<string>();
        var examples = ConstructExamples(pat);
        int diff = examples.Count switch{
            var x when x < 5 => -1,
            var x when x < 10 => 0,
            var x when x < 15 => 2,
            var x when x < 30 => 3,
            _ => 4
        };
        foreach(var item in examples) {
            if(rnd.Next(Diff(printed, item)) > diff){
                printed.AddLast(item);
                Console.WriteLine(item);
            }
        }
    }
    static int Diff(LinkedList<string> printed, string st){
        if(printed.Count == 0){ return int.MaxValue; }
        int min = LevenshteinDistance.Compute(printed.First.Value, st);
        foreach(var item in printed) {
            min = Math.Min(min, LevenshteinDistance.Compute(item, st));
        }
        return min;
    }

    private static LinkedList<string> ConstructExamples(string pat){
        // var pat = "\\w+@(gmail|yahoo)\\.(com|org)";
        // pat = "[+-]?\\d+(\\.\\d+e?)?";
        // pat = "\\d+(\\.\\d)?";
        
        var examples = GetExamples(pat.ToCharArray(), "", 0, false, new LinkedList<string>());
        var ans = new LinkedList<string>();
        HashSet<string> hs = new HashSet<string>();
        foreach (var item in examples){
            if (hs.Contains(item)) { continue;  }
            hs.Add(item);
            ans.AddLast(item);
        }
        return ans;
    }
    static int CalcDiff(string str1, string str2){
        //todo
        return 0;
    }

    const int ANY = 0, W = 1, D = 2, S = 3;
    const string LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        NUMBERS = "0123456789", NUM_LETTER = NUMBERS + LETTERS + "_", SPACES = " \t\n";
    static char GetRandomChar(int type) => type switch{ //todo add more
        ANY =>  (char)rnd.Next(32, 126),
        W => NUM_LETTER[rnd.Next(NUM_LETTER.Length)],
        D => NUMBERS[rnd.Next(NUMBERS.Length)],
        S => SPACES[rnd.Next(SPACES.Length)],
        _ => throw new Exception()
    };

    static LinkedList<string> GetExamples(char[] pattern, /*StringBuilder*/ string currentEx, int index, bool escape, LinkedList<string> ll){
        if(index == pattern.Length){
            ll.AddLast(currentEx);
            return ll;
        }
        var c = pattern[index];
        int amount;
        string newSt;
        if(IsOptional(pattern, index, escape) && c != '\\' ){
            int amountToSkip = 1;
            if(c == '(' || c == '['){
                int open = 1;
                while(open > 0){
                    amountToSkip+=1;
                    if      (pattern[index+amountToSkip-1] == '\\'){ continue; } //todo unless index-2 is \\ and index-3 isnt....
                    if      (pattern[index+amountToSkip] == '(' || pattern[index+amountToSkip] == '['){ open++; }
                    else if (pattern[index+amountToSkip] == ')' || pattern[index+amountToSkip] == ']'){ open--; }
                }
            }
            GetExamples(pattern, currentEx, index+amountToSkip, false, ll);
        }
        if(escape){
            for (int i=0; i < VARIETY; i++) {
                amount = IsMultiple(pattern, index, escape) ? rnd.Next(1, 10) : 1;
                newSt = currentEx;
                for (int j=0; j < amount; j++) {
                    newSt += c switch{
                        'w' => GetRandomChar(W),
                        'd' => GetRandomChar(D),
                        's' => GetRandomChar(S),
                        _ => c
                    };
                    // if(IsMultiple(pattern, index, escape) && j > 0 && j < amount-1 && rnd.Next(4) == 2){
                    //     GetExamples(pattern, newSt, index+1, false, ll);
                    // }
                }
                GetExamples(pattern, newSt, index+1, false, ll);
                if(!NUM_LETTER.Contains(c)){
                    break; //? no need for variety when its just a normal char (cuz will get same res each time)
                }
            }
            return ll;
        }
        int origIndex;
        StringBuilder options;
        switch(c){
            case '\\':  case ')': case '?': case '*': case '+': case ']': break; 
            case '(':
                origIndex = index;
                options = new StringBuilder();
                int open = 1;
                while(open > 0){
                    index += 1;
                    options.Append(pattern[index]);
                    if (pattern[index-1] == '\\')   { continue; } //todo unless index-2 is \\ and index-3 isnt....
                    open += pattern[index] == '(' ? 1 : pattern[index] == ')' ? -1 : 0;
                } options.Length--;
                
                var optionsArr = options.ToString().Split('|');
                if(optionsArr.Length == 1){    index = origIndex; break; }
               
                for (int i=0; i < Math.Min(VARIETY, optionsArr.Length); i++){
                    newSt = currentEx;
                    amount = IsMultiple(pattern, origIndex, escape) ? rnd.Next(1, 5) : 1;
                    for (int a = 0; a < amount; a++){
                        int pos = rnd.Next(optionsArr.Length);
                        var option = optionsArr[pos];
                        var resses = GetExamples(option.ToCharArray(), "", 0, false, new LinkedList<string>());

                        newSt += resses.ElementAt(rnd.Next(resses.Count));
                    }
                    GetExamples(pattern, newSt, index + 1, false, ll);
                }
                return ll;
            case '[':  
                origIndex = index;
                options = new StringBuilder();
                while(true){
                    index += 1;
                    options.Append(pattern[index]);
                    if (pattern[index-1] == '\\')   { continue; } //todo unless index-2 is \\ and index-3 isnt....
                    if (pattern[index] == ']')      { break;    }
                } options.Length--;
                //todo add used to prevent getting same res twice
                if(options[0] == '^'){
                    //todo todo todo todo todo todo todo todo todo todo todo todo todo
                }
                var ranges = rangesRX.Split(options.ToString());
                if(ranges.Length > 1){
                    //todo todo todo todo todo todo todo todo todo todo todo todo todo
                }
                for (int v=0; v < VARIETY; v++) {
                    newSt = currentEx;
                    var opt = options.ToString(); 
                    amount = IsMultiple(pattern, origIndex, escape) ? rnd.Next(1, 5) : 1;
                    for (int i=0; i < amount; i++) {
                        int r = rnd.Next(opt.Length);
                        newSt += opt[r];
                    }
                    GetExamples(pattern, newSt, index+1, false, ll);
                }
                return ll;
            case '.':
                for (int i = 0; i < VARIETY; i++){
                    amount = IsMultiple(pattern, index, escape) ? rnd.Next(1, 10) : 1;
                    newSt = currentEx;
                    for (int j=0; j < amount; j++) {
                        newSt += GetRandomChar(ANY);
                    }
                    GetExamples(pattern, newSt, index+1, false, ll);
                } return ll;
            default:
                if(IsMultiple(pattern, index, escape)){
                    for (int i = 0; i < VARIETY; i++){
                        newSt = currentEx + new string(c, rnd.Next(1, 10)); //? repeats c rnd amount of times
                        GetExamples(pattern, newSt, index+1, false, ll);
                    } break;
                }
                GetExamples(pattern, currentEx + c, index+1, false, ll);
                return ll;
        }
        return GetExamples(pattern, currentEx, index+1, c=='\\', ll);
    }

    static bool IsOptional(char[] pattern, int index, bool escaped){
        if(pattern[index] == ')' || pattern[index] == ']'){
            return false;
        }
        if(!escaped && pattern[index] == '(' || pattern[index] == '['){
            int open = 1;
            while(open > 0){
                index+=1;
                if      (pattern[index-1] == '\\'){ continue; } //todo unless index-2 is \\ and index-3 isnt....
                if      (pattern[index] == '(' || pattern[index] == '['){ open++; }
                else if (pattern[index] == ')' || pattern[index] == ']'){ open--; }
            }
        }
        return index+1 < pattern.Length && (pattern[index+1] == '?' || pattern[index+1] == '*');
    }
    static bool IsMultiple(char[] pattern, int index, bool escaped){
        if(pattern[index] == ')' || pattern[index] == ']'){
            return false;
        }
        if(!escaped && pattern[index] == '(' || pattern[index] == '['){
            int open = 1;
            while(open > 0){
                index+=1;
                if      (pattern[index-1] == '\\'){ continue; } //todo unless index-2 is \\ and index-3 isnt....
                if      (pattern[index] == '(' || pattern[index] == '['){ open++; }
                else if (pattern[index] == ')' || pattern[index] == ']'){ open--; }
            }
        }
        return index+1 < pattern.Length && (pattern[index+1] == '+' || pattern[index+1] == '*');
    }
}