using System;
using System.Collections.Generic;
using System.Linq;
using LLEnumer = System.Collections.Generic.LinkedList<ReCharTypes>.Enumerator;
using StrStrDict = System.Collections.Generic.Dictionary<string, string>;


public record Char(char ch, bool isEscaped);


public class RegxExmplGenerator {
    public static Random rnd = new Random();
    
    static readonly Dictionary<char, TypeOfGroup> charToGroupType = new(){
        {':', TypeOfGroup.NonCapturing},
        {'=', TypeOfGroup.LookAhead},
        {'!', TypeOfGroup.NegativeLookAhead},
    };
    static void Main(string[] args){      
        // Console.WriteLine("input regex: ");
        // var pat = Console.ReadLine();
        var pat = "";
        // Console.WriteLine("\n--------------------------------");
        var printed = new LinkedList<string>();
        var examples = ConstructExamples(pat);
        // int diff = examples.Count switch{
        //     var x when x < 5 => -1,
        //     var x when x < 10 => 0,
        //     var x when x < 15 => 2,
        //     var x when x < 30 => 3,
        //     _ => 4
        // };
        var examplesRand = examples.OrderBy(x => rnd.Next()).Take(10); 
        foreach(var item in examplesRand) {
            // if(rnd.Next(Diff(printed, item)) > diff){
                printed.AddLast(item);
                Console.WriteLine(item);
            // }
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
        pat = Pattern.PATTERN;
        var parsedEscapes = EscapeChars(pat);
        var parsedRegex = ParseRegex(parsedEscapes);
        parsedRegex = ParseGroups(parsedRegex);
        var examples = new LinkedList<Match>();

        System.Diagnostics.Stopwatch stopwatch = new();
        stopwatch.Start();

        GenerateExmples(parsedRegex.ToArray(), 0, "", examples, new());
        
        stopwatch.Stop();
        Console.WriteLine(stopwatch.ElapsedMilliseconds);

        #region just checking...
            //todo probably not useful...
            HashSet<string> hs = new HashSet<string>(examples.Select(x => x.str));
            if(hs.Count != examples.Count){
                Console.WriteLine($"Useful");
            }
        #endregion
        
        return new LinkedList<string>(examples.Select(x => x.str));
    }

    const string LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        NUMBERS = "0123456789", NUM_LETTER = NUMBERS + LETTERS + "_", SPACES = " \t\n";
    
    static char[] AllCharsInEscapeSeq(char chr){
        var options = chr switch{
            'd' or 'D' => NUMBERS,
            'w' or 'W' => NUM_LETTER,
            's' or 'S' => SPACES,
            _ =>  throw new Exception("Unrecognized letter for group")
        };
        
        if(char.IsLower(chr)){  return options.ToCharArray(); } 

        return Not(options);
    }
    public static char[] Not(string options){
        return Enumerable.Range(32, 126 - 31)
            .Append((int)'\t').Append((int)'\n')
            .Where(x => !options.Contains((char) x))
            .Select(x => (char)x)
            .ToArray();
    }

    static LinkedList<Char> EscapeChars(string pattern){
        var res = new LinkedList<Char>();
        var isEscaped = false;
        foreach(var c in pattern) {
            if(c == '\\' && !isEscaped){
                isEscaped = true;
                continue;
            }
            res.AddLast(new Char(c, isEscaped));
            isEscaped = false;
        }
        return res;
    }
    static LinkedList<ReCharTypes> ParseRegex(LinkedList<Char> pattern){
        var parsed = new LinkedList<ReCharTypes>();
        Func<Char, bool> IsDotAll = chr => chr is Char {isEscaped: false, ch: '.'} && !IsInSquareGroup(parsed);
        var pointer = pattern.First;
        while(pointer != null){
            var chr = pointer.Value;
            pointer = pointer.Next;

            if(IsDotAll(chr)){
                AddAllChars(parsed, Not(""));
            } 
            
            else if(chr.isEscaped){
                if("dwsDWS".Contains(chr.ch)){
                    AddAllChars(parsed, AllCharsInEscapeSeq(chr.ch));
                } else if(NUMBERS.Contains(chr.ch)){
                    parsed.AddLast(new BackReference(NUMBERS.IndexOf(chr.ch)));
                } else if(chr.ch == 'k'){
                    parsed.AddLast(new BackReference());
                } else {
                    AddChar(parsed, chr);
                }
            } 

            else if(IsInSquareGroup(parsed)){
                if(chr.ch == ']')   {  parsed.Last.Value.EndEdit().SetOpen(false); } 
                else                {  AddChar(parsed, chr); }
            } 

            else if(parsed.Last?.Value is BackReference{isNamed: true, IsOpen: true} refGroup){
                if(chr.ch == '<'){}
                else if(chr.ch == '>'){ 
                    refGroup.SetOpen(false).EndEdit(); 
                }
                else { refGroup.AddLetter(chr.ch); }
            } 

            else if(parsed.Last?.Value is PlaceHolder {groupType: TypeOfGroup.Named, IsOpen: true} namedGroup){
                if(chr.ch == '>')   {  namedGroup.SetOpen(false); } 
                else                {  namedGroup.name += chr.ch; }
            } 

            else {
                switch (chr.ch) {
                    case '?':
                        pointer = QuestionMark(parsed, pointer);
                        break;
                    case '+':
                        parsed.Last.Value.SetMany(true);
                        break;
                    case '*':
                        parsed.Last.Value.SetOptional(true).SetMany(true);
                        break;
                    case '[':
                        parsed.AddLast(new SquaredBracketsGroup());
                        break;
                    case '(':   
                        parsed.AddLast(new PlaceHolder(PlaceHolderType.OpenCircleBracket));
                        break;
                    case ')':
                        parsed.AddLast(new PlaceHolder(PlaceHolderType.CloseCircleBracket));
                        break;
                    case '|':
                        parsed.AddLast(new PlaceHolder(PlaceHolderType.Pipe));
                        break;
                    case '{': 
                        parsed.AddLast(new CurlyBracketsGroup());  
                        break;
                    case '}':   
                        if(parsed.Last.Value is CurlyBracketsGroup last){
                            last.EndEdit().SetOpen(false);
                        } else {    AddChar(parsed, chr); }
                        break;
                    case '0' or '1' or '2' or '3' or '4' or '5' or '6' or '7' or '8' or '9':
                        if(parsed.Last.Value is BackReference group){
                            group.AddDigit(NUMBERS.IndexOf(chr.ch));
                        } else {    AddChar(parsed, chr); }
                        break;
                    default:
                        AddChar(parsed, chr);
                        break;
                }
            }
        }
        return parsed;
    }

    private static LinkedListNode<Char> QuestionMark(LinkedList<ReCharTypes> parsed, LinkedListNode<Char> pointer){
        if (parsed.Last.Value is PlaceHolder { type: PlaceHolderType.OpenCircleBracket } openGroup){
            var next = pointer.Value.ch;
            if (charToGroupType.TryGetValue(next, out TypeOfGroup typ)){
                openGroup.groupType = typ;
                return pointer.Next;
            } else if (next == '<') {
                openGroup.groupType = pointer.Next.Value.ch switch {
                    '=' => TypeOfGroup.LookBehind,
                    '!' => TypeOfGroup.NegativeLookBehind,
                    _ => TypeOfGroup.Named,
                };
                if (openGroup.groupType == TypeOfGroup.Named){
                    openGroup.name += pointer.Next.Value.ch;
                }
                return pointer.Next.Next;
            }
            throw new Exception("Unrecognizeg type of group");
        }
        if(!parsed.Last.Value.IsMany){ //? if its not char(+?) [lazy]
            parsed.Last.Value.SetOptional(true);
        }
        return pointer;
    }

    static LinkedList<ReCharTypes> ParseGroups(LinkedList<ReCharTypes> parsedRegex){
        var res = new LinkedList<ReCharTypes>();
        var enumer = parsedRegex.GetEnumerator();
        while(enumer.MoveNext()) {
            if(enumer.Current is PlaceHolder {type: PlaceHolderType.OpenCircleBracket}){
                (var group, enumer) = GetCircleBracketsGroup(enumer);
                res.AddLast(group);
            } else {
                res.AddLast(enumer.Current);
            }
        }
        return res;
    }

    static (CircleBracketsGroup group, LLEnumer enumer) GetCircleBracketsGroup(LLEnumer enumer){
        var ph = enumer.Current as PlaceHolder;
        var group = new CircleBracketsGroup()
            .ChangeName(ph.name)
            .ChangeGroupType(ph.groupType);

        while(enumer.MoveNext()){
            if(enumer.Current is PlaceHolder {type: PlaceHolderType.OpenCircleBracket} placeHolder){
                (var newGroup, enumer) = GetCircleBracketsGroup(enumer);
                group.Add(newGroup);
            } else if(enumer.Current is PlaceHolder {type: PlaceHolderType.CloseCircleBracket}){
                group.SetMany(enumer.Current.IsMany);
                group.SetOptional(enumer.Current.IsOptional);
                return (group, enumer);
            } else {
                group.Add(enumer.Current);
            }
        }
        throw new Exception("Unclosed () group");
    }

    private static void AddAllChars(LinkedList<ReCharTypes> parsed, char[] allChars){
        var last = IsInSquareGroup(parsed) ? null : parsed.AddLast(new SquaredBracketsGroup());
        foreach (var c in allChars){    AddChar(parsed, new Char(c, false), true); }
        last?.Value.EndEdit().SetOpen(false);
    }
    private static void AddChar(LinkedList<ReCharTypes> parsed, Char chr, bool? inSquareGroup=null){
        inSquareGroup ??= IsInSquareGroup(parsed);
        if ((bool) inSquareGroup || IsInCurlyGroup(parsed)) {
            parsed.Last.Value.Add(chr);
        } else {
            parsed.AddLast(new SimpleChar(chr));
        }
    }
    static bool IsInSquareGroup(LinkedList<ReCharTypes> list){
        return list.Last?.Value is SquaredBracketsGroup last && last.IsOpen;
    }
    static bool IsInCurlyGroup(LinkedList<ReCharTypes> list){
        return list.Last?.Value is CurlyBracketsGroup last && last.IsOpen;
    }

    public static void GenerateExmples(
            ReCharTypes[] parsedRegex, int index, string example, 
            LinkedList<Match> result, StrStrDict groups //!  , Lookahead? lookahead=null
    ){
        var matchedSoFar = new Match(example, groups);
        if (index >= parsedRegex.Length){
            result.AddLast(matchedSoFar);
            return;
        }
        var thisChar = parsedRegex[index];
        if (thisChar.IsOptional){
            GenerateExmples(parsedRegex, index + 1, example, result, groups);
        }

        CurlyBracketsGroup curlyGroup = null;
        CircleBracketsGroup circleGroup = null;
        if (thisChar is CurlyBracketsGroup group1) { curlyGroup = group1; }
        else if (thisChar is CircleBracketsGroup group2) { circleGroup = group2; }
        bool isCurlyGroup = curlyGroup is not null;
        bool isCircleGgroup = circleGroup is not null;
        
        int varietyToTry = thisChar.MaxExampleOptions();
        string[] matches = null;
        Match[] matchesAndGroups = null;
        bool alreadyCalculatedMatches = false;
        if(varietyToTry != -1){
            CalculateMatches(parsedRegex, index, matchedSoFar, thisChar, curlyGroup, circleGroup, isCurlyGroup, isCircleGgroup, ref matches, ref matchesAndGroups);
            alreadyCalculatedMatches = true;
        }
        if (varietyToTry == -1 || varietyToTry > Pattern.VARIETY || thisChar.IsMany){  
            varietyToTry = Pattern.VARIETY; 
        }

        var differentPossibilities = new LinkedList<Match>();
        for (int variety = 0; variety < varietyToTry; variety++){
            if(!alreadyCalculatedMatches){
                //? the number of possible matches is unknownly big so instead it'll just  
                //? generate a new batch of VARIETY examples each time it loops
                CalculateMatches(parsedRegex, index, matchedSoFar, thisChar, curlyGroup, circleGroup, isCurlyGroup, isCircleGgroup, ref matches, ref matchesAndGroups);
            }
            int amountOfRepete = thisChar.IsMany ? rnd.Next(1, Pattern.VARIETY) : 1;
            Match newExample = new();
            newExample.groups = new();
            for (int repete = 0; repete < amountOfRepete; repete++){
                if (matches is null){
                    var ex = matchesAndGroups[rnd.Next(matchesAndGroups.Length)];
                    newExample.str += ex.str;
                    JoinDicts(newExample.groups, ex.groups);
                } else {
                    newExample.str += matches[rnd.Next(matches.Length)];
                }
            }
            AddIfNotIn(differentPossibilities, newExample);
        }
        foreach (var possibility in differentPossibilities){
            var groupsCopy = groups;
            if (thisChar is CircleBracketsGroup group){
                groupsCopy = CopyDict(possibility.groups);
                groupsCopy[group.GroupNumber ?? "-1"] = possibility.str;
                groupsCopy[group.GroupName ?? "-1"] = possibility.str;
            }
            GenerateExmples(parsedRegex, index + 1, example + possibility.str, result, groupsCopy);
        }
    }


    private static void CalculateMatches(
            ReCharTypes[] parsedRegex, int index, Match matchedSoFar, ReCharTypes thisChar, 
            CurlyBracketsGroup curlyGroup, CircleBracketsGroup circleGroup, bool isCurlyGroup, 
            bool isCircleGgroup, ref string[] matches, ref Match[] matchesAndGroups
    ){
        if (isCurlyGroup){
            matchesAndGroups = GetCurlyBracketsMatch(parsedRegex, index, curlyGroup, matchedSoFar);
        } else if (isCircleGgroup){
            matchesAndGroups = circleGroup.GetExampleMatchGroups(matchedSoFar);
        } else {
            matches = thisChar.GetExampleMatch(matchedSoFar);
        }
    }

    private static void AddIfNotIn(LinkedList<Match> ll, Match match){
        foreach (var item in ll){
            if (match.str.Equals(item.str) && CompareDicts(item.groups, match.groups)){
                return;
            }
        }
        ll.AddLast(match);
    }

    private static bool CompareDicts(StrStrDict dict1, StrStrDict dict2){     
        if(dict1.Count != dict2.Count){ return false; }
        foreach(var set in dict1) {
            if(!dict2.TryGetValue(set.Key, out string val) || val != set.Value){
                return false;
            }
        }
        return true;
    }

    private static void JoinDicts(StrStrDict dict1, StrStrDict dict2){
        foreach(var item in dict2) {
            if(!dict1.ContainsKey(item.Key)){
                dict1[item.Key] = item.Value;
            }
        }
    }
    private static StrStrDict CopyDict(StrStrDict dict){
        var res = new StrStrDict();
        if(dict is null){   return res; }
        foreach(var set in dict) {  res[set.Key] = set.Value; }
        return res;
    }
    private static Match[] GetCurlyBracketsMatch(ReCharTypes[] parsedRegex, int index, CurlyBracketsGroup bracketGroup, Match matchedSoFar){
        var examples = new HashSet<Match>();
        for (int i = 0; i < 10; i++){
            var example = new Match();
            example.groups = new();
            int amountOfRepete = bracketGroup.GetExampleAmountOfMatch()-1; //? minus 1 cuz already matched once
            var prev = parsedRegex[index - 1];
            for (int j = 0; j < amountOfRepete; j++){
                if(prev is CircleBracketsGroup group){
                    var matchesAndGroups = group.GetExampleMatchGroups(matchedSoFar);
                    var match = matchesAndGroups[rnd.Next(matchesAndGroups.Length)];
                    example.str += match.str;
                    JoinDicts(example.groups, match.groups);
                } else {
                    var possibleMatches = prev.GetExampleMatch(matchedSoFar);
                    example.str += possibleMatches[rnd.Next(possibleMatches.Length)];
                }
            }
            examples.Add(example);
        }
        return examples.ToArray();
    }
}
