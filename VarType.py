import re
import copy

INT = re.compile("-?\\d+")
FLOAT = re.compile("-?\\d+(?:\\.\\d*)?")
STR_CONST = re.compile("\".*?\"")
LIST_CONST = re.compile("\\[.*?\\]")
NUMBER = re.compile("-?\\d+(?:\\.\\d+)?")


class Bool:
    def __init__(self, val):
        if val == "false":
            self.value = False
        elif val == "true":
            self.value = True
        else:
            self.value = bool(val)
        self.attributes = {
            "is?": lambda: self,
            "float": self.to_float,
            "str": self.to_str,
            "int": self.to_int,
        }

    def to_float(self):
        return Float((Int(0) + self).value)

    def to_str(self):
        return String(str(self), {})

    def to_int(self):
        return Int(0) + self

    def __add__(self, other):
        return Bool(False)

    def __sub__(self, other):
        return Bool(False)

    def __mul__(self, other):
        return Bool(False)

    def __truediv__(self, other):
        return Bool(False)

    def __floordiv__(self, other):
        return Bool(False)

    def __len__(self):
        return Bool(False)

    def __pow__(self, power, modulo=None):
        return Bool(False)

    def __eq__(self, other):
        if type(other) != Bool:
            return False    # 5 MAYBE immplement TRUFY? !!!!!!!!!
        return self.value == other.value

    def __str__(self):
        return "true" if self.value else "false"

    def __copy__(self):
        return Bool(self.value)


class String:
    def __init__(self, val, variables, was_str=False):
        self.variables = variables
        if was_str:
            self.value = val
        else:
            self.value = []
            val = str(val)
            st, var = "", ""
            finding_var = False
            for c in val:
                if c == "{":
                    if st:
                        self.value.append(st)
                        st = ""
                    finding_var = True
                elif c == "}":
                    self.value.append([var])
                    var = ""
                    finding_var = False
                elif finding_var:
                    var += c
                else:
                    st += c
            if st:
                self.value.append(st)
        self.functions = {
            "nxtOf": self.next_contain,
            "rem": self.remove_all,
            "remF": self.remove_first,
            "pop": self.remove_at,
            "rep": self.replace,
            "repF": self.replace_first,
            "get": self.get_range,
            "copy": self.__copy__,
            "has": self.has,
            "solidify": self.solidify,
            "CAP": self.to_caps,
            "low": self.to_lower,
            "get_at": self.get_at,
            "change_at": self.change_at,
            "is?": self.is_of_type,
            "reverse": self.reverse,
        }
        self.attributes = {
            "len": self.length,
            "isNum?": self.is_number,
            "isDecNum?": self.is_float,
            "is?": lambda: Bool(len(self) > 0),
            "float": self.to_float,
            "int": self.to_int,
            "bool": self.to_bool,
            "list": self.to_list,
        }

    def to_float(self):
        return Float(str(self))

    def to_int(self):
        return Int(str(self))

    def to_bool(self):
        return Bool(len(self) > 0)

    def to_list(self):
        lst = [x for x in str(self)[1:-1]]
        return List(lst)

    def reverse(self):
        self.value = [self.solidify().value[0][::-1]]
        return self

    def __pow__(self, other, modulo=None):
        return Bool(False)

    def __add__(self, other):
        if type(other) in [Int, Float,
                           List, Bool]:
            new_st = [x for x in self.value]
            new_st.append(str(other))
            new_String = String(None, self.variables, was_str=True)
            new_String.value = new_st
            return new_String
        elif type(other) is String:
            first_val = [x for x in self.value]
            second_val = [x for x in other.value]
            first_val.extend(second_val)
            new_String = String(None, self.variables, was_str=True)
            new_String.value = first_val
            return new_String
        elif type(other) is Bool:
            return self + "true" if other.value else "false"
        return Bool(False)

    def __mul__(self, other):
        if type(other) is Int:
            return String(self.value * other.value, {}, was_str=True)
        if type(other) is Bool:
            return self if other.value else other
        return Bool(False)

    def __truediv__(self, other):
        return Bool(False)

    def __floordiv__(self, other):
        return Bool(False)

    def __sub__(self, other):
        return Bool(False)

    def __str__(self):
        st = ""
        for val in self.value:
            if type(val) is list:
                val = self.variables[val[0]]
                if type(val) is String:
                    val = str(val)[1:-1]
                st += str(val)
            else:
                st += str(val)
        return '\"' + st + '\"'

    def solidify(self):
        self.value = [str(self)[1:-1]]
        return self

    def __len__(self):
        return len(str(self)) - 2

    def length(self):
        return Int(len(self))

    def __eq__(self, other):
        if type(other) != String:
            return False
        return self.value == other.value

    def __lt__(self, other):
        return len(self) < len(other)

    def __le__(self, other):
        return len(self) <= len(other)

    def __gt__(self, other):
        return len(self) > len(other)

    def __ge__(self, other):
        return len(self) >= len(other)

    def __contains__(self, item):
        self_arr = str(self)[1:-1]
        item_len = len(item)
        item_st = str(item)[1:-1]
        for pos in range(len(self_arr) - (item_len - 1)):
            if self_arr[pos: pos + item_len] == item_st:
                return Bool(True)
        return Bool(False)

    def has(self, packed=None):
        return Bool(packed[0] in self)

    def get_at(self, packed=None):
        val = packed[0] if type(packed[0]) in [int, str] else packed[0].value
        if type(val) is str:
            val = int(val[1:])
            st = str(self)[1:-1]
            if val < len(st):
                return String(st[val], self.variables)
            else:
                return Bool(False)
        return String(str(self)[1:-1][val], self.variables)

    def is_of_type(self, packed=None):
        st = packed[0].to_caps().value[0]
        self_val = str(self)[1:-1]
        try:
            if st == 'INT':
                _ = Int(self_val)
            elif st == 'FLOAT':
                _ = Float(self_val)
            elif st == 'BOOL':
                if self_val != 'true' and self_val != 'false':
                    raise Exception
            elif st == 'STRING':
                pass
            else:
                raise Exception
            return Bool('true')
        except Exception:
            return Bool('false')

    def get_range(self, packed=None):
        negatives = lambda x: x if x >= 0 else len(self) + x
        pos1 = negatives(packed[0].value)
        pos2 = negatives(packed[1].value)
        arr = ""
        for i in range(pos1, pos2 + 1):
            arr += str(self.get_at(packed=[i]))[1:-1]
        self.value = arr
        return self

    def change_at(self, val, pos):
        pos = pos[0]
        pos = pos if type(pos) is int else pos.value
        i = 0
        for r, item in enumerate(self.value):
            item = self.item_to_str(item)
            for c, _ in enumerate(item):
                if i == pos:
                    self_r = self.value[r] if type(self.value[r]) is str else self.variables[self.value[r][0]]
                    self_str = str(self_r) if type(self_r) is not String else str(self_r)[1:-1]
                    val_str = str(val) if type(val) is not String else str(val)[1:-1]
                    self.value[r] = self_str[:c] + val_str + self_str[c+1:]
                    return self
                i += 1
        return Bool(False)

    def item_to_str(self, item):
        if type(item) is not str:
            item = self.variables[item[0]]
            item = str(item)[1:-1] if type(item) is String else str(item)
        return item

    def next_contain(self, item=None, start=None, packed=None):
        self_st = str(self)[1:-1]
        if packed is not None:
            item, start = packed
        if type(start) is Int:
            start = start.value
        item_len = len(item)
        item_st = str(item)[1:-1]
        for pos in range(start, len(self_st) - (item_len - 1)):
            if self_st[pos: item_len + pos] == item_st:
                return Int(pos)
        return Bool(False)

    def remove_first(self, packed=None):
        self.value = [str(self)[1:-1]]
        while packed is not None and len(packed) != 0:
            val = packed.pop(0)
            self.replace_first(to_rep=val, rep_with=String("", {}))
        return self

    def remove_all(self, packed=None):
        self.value = [str(self)[1:-1]]
        while packed is not None and len(packed) != 0:
            val = packed.pop(0)
            self.replace(to_rep=val, rep_with=String("", {}))
        return self

    def remove_at(self, pos=None, packed=None):
        amount = Int(1)
        self.value = list(str(self)[1:-1])
        if packed is not None:
            pos = packed[0]
            if len(packed) > 1:
                amount = packed[1]
        if (pos + amount).value > len(self.value):
            return Bool(False)
        for _ in range(amount.value):
            self.value.pop(pos.value)
        self.value = "".join(self.value)
        return self

    def replace(self, to_rep=None, rep_with=None, packed=None, amount=None):
        if packed is not None:
            to_rep, rep_with = packed
        if not type(to_rep) == type(rep_with) == String:
            return False
        st = self.rep_works(amount, rep_with, to_rep)
        self.value = list(st)
        return self

    def rep_works(self, amount, rep_with, to_rep):
        st = str(self)[1:-1]
        if amount is None:
            st = st.replace(str(to_rep)[1:-1], str(rep_with)[1:-1])
        else:
            st = st.replace(str(to_rep)[1:-1], str(rep_with)[1:-1], 1)
        return st

    def replace_first(self, to_rep=None, rep_with=None, packed=None):
        return self.replace(to_rep=to_rep, rep_with=rep_with, packed=packed, amount=1)

    def is_number(self):
        return Bool(re.fullmatch(INT, str(self)[1:-1]))

    def is_float(self):
        return Bool(re.fullmatch(FLOAT, str(self)[1:-1]))

    def to_caps(self):
        self.value = [str(self)[1:-1].upper()]
        return self

    def to_lower(self):
        self.value = [str(self)[1:-1].lower()]
        return self

    def __copy__(self):
        arr = []
        new_str = String("", self.variables)
        for c in self.value:
            arr.append(c)
        new_str.value = arr
        return new_str


class Float:
    def __init__(self, val):
        try:
            self.value = float(val.value)
        except AttributeError:
            self.value = float(val)
        self.attributes = {
            "len": lambda: Int(len(str(self))),
            "is?": lambda: Bool(self.value != 0),
            "int": self.to_int,
            "str": self.to_str,
            "bool": self.to_bool,
            "list": self.to_list,
        }

    def to_int(self):
        return Int(int(self.value))

    def to_str(self):
        return String(str(self), {})

    def to_bool(self):
        return Bool(self.value != 0)

    def to_list(self):
        lst = [x for x in str(self.value)]
        return List(lst)

    def __add__(self, other):
        if type(other) is Int:
            return Float(self.value + other.value)
        if type(other) is Float:
            return Float(self.value + other.value)
        if type(other) is String:
            return String(self, {}) + other.value
        if type(other) is Bool:
            return Float(self.value + 1 if other.value else 0)
        return Bool(False)

    def __pow__(self, other, modulo=None):
        if type(other) is Int or type(other) is Float:
            return self.value ** other.value
        return Bool(False)

    def __sub__(self, other):
        if type(other) is Int:
            return Float(self.value - other.value)
        if type(other) is Float:
            return Float(self.value - other.value)
        if type(other) is Bool:
            return Float(self.value - 1 if other.value else 0)
        return Bool(False)

    def __mul__(self, other):
        if type(other) is Int:
            return Float(self.value * other.value)
        if type(other) is Float:
            return Float(self.value * other.value)
        if type(other) is Bool:
            return Float(self.value * 1 if other.value else 0)
        return Bool(False)

    def __truediv__(self, other):
        if type(other) is Int:
            return Float(self.value / other.value)
        if type(other) is Float:
            return Float(self.value / other.value)
        return Bool(False)

    def __floordiv__(self, other):
        if type(other) is Int:
            return Int(self.value // other.value)
        if type(other) is Float:
            return Int(self.value // other.value)
        return Bool(False)

    def __mod__(self, other):
        if type(other) is Int:
            return Float(self.value % other.value)
        if type(other) is Float:
            return Float(self.value % other.value)
        return Bool(False)

    def __len__(self):
        return len(str(self.value))

    def __eq__(self, other):
        if type(other) != Float and type(other) != Int:
            return False
        return self.value == other.value

    def __str__(self):
        return str(self.value)


class Int:
    def __init__(self, val: object) -> object:
        self.value = None
        try:
            self.value = int(val.value)
        except AttributeError:
            self.value = int(val)
        self.attributes = {
            "len": lambda: Int(len(str(self))),
            "is?": lambda: Bool(self.value != 0),
            "float": self.to_float,
            "str": self.to_str,
            "bool": self.to_bool,
            "list": self.to_list,
        }

    def to_float(self):
        return Float(self.value)

    def to_str(self):
        return String(str(self), {})

    def to_bool(self):
        return Bool(self.value != 0)

    def to_list(self):
        lst = [int(x) for x in str(self.value)]
        return List(lst)

    def __add__(self, other):
        if type(other) is Int:
            return Int(self.value + other.value)
        if type(other) is Float:
            return Float(self) + other
        if type(other) is String:
            return String(self, {}) + other
        if type(other) is Bool:
            return Int(self.value + 1 if other.value else 0)
        return Bool(False)

    def __pow__(self, other, modulo=None):
        if type(other) is Int:
            return Int(self.value ** other.value)
        if type(other) is Float:
            return Float(self) ** other
        return Bool(False)

    def __sub__(self, other):
        if type(other) is Int:
            return Int(self.value - other.value)
        if type(other) is Float:
            return Float(self) - other
        if type(other) is String:
            return String(self, {}) - other
        if type(other) is Bool:
            return Int(self.value - 1 if other.value else 0)
        return Bool(False)

    def __mul__(self, other):
        if type(other) is Int:
            return Int(self.value * other.value)
        if type(other) is Float:
            return Float(self) * other
        if type(other) is String:
            return String(self, {}) * other
        if type(other) is Bool:
            return Int(self.value * 1 if other.value else 0)
        return Bool(False)

    def __truediv__(self, other):
        if type(other) is Int:
            return Float(self) / other
        if type(other) is Float:
            return Float(self) / other
        return Bool(False)

    def __floordiv__(self, other):
        if type(other) is Int:
            return Int(self.value // other.value)
        if type(other) is Float:
            return Int(self.value // other.value)
        return Bool(False)

    def __mod__(self, other):
        if type(other) is Int:
            return Int(self.value % other.value)
        if type(other) is Float:
            return Float(self.value % other.value)
        return Bool(False)

    def __len__(self):
        return len(str(self.value))

    def __eq__(self, other):
        if type(other) != Int and type(other) != Float:
            return False
        return self.value == other.value

    def __str__(self):
        return str(self.value)

    def __copy__(self):
        return Int(self.value)

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):    # todo this... 2(!=)
        return not (self.__eq__(other))


class Iterable:
    def __init__(self, lst):
        self.value = lst if type(lst) is list else lst.value
        self.functions = {
            "pop": self.pop,
            "has": self.has,
        }
        self.attributes = {
            "lst": self.to_lst,
        }

    def to_lst(self):
        return List(self.value)

    def pop(self):
        return self.value.pop(0)

    def has(self):
        return len(self.value) > 0

    def __str__(self):
        st = '{'
        for i, v in enumerate(self.value):
            st += str(v)
            if i < len(self.value) - 1:
                st += ', '
        return st + '}'

    def __len__(self):
        return len(self.value)

    def __add__(self, other):
        return Bool(False)

    def __mul__(self, other):
        return Bool(False)

    def __truediv__(self, other):
        return Bool(False)

    def __floordiv__(self, other):
        return Bool(False)

    def __sub__(self, other):
        return Bool(False)

    def __pow__(self, power, modulo=None):
        return Bool(False)


def list_split(val):
    val = val[1: -1].split(',')
    i = 0
    while i < len(val):
        amount_of_open = val[i].count("[") - val[i].count("]")
        if amount_of_open > 0:
            val[i] += "," + val[i + 1]
            val.pop(i + 1)
        else:
            i += 1
    return val


class List:
    def __init__(self, *val):
        val = val[0]
        if val is None:
            self.value = list()
        elif type(val) is list:
            self.value = [x for x in val]
        elif type(val) is int:
            self.value = [Bool(False) for _ in range(val)]
        elif type(val) is List:
            self.value = [x for x in val.value]
        else:
            exit(99)
        self.functions = {
            "nxtOf": self.next_contain_user,
            "rem": self.remove_all,
            "remF": self.remove,
            "pop": self.remove_at,
            "rep": self.replace,
            "repF": self.replace_first,
            "get": self.get_range,
            "sort": self.sort,
            "count": self.amount_of_occurrences,
            "dupe": self.get_first_dupe,
            "consDupe": self.get_first_consecutive_dupe,
            "dupes": self.get_all_dupes,
            "consDupes": self.get_all_consecutive_dupes,
            "stitch": self.stitch,
            "copy": self.__copy__,
            "has": self.has,
            "get_at": self.get_at,
            "change_at": self.change_at,
            "reverse": self.reverse,
        }
        self.attributes = {
            "len": self.length,
            "is?": lambda: Bool(len(self) > 0),
            "isSorted?": self.is_sorted,
            "hasDupe?": self.has_duplicate,
            "hasConstDupe?": self.has_const_duplicate,
            "float": self.to_float,
            "str": self.to_str,
            "bool": self.to_bool,
            "int": self.to_int,
        }

    def reverse(self):
        self.value = self.value[::-1]
        return self

    def to_float(self):
        val = float("".join(self.value))
        return Float(val)

    def to_str(self):
        return String("".join(self.value), {})

    def to_bool(self):
        return Bool(len(self) > 0)

    def to_int(self):
        val = int("".join(self.value))
        return Int(val)

    def is_sorted(self):
        return Bool(
            self.value == copy.copy(self).sort().value or
            self.value == copy.copy(self).sort(packed=[Bool(True)]).value
        )

    def __add__(self, other):
        if type(other) in [List, Int, Float, String, str, int,
                           float]:
            new_list = [x for x in self.value]
            new_list.append(other)
            return List(new_list)
        elif type(other) in [Bool, bool]:
            other_val = other if type(other) is bool else other.value
            new_list = List([x for x in self.value])    # 6 was deepcopy(list) ???
            return new_list + "true" if other_val else "false"
        return self

    def __mul__(self, other):
        if type(other) is Int:
            return List(self.value * other.value)
        if type(other) is Float:
            return Bool(False)
        if type(other) is String:
            return Bool(False)
        if type(other) is Bool:
            return List(self.value * 1 if other.value else 0)
        if type(other) is List:
            return Bool(False)

    def __pow__(self, power, modulo=None):
        return Bool(False)

    def __truediv__(self, other):
        return Bool(False)

    def __floordiv__(self, other):
        return Bool(False)

    def __sub__(self, other):
        return Bool(False)

    def __str__(self):
        st = "["
        for i, obj in enumerate(self.value):
            st += str(obj)
            if i != len(self.value) - 1:
                st += ", "
        return st + "]"

    def __len__(self):
        return len(self.value)

    def length(self):
        return Int(len(self))

    def __contains__(self, item):
        for obj in self.value:
            if item.value == obj.value:
                return True
        return False

    def has(self, packed=None):
        return Bool(packed[0] in self)

    def amount_of_occurrences(self, packed=None):
        item = packed[0]
        amount = 0
        for i in self.value:
            if i.value == item.value:
                amount += 1
        return Int(amount)

    def is_duplicate(self, packed=None):
        item = packed[0]
        return Bool(self.amount_of_occurrences([item]) > 1)

    def has_duplicate(self):
        for item in self.value:
            if self.is_duplicate(packed=[item]).value:
                return Bool(True)
        return Bool(False)

    def has_const_duplicate(self):
        for i, item in self.value[:-1]:
            if item == self.value[i+1]:
                return Bool(True)
        return Bool(False)

    def get_first_dupe(self):
        for item in self.value:
            if self.is_duplicate(packed=[item]).value:
                return item
        return Bool(False)

    def get_first_consecutive_dupe(self):
        for i, item in enumerate(self.value):
            if i == len(self)-1:
                return Bool(False)
            if self.value[i+1].value == item.value:
                return item

    def get_all_dupes(self):
        lst = List(None)
        for item in self.value:
            if self.is_duplicate(packed=[item]).value:
                if item not in lst:
                    lst.change_at(item, [len(lst)])
        return lst

    def get_all_consecutive_dupes(self):
        lst = List(None)
        for i, item in enumerate(self.value):
            if i == len(self) - 1:
                return lst if len(lst) > 0 else Bool(False)
            if self.value[i + 1].value == item.value:
                lst.change_at(item, [len(lst)])

    def get_at(self, packed=None):
        pos = packed[0] if type(packed[0]) in [int, str] else packed[0].value
        to_change = self
        if type(pos) is str:
            pos = int(pos[1:])
            if pos >= len(to_change.value):
                return Bool(False)
        elif pos >= len(to_change.value):
            for _ in range(pos - (len(to_change.value) - 1)):
                to_change.value.append(Bool(False))
        return to_change.value[pos]

    def get_range(self, packed=None):
        negatives = lambda x: x if x >= 0 else len(self) + x
        pos1 = negatives(packed[0].value)
        pos2 = negatives(packed[1].value)
        arr = []
        for i in range(pos1, pos2 + 1):
            arr.append(self.get_at(packed=[i]))
        self.value = arr
        return self

    def change_at(self, val, posses):
        prev = None
        to_change = self
        for pos in posses:
            pos = pos if type(pos) is int else pos.value
            if pos >= (ln := len(to_change)):
                for _ in range(pos - (ln - 1)):
                    to_change.value.append(Bool(False))
            prev = (to_change, pos)
            to_change = to_change.value[pos]
        prev[0].value[prev[1]] = copy.copy(val)
        return self

    def change_by(self, val, posses):
        prev = None
        to_change = self
        for pos in posses:
            pos = int(pos) if type(pos) is str else int(pos.value)
            if pos >= (ln := len(to_change)):
                for _ in range(pos - (ln - 1)):
                    to_change.value.append(Bool(False))
            prev = (to_change, pos)
            to_change = to_change.value[pos]
        prev[0].value[prev[1]] = to_change + val
        return self

    def next_contain(self, item=None, start=None):
        if start >= len(self.value) or item not in self:
            return Bool(False)
        for i in range(start, len(self.value)):
            if item.value == self.value[i].value:
                return Int(i)

    def next_contain_user(self, packed=None):
        item = packed[0]
        start = 0 if len(packed) == 1 else packed[1].value
        if start >= len(self.value) or item not in self:
            return Bool(False)
        for i in range(start, len(self.value)):
            if item.value == self.value[i].value:
                return Int(i)
        return Bool(False)

    def remove(self, packed=None):
        while packed is not None and len(packed) != 0:
            val = packed.pop(0)
            pos = self.next_contain(val, 0).value
            if type(pos) is not int:
                return self
            self.value.pop(pos)
        return self

    def remove_all(self, packed=None):
        while packed is not None and len(packed) != 0:
            val = packed.pop(0)
            while type(pos := self.next_contain(val, 0).value) is int:
                self.value.pop(pos)
        return self

    def remove_at(self, pos=None, amount=1, packed=None):
        if packed is not None:
            pos = packed[0].value
            if len(packed) > 1:
                amount = packed[1].value
        if pos + amount > len(self):
            return Bool(False)
        for _ in range(amount):
            self.value.pop(pos)
        return self

    def replace(self, to_rep=None, rep_with=None, packed=None, amount=None):
        if packed is not None:
            if len(packed) == 2:
                to_rep, rep_with = packed
            else:
                to_rep, rep_with, amount = packed
                amount = amount.value
        if amount is None:
            amount = len(self) + 10000  # just in case
        while type(pos := self.next_contain(to_rep, 0).value) is int:
            self.value[pos] = rep_with
            amount -= 1
            if amount == 0:
                break
        return self

    def replace_first(self, to_rep=None, rep_with=None, packed=None):
        return self.replace(to_rep=to_rep, rep_with=rep_with, packed=packed, amount=1)

    def sort(self, packed=None, variables=None):
        for i in range(len(self.value)):
            for j in range(i):
                val1 = packed[-1]([packed[0] + f"({ self.value[i] })"], variables)
                val2 = packed[-1]([packed[0] + f"({ self.value[j] })"], variables)
                if val1 < val2 if len(packed) == 2 or not packed[1].value else val1 > val2:
                    temp = self.value[i]
                    self.value[i] = self.value[j]
                    self.value[j] = temp
                else:
                    break
        return self

    def stitch(self, packed=None):
        if packed is None:
            packed = [""]
        sep = packed[0]
        st = ""
        for i, val in enumerate(self.value):
            st += str(val)[1:-1] if type(val) is String else str(val)
            if i == len(self.value) - 1:
                return String(st, {})
            st += str(sep)[1:-1] if type(sep) is String else str(sep)

    def __copy__(self):
        return List(self.value)

    def __eq__(self, other):
        if type(other) is not List:
            return False
        if len(other) != len(self):
            return False
        for obj1, obj2 in zip(self.value, other.value):
            if obj1 != obj2:
                return False
        return True


def matrix_split(val):
    val = val[2: -2].split('|')
    i = 0
    while i < len(val):
        amount_of_open = val[i].count("[") - val[i].count("]")
        if amount_of_open > 0:
            val[i] += "," + val[i + 1]
            val.pop(i + 1)
        else:
            i += 1
    if val[0].startswith('['):
        return [list_split(v) for v in val]
    return [Int(int(val[0]))]


class Matrix:
    def __init__(self, *val):
        val = val[0]
        if type(val) is Int:
            self.value = \
                [[Bool(False) for _ in range(val.value)] for _ in range(val.value)]
        elif type(val) is list:
            self.value = val
        elif type(val) is Matrix:
            self.value = [x for x in val]   # 6 was copy.copy(val).value??

        self.functions = {
            "nxtOf": self.next_contain,
            "rem": self.remove_all,
            "remF": self.remove,
            "erase": self.remove_at,
            "rep": self.replace,
            "repF": self.replace_first,
            "sort": self.sort,
            "copy": self.__copy__,
            "has": self.has,
            "get_at": self.get_at,
            "change_at": self.change_at
        }
        self.attributes = {
            "cols": self.cols,
            "rows": self.rows,
            "len": self.length,
            "is?": lambda: Bool(len(self) > 0),
            "isSorted?": None
        }

    def __add__(self, other):
        return Bool(False)

    def __mul__(self, other):
        return Bool(False)

    def __truediv__(self, other):
        return Bool(False)

    def __floordiv__(self, other):
        return Bool(False)

    def __sub__(self, other):
        return Bool(False)

    def __pow__(self, power, modulo=None):
        return Bool(False)

    def __str__(self):
        st = "[|"
        for r, row in enumerate(self.value):
            for c, obj in enumerate(row):
                st += str(obj)
                if c != len(row) - 1:
                    st += ", "
            st += "]"
            if r != len(self.value) - 1:
                st += "|\n     ["
        return st + "|]"

    def __len__(self):
        return len(self.value)

    def length(self):
        return Int(len(self))

    def __contains__(self, item):
        for obj in self.value:
            if item in obj:
                return True
        return False

    def has(self, packed=None):
        return Bool(packed[0] in self)

    def cols_rows(self, is_cols=False):
        cols = List(None)
        for col in range(len(self)):
            col_arr = List(None)
            for row in range(len(self)):
                if is_cols:
                    col_arr.change_at(self.get_at([row, col]), [row])
                else:
                    col_arr.change_at(self.get_at([col, row]), [row])
            cols.change_at(col_arr, [len(cols)])
        return cols

    def cols(self):
        return self.cols_rows(is_cols=True)

    def rows(self):
        return self.cols_rows(is_cols=False)

    def get_at(self, packed=None):
        if packed[0] is None:
            pass    # return a list
        if packed[1] is None:
            pass    # return a list
        row = packed[0] if type(packed[0]) is int else packed[0].value
        col = packed[1] if type(packed[1]) is int else packed[1].value
        if row >= len(self) or col >= len(self):
            return Bool(False)
        return self.value[row][col]

    def change_at(self, val, posses):
        row = posses[0] if type(posses[0]) is int else posses[0].value
        col = posses[1] if type(posses[1]) is int else posses[1].value
        self.value[row][col] = copy.copy(val)
        return self

    def change_by(self, val, posses):
        self.change_at(self.get_at(packed=posses) + val, posses)
        return self

    def next_contain(self, item=None, start=None, packed=None):
        if packed is not None:
            item = packed[0]
            start = [0, 0] if len(packed) == 1 else packed[1].value
        if start[0] >= len(self.value) or start[1] >= len(self.value) or item not in self:
            return Bool(False)
        for row in range(start[0], len(self)):
            for col in range(start[1], len(self)):
                if type(self.value[row][col]) is type(item):
                    if self.value[row][col].value == item.value:
                        row = Int(row)
                        col = Int(col)
                        return List([row, col])
        return Bool(False)

    def remove(self, packed=None):
        while packed is not None and len(packed) != 0:
            val = packed.pop(0)
            row, col = self.next_contain(val, [0, 0]).value
            row, col = row.value, col.value
            if type(row) is not int or type(col) is not int:
                return self
            self.change_at(Bool(False), [row, col])
        return self

    def remove_all(self, packed=None):
        while packed is not None and len(packed) != 0:
            val = packed.pop(0)
            while type(pos := self.next_contain(val, [0, 0]).value) is list:
                self.change_at(Bool(False), pos)
        return self

    def remove_at(self, row=None, col=None, packed=None):
        if packed is not None:
            row, col = packed
            row, col = row.value, col.value
        if row > len(self) or col > len(self):
            return Bool(False)
        self.value[row][col] = Bool(False)
        return self

    def replace(self, to_rep=None, rep_with=None, packed=None, amount=None):
        if packed is not None:
            to_rep, rep_with = packed
        if amount is None:
            amount = len(self) + 10000  # just in case
        while type(pos := self.next_contain(to_rep, [0, 0]).value) is list:
            self.value[pos[0].value][pos[1].value] = rep_with
            amount -= 1
            if amount == 0:
                break
        return self

    def replace_first(self, to_rep=None, rep_with=None, packed=None):
        return self.replace(to_rep=to_rep, rep_with=rep_with, packed=packed, amount=1)

    def sort(self, packed=None):    # todo MAYBE
        pass

    def __copy__(self):
        new_m = Matrix(Int(len(self)))
        for row in range(len(self)):
            for col in range(len(self)):
                new_m.value[row][col] = copy.copy(self.value[row][col])
        return new_m

    def __eq__(self, other):
        if type(other) is not Matrix:
            return False
        if len(other) != len(self):
            return False
        for obj1, obj2 in zip(self.value, other.value):
            if obj1 != obj2:
                return False
        return True
