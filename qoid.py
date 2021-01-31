"""
Qoid is a database-like serialization API for reading and writing miscellaneous data in a readable way
"""

import os
import json
import copy


class QoidError(KeyError):
    __doc__ = "A QoidError is raised for KeyErrors and KeyError-like problems which occur specifically in qoid_test.py."


class QoidParseError(SyntaxError):
    __doc__ = "A QoidParseError is raised for any SyntaxError involving the parsing of a file using Qoid markup."


class Property:
    __doc__ = "A Property is a tag-value pair, where the tag is used to refer to the value given"

    def __init__(self, tag: str ="Property", val=None, parent=None):
        self.tag = str(tag)
        self.val = val
        self.parent = parent

    def __add__(self, other):
        if isinstance(other, Property):
            return Qoid(f"{self.tag} + {other.tag}", [self, other])
        else:
            return NotImplemented

    def __bytes__(self):
        return str.encode(format(self))

    def __eq__(self, other):
        if isinstance(other, Property):
            return self.tag == other.tag and self.val == other.val
        return False

    def __format__(self, format_spec=None):
        return self.tag + (f": {self.val}" if self.val else "")

    def __ge__(self, other):
        return self.tag >= other.tag

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(format(self))

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return 1 if self.val else 0

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"Property({self.tag}, {self.val})"

    def __str__(self):
        return format(self)

    def get_parent(self):
        """
        :return: the parent Qoid
        """
        return self.parent

    def lower(self):
        return Property(self.tag.lower(), self.val.lower() if self.val else "")

    def set(self, tag=None, val=None):
        """
        Set the Property's tag, value, or both

        :param tag: the new tag for the Property
        :param val: the new value for the Property
        """
        if tag:
            self.tag = tag
        if val:
            self.val = val


class Qoid:
    __doc__ = "A Qoid is a set of Properties. Each Qoid has a tag which functions as a key."

    def __init__(self, tag: str="Qoid", val=None, parent=None):
        self.tag = tag
        self.val = []
        self.parent = parent
        if val:
            if isinstance(val, (Qoid, list)):
                for e in val:
                    if isinstance(e, Property):
                        self.append(e)
                    else:
                        err = [val.index(e), type(e)]
                        raise TypeError(f"Invalid element val[{err[0]}] of type {err[1]}: must contain only Property")
            else:
                raise ValueError(f"Invalid val type {type(val)}: must submit Qoid or list")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += other
        return out

    def __bytes__(self):
        return str.encode(str(self))

    def __contains__(self, item):
        if isinstance(item, Property):
            for e in self:
                if item == e:
                    return True
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return True
        return False

    def __delitem__(self, key):
        if isinstance(key, int):
            del self.val[key]
        elif isinstance(key, str):
            del self.val[self.index(key)]
        else:
            raise ValueError(f"Invalid type {type(key)}, must use int or str")

    def __eq__(self, other):
        if isinstance(other, Qoid):
            if self.tag != other.tag:
                return False
            elif len(self) != len(other):
                return False

            temp = copy.deepcopy(other.val)

            for each in self:
                if each in temp:
                    temp.pop(temp.index(each))
                else:
                    return False

            if len(temp) == 0:
                return True
        return False

    def __format__(self, format_spec=None):
        out = f"#{self.tag}\n" if len(self.tag) else ""
        for e in self:
            out += format(e) + "\n"
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return Qoid(self.tag, [self.val[i] for i in range(start, stop, step)])
        elif isinstance(item, int):
            return self.get(n=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Property):
            out = copy.deepcopy(self)
            out.append(Property(other.tag, other.val))
            return out
        elif isinstance(other, Qoid):
            out = copy.deepcopy(self)
            for e in other:
                out.append(Property(e.tag, e.val))
            return out
        elif isinstance(other, list):
            out = copy.deepcopy(self)
            for e in other:
                out += e
            return out
        else:
            raise ValueError(f"Incompatible type {type(other)}, must be Property or Qoid")

    def __isub__(self, subtra):
        out = copy.deepcopy(self)
        if isinstance(subtra, Property):
            try:
                out.pop(subtra)
            except QoidError:
                pass
            return out
        elif isinstance(subtra, Qoid):
            for e in subtra:
                if e.val is None:
                    try:
                        out.pop(e.tag)
                    except QoidError:
                        pass
                else:
                    try:
                        out.pop(e)
                    except QoidError:
                        pass
            return out
        else:
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in Qoid.__isub__(self, subtra)")

    def __iter__(self):
        return iter(self.val)

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return len(self.val)

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __radd__(self, other):
        if isinstance(other, Property):
            out = Qoid(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        # TODO: fix
        return f"Qoid({self.tag}, {[repr(v) for v in self.val]})"

    def __reversed__(self):
        return Qoid(self.tag, val=list(reversed(self.val)))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, Property):
                self.val[key] = value
            else:
                self.val[key] = Property(self.val[key].tag, value)
        elif isinstance(key, str):
            if isinstance(value, Property):
                self.val[self.index(key)] = value
            else:
                self.val[self.index(key)] = Property(key, value)
        else:
            raise TypeError(f"Unsupported type {type(key)} for key in Qoid.__setitem__(self, key, value)")

    def __sub__(self, other):
        out = copy.deepcopy(self)
        out -= other
        return out

    def __str__(self):
        return format(self)

    def all_of(self, tag: str):
        """
        Finds all instances of the given tag

        :param tag: the tag to search for
        :return: a list of all Properties with the given tag
        """
        if tag:
            out = []
            for e in self:
                if e.tag == tag:
                    out.append(e)
            return out
        else:
            raise QoidError(f"{tag}")

    def append(self, item: Property):
        """
        Add a Property to the Qoid

        :param item: the item to add
        """
        to_add = copy.deepcopy(item) if item.parent else item
        to_add.parent = self
        self.val.append(to_add)

    def count(self, tag):
        """
        Counts the number of times the given tag appears

        :param tag: the tag to count
        :return: the number of times tag appears
        """
        c = 0
        for e in self:
            c += 1 if e.tag == tag else 0
        return c

    def extend(self, val: iter):
        """
        Add all the Properties given to the Qoid

        :param val: the Properties to add
        """
        for e in self:
            if not isinstance(e, Property):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Property is allowed")
        self.val.extend(val)

    def get(self, tag:str = None, n=-1):
        """
        Get the first Property which matches the given tag,
        or the Property at the given index.
        If no argument is specified, returns all contents.

        :param tag: the tag to search for
        :param n: the index to select
        :return: the first Property with the given tag; at the given index; or the set of Properties
        """
        if tag:
            for e in self:
                if e.tag == tag:
                    return e
            raise QoidError(f"'{tag}'")
        elif n == -1:
            return self.val
        else:
            if len(self) > n >= 0:
                return self.val[n]
            raise IndexError("Qoid index out of range")

    def get_parent(self):
        """
        :return: the Bill in which this Qoid is contained
        """
        return self.parent

    def index(self, item):
        """
        Get the first index of a Property with the given tag

        :param item: the Property or tag to search for
        :return: the first index of the Property or tag
        """
        if isinstance(item, Property):
            for e in self:
                if item == e:
                    return self.val.index(e)
            raise QoidError(f"'{item}'")
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return self.val.index(e)
            raise QoidError(f"'{item}'")
        else:
            raise TypeError(f"Invalid type {type(item)}, must use Property or str")

    def insert(self, index, obj):
        """
        Add a set of Properties starting from the given index

        :param index: the location in the Qoid to start
        :param obj: the object to be inserted
        """
        if isinstance(index, int):
            if isinstance(obj, Property):
                self.val = self[:index] + [obj] + self[index:]
            elif isinstance(obj, Qoid):
                self.val = self[:index] + obj.val + self[index:]
            else:
                raise TypeError(f"Unsupported type '{type(obj)}' for argument 'obj', must be 'Property' or 'Qoid'")
        else:
            raise TypeError(f"Unsupported type '{type(obj)}' for argument 'index', must be 'int'")

    def lower(self):
        """
        :return: the Qoid with its tag in lower case
        """
        return Qoid(self.tag.lower(), copy.deepcopy(self.val))

    def pack(self):
        """
        Pack the contents of this qoid into a json-serialized format

        :return: the json-serialized Qoid
        """
        return {self.tag: [self.tags(), self.vals()]}

    def pop(self, this=None):
        """
        Remove either the property at the given index, with the given tag,
        or which matches the property given

        :param this: the index, tag, or Property to pop
        :return: the popped Property
        """
        if not this:
            return self.val.pop()
        elif isinstance(this, int):
            if len(self) > this >= 0:
                return self.val.pop(this)
            else:
                raise IndexError("Qoid index out of range")
        elif isinstance(this, str):
            for e in self:
                if e.tag == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError(f"'{this}'")
        elif isinstance(this, Property):
            for e in self:
                if e == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError(f"'{this}'")
        else:
            raise TypeError(f"Unsupported type {type(this)}, must be int, str, or Property")

    def reverse(self):
        """
        Reverse the order of the Properties in the Qoid
        """
        self.val = list(reversed(self.val))

    def set(self, tag=None, index=-1, val=None):
        """
        Set the first Property which matches the given tag, or at the given index.
        If no argument is specified, returns all contents.

        :param tag: the tag to be set
        :param index: the index of the Property to be set
        :param val: the value of the Property to set
        """
        if tag:
            tag = str(tag)
            for e in self:
                if e.tag == tag:
                    e.set(tag, val)
                    return
            raise QoidError(f"'{tag}'")
        else:
            if len(self) > index >= 0:
                self.val[index].set(val=val)
                return
            raise IndexError("Qoid index out of range")

    def sort(self):
        """
        Sort the Properties in the given Qoid
        """
        self.val.sort(key=Property.lower)

    def tags(self):
        """
        Get the set of all tags in this Qoid
        :return: a list of tags
        """
        return [e.tag for e in self]

    def update_parent(self):
        """
        Ensures all Properties in this Qoid have itself as parent
        """
        for e in self:
            e.parent = self

    def vals(self):
        """
        :return: the set of all values in this Qoid
        """
        return [e.val if e.val else "" for e in self]


class Bill:
    __doc__ = "A Bill is a Qoid whose elements are Qoids."

    def __init__(self, tag: str = "Bill", val=None, parent=None):
        self.tag = str(tag)
        self.val = []
        self.path = None
        self.parent = parent
        if val:
            if isinstance(val, (Bill, list)):
                for e in val:
                    if isinstance(e, Qoid):
                        self.append(e)
                    else:
                        raise ValueError(f"Invalid val type {type(e)}, must be Qoid")
            else:
                raise ValueError(f"Invalid val type {type(val)}, must submit Bill or list")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += other
        return out

    def __bytes__(self):
        return str.encode(str(self))

    def __contains__(self, item):
        if isinstance(item, Qoid):
            for e in self:
                if item == e:
                    return True
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return True
        return False

    def __delitem__(self, key):
        if isinstance(key, int):
            del self.val[key]
        elif isinstance(key, str):
            del self.val[self.index(key)]
        else:
            raise ValueError(f"Invalid type {type(key)}, must use int or str")

    def __eq__(self, other):
        if isinstance(other, Bill):
            if self.tag != other.tag:
                return False
            elif len(self) != len(other):
                return False

            # Due to the way __contains__ works, this is necessary
            temp = copy.deepcopy(other.val)

            for each in self:
                if each in temp:
                    temp.pop(temp.index(each))
                else:
                    return False

            if len(temp) == 0:
                return True
        return False

    def __format__(self, format_spec=None):
        out = ""
        for e in self:
            out += format(e) + "\n"
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return Bill(tag=self.tag, val=[self.val[i] for i in range(start, stop, step)])
        elif isinstance(item, int):
            return self.get(n=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Qoid):
            out = copy.deepcopy(self)
            out.append(Qoid(other.tag, other.val))
            return out
        elif isinstance(other, Bill):
            out = copy.deepcopy(self)
            for e in other:
                out.append(Qoid(e.tag, e.val))
            return out
        elif isinstance(other, list):
            out = copy.deepcopy(self)
            for e in other:
                out += e
            return out
        else:
            raise ValueError(f"Incompatible operands Bill and {type(other)}")

    def __isub__(self, subtra):
        out = copy.deepcopy(self)
        if isinstance(subtra, Qoid):
            out.pop(out.index(subtra))
            return out
        elif isinstance(subtra, Bill):
            for e in subtra:
                if e.val is None:
                    try:
                        out.pop(out.index(e.tag))
                    except QoidError:
                        pass
                else:
                    try:
                        out.pop(out.index(e))
                    except QoidError:
                        pass
            return out
        else:
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in Bill.__isub__(self, subtra)")

    def __iter__(self):
        return iter(self.val)

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return len(self.val)

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __radd__(self, other):
        if isinstance(other, Qoid):
            out = Bill(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return f"Bill({self.tag}, {self.val})"

    def __reversed__(self):
        return Bill(self.tag, val=list(reversed(self.val)))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, Qoid):
                self.val[key] = value
            else:
                raise ValueError(f"Unsupported type {type(value)} for 'value in Qoid.__setitem__(self, key, value); must be Qoid")
        elif isinstance(key, str):
            if isinstance(value, Qoid):
                self.val[self.index(key)] = value
            else:
                raise ValueError(f"Unsupported type {type(value)} for 'value in Qoid.__setitem__(self, key, value); must be Qoid")
        else:
            raise TypeError(f"Unsupported type {type(key)} for 'key' in Qoid.__setitem__(self, key, value); must be int or str")

    def __sub__(self, other):
        out = copy.deepcopy(self)
        out -= other
        return out

    def __str__(self):
        return format(self)

    def append(self, item: Qoid):
        """
        Add the given Qoid to the Bill.

        :param item: the Qoid to be appended
        """
        to_add = copy.deepcopy(item) if item.parent else item
        to_add.parent = self
        self.val.append(to_add)

    def count(self, tag: str):
        """
        Count the number of occurrences of the given tag

        :param tag: the tag to be matched
        :return: the number of times the tag appears
        """
        c = 0
        for e in self:
            c += 1 if e.tag == tag else 0
        return c

    def extend(self, val: iter):
        """
        Extend the contents of the Bill with the given values

        :param val: the set to extend with
        """
        for e in val:
            if not isinstance(e, Qoid):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Register or Bill is allowed")
        self.val.extend(val)

    def get(self, tag=None, n=-1):
        """
        Get all Qoids which match the given tag.
        If no argument is specified, returns all contents.

        :param tag: the tag to match
        :param n: the index to get; -1 means return all
        """
        if tag:
            tag = str(tag)
            out = Bill(self.tag)
            for e in self:
                if e.tag == tag:
                    return e
            raise QoidError(f"'{tag}'")
        elif n == -1:
            return self.val
        else:
            if len(self) > n >= 0:
                return self.val[n]
            raise IndexError("Qoid index out of range")

    def get_parent(self):
        """
        :return: the parent to this Bill
        """
        return self.parent

    def index(self, item):
        """
        Get the first index of a Qoid with the given tag

        :param item: the tag to be matched
        :return: the first index of a Qoid with the given tag
        """
        if isinstance(item, Qoid):
            if item in self:
                return self.val.index(item)
            raise QoidError(f"'{item}'")
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return self.val.index(e)
            raise QoidError(f"'{item}'")
        else:
            raise TypeError(f"Invalid type {type(item)}, must use Qoid or str")

    def insert(self, index, obj):
        """
        Place the given Qoid or Bill's contents at the given index

        :param index: the index to place the contents
        :param obj: the contents to be placed
        """
        if isinstance(index, int):
            if isinstance(obj, Qoid):
                self.val = self[:index].val + [obj] + self[index:].val
            elif isinstance(obj, Bill):
                self.val = self[:index].val + obj.val + self[index:].val
            else:
                raise TypeError(f"Unsupported type '{type(obj)}', must be 'Qoid' or 'Bill'")
        else:
            raise TypeError(f"Unsupported type '{type(index)}', must be 'int'")

    def lower(self):
        """
        :return: the Bill with the tag in lower case
        """
        return Bill(self.tag.lower(), copy.deepcopy(self.val))

    @staticmethod
    def open(source_file: str):
        """
        Read and parse a .cxr or .json file

        :param source_file: the file to be parsed
        :return: an Bill constructed out of the source file
        """
        source_file = source_file.replace("/", "\\")
        if os.path.isfile(source_file):
            with open(source_file, "r") as f:
                if source_file.endswith(".json"):
                    content = json.load(fp=f)
                elif source_file.endswith(".cxr"):
                    content = [l.replace("\n", "") for l in f.readlines()]
                    tag = source_file.split("\\")[-1]
                    tag = tag.replace(".cxr", "")
                    out = Bill.parse(content, tag=tag)
                    out.source = source_file
                    return out
                else:
                    raise TypeError(f"Invalid file type; must be .json or .cxr")
        else:
            raise FileNotFoundError(f"Invalid source specified: {source_file}")

    def pack(self):
        """
        TODO: fix or deprecate

        :return: the contents of this Bill in a json-serialized format
        """
        return {q.tag: [q.tags(), q.vals()] for q in self}

    def path_priority(self):
        """
        :return: the local path to which the file will save
        """
        if self.path:
            return self.path
        else:
            return self.tag + (".cxr" if not self.tag.endswith(".cxr") else "")

    def create_path(self):
        """
        :return: a file path for saving the given Bill
        """
        p = self.path_priority()
        if self.parent:
            out = self.parent.create_path()
            return os.path.join(out, p)
        else:
            return p

    @staticmethod
    def parse(source, tag: str = "Bill"):
        """
        Parse the contents of a file, whether it's
        lines of text or a dict

        :param source: the contents to be parsed
        :param tag: the tag value to give the parsed Bill
        :return: the parsed Bill
        """
        if isinstance(source, list):
            spool = None
            state = 0
            val = []
            for x in range(len(source)):
                if state == 0:
                    if not source[x]:
                        pass
                    elif source[x][0] == '#':
                        spool = Qoid(source[x][1:])
                        state = 1
                else:
                    if not source[x]:
                        val.append(spool)
                        spool = None
                        state = 0
                    elif source[x][0] == "/":
                        pass
                    else:
                        s = source[x].split(':', 1)
                        p = Property(tag=s[0], val=s[1].strip() if len(s) == 2 else "")
                        spool += p
            if spool is not None:
                val.append(spool)
            return Bill(tag=tag, val=val)
        elif isinstance(source, dict):
            qoids = []
            for key, value in source.items():
                # Step 1: ensure the tag is a string, and value is a 2-length list
                if isinstance(key, str) and isinstance(value, list) and len(value) == 2:
                    t = value[0]
                    v = value[1]
                    # Step 2: ensure both value elements are lists
                    if isinstance(t, list) and isinstance(v, list) and len(t) == len(v):
                        # Step 3: ensure all elements are strings
                        for e in t:
                            if not isinstance(e, str):
                                raise QoidParseError("Invalid JSON format: tags contain non-string")
                        for e in v:
                            if not isinstance(e, str):
                                raise QoidParseError("Invalid JSON format: vals contain non-string")
                        # Step 4: create qoid
                        properties = []
                        for k in range(len(t)):
                            properties.append(Property(tag=t[k], val=v[k]))
                        q = Qoid(key, val=properties)
                        qoids.append(q)
                    else:
                        raise QoidParseError("Invalid JSON format: value is not tag-value lists")
                else:
                    raise QoidParseError("Invalid JSON format: json item is not a tag-value pair")
            return Bill(tag=tag, val=qoids)
        else:
            raise TypeError(f"Illegal source of type {type(source)}: must be list or dict")

    def pop(self, index=-1):
        """
        Remove the Qoid at the given index

        :param index: the index to remove
        :return: the Qoid popped from the Bill
        """
        return self.val.pop(index)

    def reverse(self):
        """
        Reverse the value set of the Bill
        """
        self.val = list(reversed(self.val))

    def sort(self):
        """
        Sort the contents of the Bill
        """
        self.val.sort(key=Qoid.lower)

    def save(self, echo=True, is_json=False):
        """
        Save

        :param echo: decides whether to display debug information
        :param is_json: determines whether the file should be json-serialized
        """
        with open(self.create_path() + (".json" if is_json else ""), 'w+') as out:
            if is_json:
                json.dump(obj=self.pack(), fp=out)
            else:
                out.write(format(self))
        if echo:
            print(f"Bill {self.tag} saved to {self.create_path()}")

    def tags(self):
        """
        :return: the set of all tags in this Bill
        """
        return [e.tag for e in self]

    def update_parent(self):
        """
        Ensure that each member of the Bill is properly parented
        """
        for e in self:
            e.parent = self
            e.update_parent()

    def vals(self):
        """
        :return: the set of values in the Bill
        """
        return [e.val for e in self]


class Register:
    __doc__ = "A Register is a Qoid whose elements are all Bills or other Registers"

    def __init__(self, tag: str = "Register", val=None, parent=None):
        self.tag = tag[:-4] if tag.endswith(".cxr") else tag
        self.val = []
        self.path = None
        self.parent = parent
        if val:
            if isinstance(val, (list, tuple)):
                for e in val:
                    if isinstance(e, (Register, Bill)):
                        self.append(e)
                    else:
                        raise ValueError(f"Invalid val type {type(e)} in {type(val)}, must be Bill or Register")
            elif isinstance(val, (Bill, Register)):
                self.append(val)
            else:
                raise ValueError(f"Invalid val type {type(val)}, must be list, tuple, Bill, or Register")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += other
        return out

    def __bytes__(self):
        return str.encode(format(self))

    def __contains__(self, item):
        if isinstance(item, (Register, Bill)):
            for e in self:
                if item == e:
                    return True
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return True
        return False

    def __delitem__(self, key):
        if isinstance(key, int):
            del self.val[key]
        elif isinstance(key, str):
            del self.val[self.index(key)]
        else:
            raise ValueError(f"Invalid type {type(key)}, must use int or str")

    def __eq__(self, other):
        if isinstance(other, Register):
            if self.tag != other.tag:
                return False
            elif len(self) != len(other):
                return False

            temp = copy.deepcopy(other.val)

            for each in self:
                if each in temp:
                    temp.pop(temp.index(each))
                else:
                    return False

            if len(temp) == 0:
                return True
        return False

    def __format__(self, format_spec=None):
        out = ""
        for e in self:
            out += f"/ {e.tag}\n\n"
            out += format(e)
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return Register(self.tag, [self.val[i] for i in range(start, stop, step)])
        elif isinstance(item, int):
            return self.get(index=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Bill):
            out = copy.deepcopy(self)
            if other.tag in out:
                raise ValueError(f"Bill {other.tag} already exists within the Register")
            else:
                out.append(Bill(other.tag, other.val))
                return out
        elif isinstance(other, Register):
            out = copy.deepcopy(self)
            if other.tag in out:
                raise ValueError(f"Register {other.tag} already exists within the Register")
            else:
                out.append(Register(other.tag, other.val))
                return out
        elif isinstance(other, list):
            out = copy.deepcopy(self)
            for e in other:
                out += e
            return out
        else:
            raise ValueError(f"Incompatible operands {type(self)} and {type(other)}")

    """Subtraction removes the subtrahend from the minuend if it exists"""
    def __isub__(self, subtra):
        out = copy.deepcopy(self)
        if isinstance(subtra, Bill):
            try:
                out.pop(out.index(subtra.tag))
            except QoidError:
                pass
            return out
        elif isinstance(subtra, Register):
            try:
                out.pop(out.index(subtra))
            except QoidError:
                pass
            return out
        elif isinstance(subtra, list):
            for e in subtra:
                out -= e
            return out
        else:
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in Qoid.__isub__(self, subtra)")

    def __iter__(self):
        return iter(self.val)

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return len(self.val)

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __radd__(self, other):
        if isinstance(other, Bill):
            out = Register(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return f"Register({self.tag}, {self.val})"

    def __reversed__(self):
        return Register(self.tag, val=reversed(self.val))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, (Bill, Register)):
                self.val[key] = value
            else:
                raise TypeError(f"Unsupported type {type(value)}; must be Bill or Register")
        elif isinstance(key, str):
            if isinstance(value, (Bill, Register)):
                self.val[self.index(key)] = value
            else:
                raise TypeError(f"Unsupported type {type(value)}; must be Bill or Register")
        else:
            raise TypeError(f"Unsupported type {type(key)} for 'key' in Qoid.__setitem__(self, key, value)")

    def __sub__(self, other):
        out = copy.deepcopy(self)
        out -= other
        return out

    def __str__(self):
        return format(self)

    def append(self, item):
        """
        Append the given Register or Bill to the Register

        :param item: the Register or Bill to be added
        """
        if isinstance(item, (Register, Bill)):
            to_add = copy.deepcopy(item) if item.parent else item
            to_add.parent = self
            self.val.append(to_add)
        else:
            raise ValueError(f"Can only append Register and Bill, not {type(item)}")

    def count(self, tag):
        """
        :param tag: the tag to be counted
        :return: the number of occurrences of the given tag
        """
        c = 0
        for e in self:
            c += 1 if e.tag == tag else 0
        return c

    def path_priority(self):
        """
        :return: the constructed path
        """
        if self.path:
            return self.path
        else:
            return self.tag + (".cxr" if not self.tag.endswith(".cxr") else "")

    def create_path(self):
        """
        :return: the local path
        """
        p = self.path_priority()
        if self.parent:
            out = self.parent.create_path()
            return os.path.join(out, p)
        else:
            return p

    def extend(self, val: iter):
        """
        Extend the contents of the Register with the given value

        :param val: the set to extend with
        """
        for e in val:
            if not isinstance(e, (Register, Bill)):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Register or Bill is allowed")
        self.val.extend(val)

    def get(self, tag: str = None, index=-1):
        """
        Get the Register or Bill with the given tag or at the given index
        If no arguments are specified, returns all contents

        :param tag: the tag to match
        :param index: the index to retrieve
        :return: the value at the given tag or index
        """
        if tag:
            tag = str(tag)
            out = Register(tag)
            for e in self:
                if e.tag == tag:
                    out.append(e)
            if len(out) > 1:
                return out
            elif len(out) == 1:
                return out[0]
            else:
                raise QoidError(f"'{tag}'")
        elif index == -1:
            return self.val
        else:
            if len(self) > index >= 0:
                return self.val[index]
            raise IndexError("Qoid index out of range")

    def get_parent(self):
        """
        :return: the parent for this Register
        """
        return self.parent

    def index(self, item):
        """
        Gives the index of the first occurrence of the item

        :param item: the Bill or Register to match
        :return: the index of the first occurrence of the item
        """
        if isinstance(item, (Register, Bill)):
            for e in self:
                if item == e:
                    return self.val.index(e)
            raise QoidError(f"'{item}'")
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return self.val.index(e)
            raise QoidError(f"'{format(item)}'")
        else:
            raise TypeError(f"Invalid type {type(item)}, must use Property or str")

    def insert(self, index, obj):
        """
        Insert the given Bill or Register at the given index

        :param index: the index to insert at
        :param obj: the Bill or Register to insert
        """
        if isinstance(index, int):
            if isinstance(obj, Bill):
                self.val = self[:index].val + [obj] + self[index:].val
            elif isinstance(obj, Register):
                self.val = self[:index].val + obj.val + self[index:].val
            else:
                raise TypeError(f"Unsupported type '{type(obj)}', must be 'Property' or 'Qoid'")
        else:
            raise TypeError(f"Unsupported type '{type(obj)}', must be 'int'")

    def lower(self):
        """
        :return: the Register with the tag lower case
        """
        return Register(self.tag.lower(), copy.deepcopy(self.val))

    @staticmethod
    def open(source_folder: str):
        """
        Read and parse a .cxr folder

        :param source_folder:
        :return: the completed Register
        """
        source_folder = source_folder.replace("/", "\\")
        if os.path.isdir(source_folder):
            out = Register(tag=source_folder.split("\\")[-1])
            out.path = source_folder.rsplit("\\", 1)[0]
            for e in os.listdir(source_folder):
                try:
                    if os.path.isdir(os.path.join(source_folder, e)) and e.endswith(".cxr"):
                        i = Register.open(os.path.join(source_folder, e))
                    elif e.endswith(".cxr"):
                        i = Bill.open(os.path.join(source_folder, e))
                    else:
                        raise QoidError("Invalid file type")
                    out += i
                except QoidError:
                    print(f"Ignoring invalid file type at {os.path.join(source_folder, e)}")
            return out
        else:
            raise NotADirectoryError(f"Invalid source specified: {source_folder}")

    def pack(self):
        """
        TODO: test, probably fix

        :return: the json-serialized Register
        """
        out = {}
        reg = []
        ind = []
        for e in self:
            if isinstance(e, Register):
                reg.append(e)
            else:
                ind.append(e)
        out.update({"Register": {e.tag: e.pack() for e in reg}})
        out.update({"Bill": {e.tag: e.pack() for e in ind}})
        return {self.tag: [self.tags(), self.vals()]}

    def pop(self, index=-1):
        """
        :param index: the index to pop
        :return: the popped value
        """
        return self.val.pop(index)

    def reverse(self):
        """
        Reverse the order of the values in the Register
        """
        self.val = list(reversed(self.val))

    def save(self, echo=True):
        """
        Save the Register to a .cxr folder

        :param echo: determines whether the save debug message displays
        """
        p = self.create_path()
        if not os.path.isdir(p):
            os.mkdir(p)
        for e in self:
            if isinstance(e, Register):
                p = e.create_path()
                if not os.path.isdir(p):
                    os.mkdir(p)
            e.save(echo=echo)
        if echo:
            print(f"Register {self.tag} saved to {self.create_path()}")

    def tags(self):
        """
        :return: a list of all tags in the Register
        """
        return [e.tag for e in self]

    def update_parent(self):
        """
        Ensures the contents of the Register are properly parented
        """
        for e in self:
            e.parent = self
            e.update_parent()

    def vals(self):
        """
        :return: a list of all lists of values in the Register
        """
        return [e.val for e in self]
