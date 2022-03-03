using System;
using System.Linq;
using System.Collections.Generic;

public record struct Match(string str, Dictionary<string, string> groups);
public abstract class BasicImplGroup : ReCharTypes{
    protected bool isOptional = false;
    public bool IsOptional => isOptional;
    public virtual ReCharTypes SetOptional(bool val) {
        isOptional = val;
        return this;
    }
    protected bool isMany = false;
    public bool IsMany => isMany;
    public virtual ReCharTypes SetMany(bool val) {
        isMany = val;
        return this;
    }
    protected bool isOpen = true;
    public bool IsOpen => isOpen;
    public virtual ReCharTypes SetOpen(bool val) {
        isOpen = val;
        return this;
    }
    protected string chr;
    
    public abstract ReCharTypes Add(Char chr);
    public abstract string[] GetExampleMatch(Match matchedSoFar);

    public virtual ReCharTypes EndEdit() => this;
    public virtual int MaxExampleOptions() => -1; 
}

public class SimpleChar : BasicImplGroup {
    public SimpleChar(Char chr) => this.chr = chr.ch.ToString();
    public override string[] GetExampleMatch(Match matchedSoFar) => new string[]{ chr };
    public override ReCharTypes Add(Char ignore) => 
        throw new Exception("Can't add to simple char");

    public override int MaxExampleOptions() => 1;
}

public class SquaredBracketsGroup : BasicImplGroup {
    private LinkedList<Char> ipt;
    private string[] chrs;
    public SquaredBracketsGroup() {
        ipt = new();
    }
    public override ReCharTypes EndEdit(){
        var options = ipt.ToArray();
        var pos = 0;
        var not = false;
        if(options[0].ch == '^'){
            not = true;
            pos++;
        }
        var parsedOptions = new LinkedList<char>();
        int skip = 0;
        for (int i=pos; i < options.Length; i++) {
            var opt = options[i];
            if(skip>0){ skip--; continue; }
            if(i + 2 < options.Length){
                if(options[i + 1] is Char{ch: '-', isEscaped: false}){
                    for (int j = (int)opt.ch; j <= (int)options[i+2].ch; j++) {
                        parsedOptions.AddLast((char)j);
                    }
                    skip = 2;
                    continue;
                }
            }
            parsedOptions.AddLast(opt.ch);
        }

        if(not){
            this.chrs = RegxExmplGenerator.Not(
                String.Join("", parsedOptions)
            ).Select(x => x.ToString()).ToArray();
        } else {
            this.chrs = parsedOptions.Select(x => x.ToString()).ToArray();
        }
        return this;
    }
    public override string[] GetExampleMatch(Match matchedSoFar){
        var amount = Pattern.VARIETY;
        if(amount >= chrs.Length){  return chrs; }
        var res = new string[amount];
        var indexes = Enumerable.Range(0, chrs.Length).ToList();
        var rand = RegxExmplGenerator.rnd;
        for (int i=0; i < amount; i++) {
            var indx = indexes.ElementAt(rand.Next(indexes.Count));
            indexes.Remove(indx);
            res[i] = chrs[indx];
        }
        return res;
    }

    public override ReCharTypes Add(Char c) {
        ipt.AddLast(c);
        return this;
    }
    public override int MaxExampleOptions() => chrs.Length;
}

public class CurlyBracketsGroup : BasicImplGroup {
    private LinkedList<Char> ipt;
    public (int start, int? end) range; 
    public CurlyBracketsGroup() {
        ipt = new();
    }
    public override ReCharTypes EndEdit(){
        var cur = ipt.First;
        var temp = "";
        while(cur != null && cur.Value.ch != ','){
            temp += cur.Value.ch;
            cur = cur.Next;
        }
        range.start = int.Parse(temp);
        if(cur == null){    return this; }
        temp = "";
        cur = cur.Next; //? skip the ','
        while(cur != null){
            temp += cur.Value.ch;
            cur = cur.Next;
        }
        range.end = temp.Equals("") ? 20 : int.Parse(temp); //? 20 is just a big number
        return this;
    }
    public override ReCharTypes SetMany(bool val) => throw new Exception("Can't make {} many");
    public override ReCharTypes SetOptional(bool val) => this;
    public override string[] GetExampleMatch(Match matchedSoFar) =>
        throw new Exception("isn't supposed to match anything");
    public int GetExampleAmountOfMatch() {
        if(range.end is null){  return range.start; }
        return RegxExmplGenerator.rnd.Next(range.start, (int)range.end + 1);
    }
    
    public override ReCharTypes Add(Char c) {
        ipt.AddLast(c);
        return this;
    }
}

public class PlaceHolder : BasicImplGroup {
    public PlaceHolderType type {get; init;}
    public TypeOfGroup groupType = TypeOfGroup.Normal;
    public string name;
    public PlaceHolder(PlaceHolderType type) => this.type = type;
    public override ReCharTypes Add(Char c) => 
        throw new Exception("Can't add to PlaceHolder");
    public override string[] GetExampleMatch(Match matchedSoFar) =>
        throw new Exception("PlaceHolder doesn't have example match");

}

public class BackReference : BasicImplGroup {
    private int? number; private string name; //? one or the other
    public bool isNamed = false;
    public BackReference(int num) {
        number = num;
        name = number.ToString();
    }
    public BackReference() => isNamed = true;
    public BackReference AddDigit(int digit){
        number = (int)(number ?? 0) * 10 + digit;
        name = number.ToString(); 
        return this;
    }
    public BackReference AddLetter(char ch){ 
        name += ch;
        return this;
    }
    public override BackReference Add(Char c) => 
        throw new Exception("Can't add to RefrenceToCapturingGroup");

    public override string[] GetExampleMatch(Match matchedSoFar) { 
        return new string[]{ matchedSoFar.groups[name] };
    }
    public override int MaxExampleOptions() => 1;
}

public class CircleBracketsGroup : BasicImplGroup {
    private static int amountOfGroups = 1;
    private int groupNumber;
    private string groupName; 
    public string GroupNumber => groupNumber.ToString(); 
    public string GroupName => groupName; 
    private TypeOfGroup groupType;
    public TypeOfGroup GroupType => groupType;
    private LinkedList<LinkedList<ReCharTypes>> ipt;
    public CircleBracketsGroup() {
        groupNumber = amountOfGroups;
        amountOfGroups++;
        ipt = new();
        ipt.AddFirst(new LinkedList<ReCharTypes>());
    }
    public override string[] GetExampleMatch(Match matchedSoFar) =>
        throw new Exception("using incorect function please use GetExamplesMatchGroups");
    
    public Match[] GetExampleMatchGroups(Match matchedSoFar){
        var res = new LinkedList<Match>();
        foreach(var item in ipt) {        
            RegxExmplGenerator.GenerateExmples(item.ToArray(), 0, "", res, matchedSoFar.groups);
        }
        return res.ToArray();
    }
    public void Add(ReCharTypes c) {
        if(c is PlaceHolder {type: PlaceHolderType.Pipe}){
            ipt.AddLast(new LinkedList<ReCharTypes>());
        } else {
            ipt.Last.Value.AddLast(c);
        }
    }

    public CircleBracketsGroup ChangeGroupType(TypeOfGroup type){
        groupType = type;
        if(type != TypeOfGroup.Normal && type != TypeOfGroup.Named){
            amountOfGroups--;
            groupNumber = -1;
        }
        return this;
    }
    public CircleBracketsGroup ChangeName(string name){
        groupName = name;
        return this;
    }
    public override CircleBracketsGroup Add(Char c) => this;
}


