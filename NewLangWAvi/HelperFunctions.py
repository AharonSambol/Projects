import re

from Tree import Tree
from Tokens import *

extension_class = "__BUILT_in_Extensions__"
loop_var_name = 10000

const_to_const = {
    Tokens.BOOL_CONSTANT: ParsedTokens.BOOL,
    Tokens.STR_CONSTANT: ParsedTokens.STR,
    Tokens.FLOAT_CONSTANT: ParsedTokens.FLOAT,
    Tokens.INT_CONSTANT: ParsedTokens.INT,
    Tokens.NULL_CONSTANT: ParsedTokens.NULL,
}
token_to_symbol = {
    ParsedTokens.MODULO: '%',
    ParsedTokens.MULTIPLICATION: '*',
    ParsedTokens.DIVISION: '/',
    ParsedTokens.ADDITION: '+',
    ParsedTokens.SUBTRACTION: '-',
    ParsedTokens.BOOL_OR: '||',
    ParsedTokens.BOOL_AND: '&&',
    ParsedTokens.BOOL_EQ: '==',
    ParsedTokens.BOOL_NEQ: '!=',
    ParsedTokens.BOOL_SEQ: '<=',
    ParsedTokens.BOOL_LEQ: '>=',
    ParsedTokens.BOOL_S: '<',
    ParsedTokens.BOOL_L: '>',
    ParsedTokens.BOOL_NOT: '!',
}
symbol_to_token = {
    '+': ParsedTokens.ADDITION,
    '-': ParsedTokens.SUBTRACTION,
    '*': ParsedTokens.MULTIPLICATION,
    '/': ParsedTokens.DIVISION,
    '/-/': ParsedTokens.FLOOR_DIVISION,
    '/+/': ParsedTokens.CEILING_DIVISION,
    '^': ParsedTokens.POW,
    '%': ParsedTokens.MODULO,
    'or': ParsedTokens.BOOL_OR,
    'xor': ParsedTokens.XOR,
    'and': ParsedTokens.BOOL_AND,
    'nand': ParsedTokens.NAND,
    '==': ParsedTokens.BOOL_EQ,
    '!=': ParsedTokens.BOOL_NEQ,
    '<=': ParsedTokens.BOOL_SEQ,
    '>=': ParsedTokens.BOOL_LEQ,
    '<': ParsedTokens.BOOL_S,
    '>': ParsedTokens.BOOL_L,
    'not': ParsedTokens.BOOL_NOT,
    'in': ParsedTokens.BOOL_IN,
}


def move_up_tree_while(node, func):
    while node.parent and func(node):
        node = node.parent
    return node


def get_precedence(token):
    if token is None:
        return 0
    match token.type:
        case ParsedTokens.MODULO | ParsedTokens.MULTIPLICATION | ParsedTokens.DIVISION | \
             ParsedTokens.CEILING_DIVISION | ParsedTokens.FLOOR_DIVISION:
            return 60
        case ParsedTokens.ADDITION | ParsedTokens.SUBTRACTION:
            return 50
        case ParsedTokens.PARENTHESES:
            return 5
        case ParsedTokens.POW:
            return 70
        case ParsedTokens.BOOL_OR | ParsedTokens.XOR:
            return 11
        case ParsedTokens.BOOL_AND | ParsedTokens.NAND:
            return 10
        case ParsedTokens.BOOL_NOT:
            return 99
        case ParsedTokens.BOOL_IN | ParsedTokens.NEGATIVE | ParsedTokens.INDEX | ParsedTokens.DOT | \
                ParsedTokens.PLUS_PLUS:
            return 100
        case ParsedTokens.BOOL_EQ | ParsedTokens.BOOL_NEQ:
            return 20
        case ParsedTokens.BOOL_SEQ | ParsedTokens.BOOL_LEQ | ParsedTokens.BOOL_S | ParsedTokens.BOOL_L:
            return 30
        case ParsedTokens.DOT | ParsedTokens.UNKNOWN:
            return 200
        case _:
            return 1


def make_function(node):
    func_node = Tree(Token(ParsedTokens.FUNCTION, node.value.name), None)
    child = node.children.pop(-1)
    node = node.parent
    if node.value.type == ParsedTokens.UNKNOWN:
        return_types = ", ".join(get_return_types(node))
        func_node.children.append(Tree(Token(ParsedTokens.TYPE, return_types.strip()), func_node))
        node = node.parent
    func_node.parent = node
    node.children[-1] = func_node

    func_node.children.append(child)
    child.parent = func_node
    node = func_node
    return node


def get_return_types(node):
    res = []
    parent = node.parent
    for i, val in enumerate(parent.children):
        if val is node:
            j = i
            while j >= 0 and parent.children[j].value.type != ParsedTokens.NEW_LINE:
                res.insert(0, parent.children[j].value.name)
                j -= 1
            return res


def add_new(node, token, typ):
    new_node = Tree(Token(typ, token.name), node)
    node.children.append(new_node)
    node = new_node
    return node


def move_to_comma_pos(node):
    stop_at = {ParsedTokens.LIST, ParsedTokens.LIST_COMPREHENSION, ParsedTokens.INDEX, ParsedTokens.PARENTHESES,
               ParsedTokens.PROGRAM, ParsedTokens.FOR_LOOP, ParsedTokens.DICT, ParsedTokens.SET}
    node = move_up_tree_while(node, lambda n: n.value.type not in stop_at)
    return node


def cast_type(st):
    st = re.sub(r'\bstr\b', str_class, st)
    while '[]' in st:
        st = re.sub(r'([^\s]+?)\[]', list_class + r'<\1>', st, 1)
    return st


dependencies = {
    "System.Linq",
    "System",
    "System.Collections.Generic",
    "System.Collections",
    "System.Text",
}  # todo add at top of file

# todo check that not in code
list_class = "__MyListWrapper__"
str_class = "__MyStrWrapper__"

extension_methods = [
    "public static bool Contains<T, G>(this Dictionary<T, G> dict, T key) => dict.ContainsKey(key);",
    f"public static bool Any<T>({list_class}<T> lst) => lst.Any();",
    f"public static bool All<T>({list_class}<T> lst) => !lst.Any((x) => x.Equals(default(T)));"
    """public static IEnumerable<(int, T)> Enumerate<T>(IEnumerable<T> input, int start = 0){
        int i = start;
        foreach (var t in input){ yield return (i++, t); }
    }""",
    """public static IEnumerable<(T, T)> Zip<T>(IEnumerable<T> arr1, IEnumerable<T> arr2){
        return arr1.Zip(arr2);
    }""",
    """public static (bool isSuccessful, T res) ShortTryFunction<T>(Func<T> func){
        try{    return(true, func()); } 
        catch (System.Exception) {  return(false, default);}
    }""",
    """public static (bool isSuccessful, Nothing res) ShortTryFunction(Action func){
        try{ func(); return (true, new Nothing()); } 
        catch (System.Exception) {  return (false, new Nothing());}
    }""",
    "public struct Nothing {}",
    """public static T ShortTryFunctionNull<T>(Func<T> func){
        try{    return func(); } 
        catch (System.Exception) {  return default;}
    }""",
    """public static T TryGetArr<T>(this __MyListWrapper__<T> arr, int index, T def=default){
        if(arr == null){    return def; }
        if(index >= 0 && index < arr.len){
            return arr[index];
        } return def;
    }""",
    """public static T Cast<T>(Nullable<T> val) where T: struct {
        if(val.HasValue){   return (T) val; }
        throw new InvalidCastException();
    }""",
    """public static T Cast<T>(Nullable<T> val, T def) where T: struct {
        if(val.HasValue){   return (T) val; }
        return def;
    }""",
    """public static ref T DoVoidAndReturn<T>(ref T val, Action func){
        func();
        return ref val;
    }""",
    '''public static bool ToBool(__MyStrWrapper__ val){
        return !(val == null) && val.ToString() != null && val.ToString() != "";
    }''',
    'public static bool ToBool(int val) => val != 0;',
    'public static bool ToBool(float val) => val != 0f;',
    'public static bool ToBool(bool val) => val;',
    'public static bool ToBool<T>(__MyListWrapper__<T> val) => val != null && val.len != 0;',
    'public static bool ToBool<T>(T val) => !val.Equals(default(T));"',
]


built_in_classes = [
    f"""public class {list_class}<T> : IEnumerable<T> {{
        public T this[int key] {{
            get => List[key];
            set => List[key] = value;
        }}
        public {list_class}(List<T> lst) {{ List = lst; }}
        public {list_class}() {{ List = new List<T>(); }}
        private List<T> List;
        public static implicit operator {list_class}<T>(List<T> lst) {{
            return new {list_class}<T>(lst);
        }}
        public int len => List.Count;
        
        public static bool operator ==({list_class}<T> lst1, {list_class}<T> lst2) {{
            if(lst1 is null || lst2 is null){{ return lst1 is null && lst2 is null;}}
            return lst1.Equals(lst2);
        }}    
    
        public static bool operator !=({list_class}<T> lst1, {list_class}<T> lst2) => !(lst1 == lst2);
        public override bool Equals(object obj){{
            if(obj is {list_class}<T> other_lst){{
                if(len != other_lst.len){{   return false; }}
                for (int i=0; i < len; i++) {{
                    if(!List[i].Equals(other_lst[i])){{
                        return false;
                    }}
                }}
                return true;
            }} return false;
        }}
        public override int GetHashCode() => List.GetHashCode();
        public static {list_class}<T> operator +({list_class}<T> lst1, {list_class}<T> lst2) {{
            return new {list_class}<T>(lst1.List.Concat(lst2.List).ToList());
        }}
        public static {list_class}<T> operator +({list_class}<T> lst, dynamic num) {{ 
            if(lst.len == 0){{
                return new List<T>(); 
            }}
            var res = new List<T>();
            for (int i=0; i < lst.len; i++) {{
                res.Add(lst[i] + num);
            }}
            return res;
        }}
        public static {list_class}<T> operator *({list_class}<T> lst, int num) {{ 
            var res = new List<T>();
            for (int i=0; i < lst.len; i++) {{
                dynamic a = lst[i];
                dynamic b = num;
                res.Add((T) (a * num));
            }}
            return new {list_class}<T>(res);
        }}

        public IEnumerator<T> GetEnumerator() => List.GetEnumerator();
        IEnumerator IEnumerable.GetEnumerator() => this.GetEnumerator();
        public bool HasIndex(int i) => i >= 0 && i < List.Count;
        public void Sort() => List.Sort();
        public void Add(T item) => List.Add(item);
        public void Extend({list_class}<T> lst){{
            List = List.Concat(lst.List).ToList();
        }}
        public T Pop(int i){{
            var res = List[i];
            List.RemoveAt(i);
            return res;
        }}
        public void Insert(int pos, T item) => List.Insert(pos, item);
        public {list_class}<T> Copy(){{
            var newList = new List<T>();
            foreach(var item in List) {{
                newList.Add(item);
            }}
            return new {list_class}<T>(newList);
        }}
        public int Index(T obj) => List.IndexOf(obj);
        public void Remove(T val) => List.Remove(val);
        public void Reverse() => List.Reverse();
        public int BinarySearch(T val) => List.BinarySearch(val);
        //todo convert
        public string Join(string sep){{
            var res = new StringBuilder();
            foreach(var item in List) {{
                res.Append(item).Append(sep);
            }}
            res.Length -= sep.Length;
            return res.ToString();
        }}
        public override string ToString() => "[" + Join(", ") + "]";
    }}""",

    f"""public class {str_class}{{  // todo remove
    public {str_class} this[int key]{{
        get{{
            if (key < 0 || key >= InternalStr.Length){{
                throw new IndexOutOfRangeException("Index out of bounds of string");
            }}
            return new {str_class}(InternalStr[key]);
        }} set {{
            lastToList = null;
            if (key < 0 || key >= InternalStr.Length) {{
                throw new IndexOutOfRangeException("Index out of bounds of string");
            }}
            InternalStr = new StringBuilder(InternalStr.Substring(0, key))
            .Append(value)
            .Append(InternalStr.Substring(key + 1, InternalStr.Length - (key + 1))).ToString();
        }}
    }}
    public {str_class}(string str) {{ InternalStr = str; }}
    public {str_class}(char str) {{ InternalStr = str.ToString(); }}
    public {str_class}(StringBuilder str) {{ InternalStr = str.ToString(); }}
    private string InternalStr;
    private {list_class}<{str_class}> lastToList;

    public override string ToString(){{
        return InternalStr;
    }}
    public static implicit operator {str_class}(string st){{
        return new {str_class}(st);
    }}
    public static implicit operator string({str_class} st){{
        if(st is null){{ return null; }}
        return st.InternalStr;
    }}
    public int len => InternalStr.Length;
    
    public static bool operator ==({str_class} st1, {str_class} st2){{
        if(st1 is null || st2 is null){{ return st1 is null && st2 is null; }}
        return st1.InternalStr.Equals(st2.InternalStr);
    }}
    public static bool operator !=({str_class} st1, {str_class} st2) => !(st1 == st2);

    public override bool Equals(object st2){{
        if (st2 is {str_class} st){{
            return InternalStr.Equals(st.InternalStr);
        }}
        return false;
    }}
    public override int GetHashCode() => InternalStr.GetHashCode();
    public static {str_class} operator +({str_class} st1, {str_class} st2){{
        return new {str_class}(st1.InternalStr + st2.InternalStr);
    }}
    public static {str_class} operator *({str_class} st, int num){{
        var res = new StringBuilder();
        for (int i = 0; i < num; i++){{
            res.Append(st);
        }}
        return new {str_class}(res.ToString());
    }}
    public IEnumerator<{str_class}> GetEnumerator(){{
        return ToList().GetEnumerator();
    }}
    public {list_class}<{str_class}> ToList(){{
        if (lastToList is null){{
            var res = new {list_class}<{str_class}>();
            foreach (var ch in InternalStr.ToCharArray()){{
                res.Add(new {str_class}(ch));
            }}
            lastToList = res;
        }}
        return lastToList.Copy();
    }}
    public void Append(string st){{
        lastToList = null;
        InternalStr += st;
    }}

    public bool EndsWith(string st) => InternalStr.EndsWith(st);
    public bool StartsWith(string st) => InternalStr.StartsWith(st);
    #region strip
    public {str_class} Strip() => InternalStr.Trim();
    public {str_class} StripEnd() => InternalStr.TrimEnd();
    public {str_class} StripStart() => InternalStr.TrimStart();
    public {str_class} StripStart(string st){{
        var res = InternalStr;
        while (res.StartsWith(st)){{
            res = res.Substring(st.Length);
        }}
        return res;
    }}
    public {str_class} StripEnd(string st){{
        var res = InternalStr;
        while (res.EndsWith(st)){{
            res = res.Substring(0, res.Length - st.Length);
        }}
        return res;
    }}
    public {str_class} Strip(string st) {{
        var res = InternalStr;
        while (res.StartsWith(st)){{
            res = res.Substring(st.Length);
        }}
        while (res.EndsWith(st)){{
            res = res.Substring(0, res.Length - st.Length);
        }}
        return res;
    }}
    public {str_class} StripEnd({list_class}<string> lst){{
        var res = InternalStr;
        restart:
        foreach (string item in lst){{
            if (res.EndsWith(item)){{
                res = res.Substring(0, res.Length - item.Length);
                goto restart;
            }}
        }}
        return res;
    }}
    public {str_class} StripStart({list_class}<string> lst){{
        var res = InternalStr;
        restart:
        foreach (string item in lst){{
            if (res.StartsWith(item)){{
                res = res.Substring(item.Length);
                goto restart;
            }}
        }}
        return res;
    }}
    public {str_class} Strip({list_class}<string> lst){{
        var res = InternalStr;
        restart:
        foreach (string item in lst){{
            if (res.StartsWith(item)){{
                res = res.Substring(item.Length);
                goto restart;
            }}
        }}
        restart2:
        foreach (string item in lst){{
            if (res.EndsWith(item)){{
                res = res.Substring(0, res.Length - item.Length);
                goto restart2;
            }}
        }}
        return res;
    }}
    #endregion

    public {list_class}<{str_class}> Split(){{
        var res = InternalStr.Split().ToList();
        var lst = new {list_class}<{str_class}>();
        foreach (var item in res) {{ lst.Add(item); }}
        return lst;
    }}
    public {list_class}<{str_class}> Split({str_class} st){{
        var res = InternalStr.Split(new string[] {{ st.InternalStr }}, StringSplitOptions.None).ToList();
        var lst = new {list_class}<{str_class}>();
        foreach (var item in res) {{ lst.Add(item); }}
        return lst;
    }}
    public {list_class}<{str_class}> Split({list_class}<{str_class}> strings){{
        var seps = new string[strings.len];
        for (int i = 0; i < seps.Length; i++){{
            seps[i] = strings[i];
        }}
        var res = InternalStr.Split(seps, StringSplitOptions.None).ToList();
        var lst = new {list_class}<{str_class}>();
        foreach (var item in res) {{ lst.Add(item); }}
        return lst;
    }}
    public {str_class} Replace({str_class} orig, {str_class} newStr){{
        return InternalStr.Replace(orig, newStr);
    }}

    public int Find({str_class} st) => InternalStr.IndexOf(st);
    public bool Contains({str_class} st) => InternalStr.Contains(st);
    public {str_class} ToUpper() => InternalStr.ToUpper();
    public {str_class} ToLower() => InternalStr.ToLower();
    public int Count({str_class} st) => Split(st).len - 1;
}}"""
]
