"""
Qoid is a database-like serialization API for reading and writing miscellaneous data in a readable way
"""

import os
import json
import copy

# Permitted file and directory extensions to read as Qoid
q_fext = (".cxr", ".meta", ".txt")
q_dirext = tuple(".cxr")


class QoidError(KeyError):
    __doc__ = "A QoidError is raised for KeyErrors and KeyError-like problems which occur specifically in qoid.py."


class NoParentError(TypeError):
    __doc__ = "A NoParentError is raised when attempting parent-requiring functions on Qoids where none exist"


class NoPathError(ValueError):
    __doc__ = "A NoSourcePathError is raised when attempting to save anything without a source, root, or target file path"


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

    def __bool__(self): return bool(self.tag) or bool(self.val)

    def __bytes__(self):
        return str.encode(format(self))

    def __eq__(self, other):
        if isinstance(other, Property):
            return self.tag == other.tag and self.val == other.val
        return False

    def __format__(self, format_spec):
        if format_spec:
            return self.tag + (f"{format_spec} {self.val}" if self.val else "")
        else:
            return self.tag + (f": {self.val}" if self.val else "")

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        return self.val[item]

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
        if self.parent:
            return self.parent
        else:
            raise NoParentError("No parent exists for this Property")

    def lower(self):
        return Property(self.tag.lower(), copy.deepcopy(self.val))

    """Set the property's tag, value, or both"""
    def set(self, tag=None, val=None):
        if tag:
            self.tag = tag
        if val:
            self.val = val

    def set_parent(self, parent):
        if isinstance(parent, Qoid):
            if self.parent and self in self.parent:
                self.parent.pop(self)
            self.parent = parent
        else:
            raise TypeError(f"Property.parent must be Qoid, not {type(parent)}")


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
                        self.val.append(copy.deepcopy(e))
                    else:
                        err = [val.index(e), type(e)]
                        raise TypeError(f"Invalid element val[{err[0]}] of type {err[1]}: must contain only Property")
            else:
                raise ValueError(f"Invalid val type {type(val)}: must submit Qoid or list")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += other
        return out

    def __bool__(self): return bool(self.tag) or bool(self.val)

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
            return all(e in other for e in self) and all(e in self for e in other)
        return False

    def __format__(self, format_spec):
        out = f"#{self.tag}\n" if len(self.tag) else ""
        for e in self:
            out += format(e, format_spec) + "\n"
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return [self.val[i].val for i in range(start, stop, step)]
        elif isinstance(item, int):
            return self.get(n=item).val
        elif isinstance(item, str):
            return self.get(tag=item).val
        elif isinstance(item, tuple):
            return self.get(tag=item[0]).val
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Property):
            out = copy.deepcopy(self)
            out.append(other)
            return out
        elif isinstance(other, Qoid):
            out = copy.deepcopy(self)
            for e in other:
                out.append(e)
            return out
        elif isinstance(other, list):
            out = copy.deepcopy(self)
            for e in other:
                out += e
            return out
        else:
            raise ValueError(f"Incompatible operands {type(self)} and {type(other)}")

    def __isub__(self, subtra):
        out = copy.deepcopy(self)
        if isinstance(subtra, (int, str, Property)):
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
        elif isinstance(subtra, list):
            out = copy.deepcopy(self)
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
        if isinstance(other, Property):
            out = Qoid(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return f"Qoid({self.tag}, {self.val})"

    def __reversed__(self):
        return Qoid(self.tag, val=reversed(self.val))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, Property):
                self.val[key] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[key] = Property(value[0], value[1])
            else:
                self.val[key] = Property(self.val[key].tag, value)
        elif isinstance(key, str):
            if isinstance(value, Property):
                self.val[self.index(key)] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[self.index(key)] = Property(value[0], value[1])
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

    def append(self, item: Property):
        to_add = copy.deepcopy(item)
        to_add.set_parent(self)
        self.val.append(to_add)

    def count(self, val):
        c = 0
        for e in self:
            c += 1 if e.tag == val else 0
        return c

    def extend(self, val: iter):
        for e in self:
            if not isinstance(val, Property):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Property is allowed")
        self.val.extend(val)

    """
    Get the first property which matches the given tag, or the property at the given index.
    If no argument is specified, returns all contents.
    """
    def get(self, tag=None, n=-1):
        if tag:
            tag = str(tag)
            out = Qoid("")
            for e in self:
                if e.tag == tag:
                    out.append(e)
            if len(out) > 1:
                return out
            elif len(out) == 1:
                return out.get(n=0)
            else:
                raise QoidError(f"'{tag}'")
        else:
            if len(self) > n >= 0:
                return self.val[n]
            raise IndexError("Qoid index out of range")

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            raise NoParentError("No parent exists for this Qoid")

    def all_of(self, tag: str):
        if tag:
            out = []
            for e in self:
                if e.tag == tag:
                    out.append(e.val)
            return out
        else:
            raise QoidError(f"{tag}")

    """Get the first index of a property with the given tag"""
    def index(self, item):
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
        if isinstance(index, int):
            if isinstance(obj, Property):
                self.val = self[:index] + [obj] + self[index:]
            elif isinstance(obj, Qoid):
                self.val = self[:index] + obj.val + self[index:]
            else:
                raise TypeError(f"Unsupported type '{type(obj)}', must be 'Property' or 'Qoid'")
        else:
            raise TypeError(f"Unsupported type '{type(obj)}', must be 'int'")

    def lower(self):
        return Qoid(self.tag.lower(), copy.deepcopy(self.val))

    def only(self, *items):
        out = []
        for each in items:
            if each in self:
                out.append(each)
        return Qoid(tag=self.tag, val=out)

    """Pack the contents of this qoid into a json-serialized format"""
    def pack(self): return {self.tag: [self.tags(), self.vals()]}

    """Remove either the property at the given index, with the given tag, or which matches the property given"""
    def pop(self, this=None):
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
        self.val = reversed(self.val)

    """
    Get the first property which matches the given tag, or the property at the given index.
    If no argument is specified, returns all contents.
    """
    def set(self, tag=None, index=-1, val=None):
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

    def set_parent(self, parent):
        if isinstance(parent, Index):
            if self.parent and self in self.parent:
                self.parent.pop(self)
            self.parent = parent
        else:
            raise TypeError(f"Qoid.parent must be Index, not {type(parent)}")

    def sort(self, ignore_case=True):
        self.val = sorted(self.val, key=Qoid.lower if ignore_case else None)

    """Get the set of all tags in this qoid"""
    def tags(self): return [e.tag for e in self]

    def without(self, *items):
        out = copy.deepcopy(self)
        for each in items:
            try:
                out.pop(each)
            except QoidError:
                # TODO
                # print(qe)
                pass
        return out

    """Get the set of all values in this qoid"""
    def vals(self): return [e.val if e.val else "" for e in self]


class Index:
    __doc__ = "An Index is a Qoid whose elements are Qoids"

    def __init__(self, tag: str = "Index", val=None, source=None, path=None, parent=None):
        self.tag = str(tag)
        self.val = []
        self.source = source
        self.path = path
        self.parent = parent
        if val:
            if isinstance(val, (Index, list)):
                for e in val:
                    if isinstance(e, Qoid):
                        self.append(e)
            else:
                raise ValueError(f"Invalid val type {type(val)}, must submit Index or list")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += other
        return out

    def __bool__(self): return bool(self.tag) or bool(self.val)

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
        if isinstance(other, Index):
            return all(e in other for e in self) and all(e in self for e in other)
        return False

    def __format__(self, format_spec):
        out = ""
        for e in self:
            out += format(e, format_spec) + "\n"
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return [self.val[i] for i in range(start, stop, step)]
        elif isinstance(item, int):
            return self.get(n=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        elif isinstance(item, tuple):
            if len(item) > 1:
                return self.get(tag=item[0])[item[1]]
            else:
                return self.get(tag=item[0])
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Qoid):
            out = copy.deepcopy(self)
            out.append(other)
            return out
        elif isinstance(other, Index):
            out = copy.deepcopy(self)
            for e in other:
                out.append(e)
            return out
        elif isinstance(other, list):
            out = copy.deepcopy(self)
            for e in other:
                out += e
            return out
        else:
            raise ValueError(f"Incompatible operands {type(self)} and {type(other)}")

    def __isub__(self, subtra):
        out = copy.deepcopy(self)
        if isinstance(subtra, (int, str, Qoid)):
            try:
                out.pop(subtra)
            except QoidError:
                pass
            return out
        elif isinstance(subtra, Index):
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
        elif isinstance(subtra, list):
            out = copy.deepcopy(self)
            for e in subtra:
                out -= e
            return out
        else:
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in Index.__isub__(self, subtra)")

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
            out = Index(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return f"Index({self.tag}, {self.val})"

    def __reversed__(self):
        return Index(self.tag, val=reversed(self.val))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, Qoid):
                self.val[key] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[key] = Qoid(value[0], value[1])
            else:
                self.val[key] = Qoid(self.val[key].tag, value)
        elif isinstance(key, str):
            if isinstance(value, Qoid):
                self.val[self.index(key)] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[self.index(key)] = Qoid(value[0], value[1])
            else:
                self.val[self.index(key)] = Qoid(key, value)
        else:
            raise TypeError(f"Unsupported type {type(key)} for 'key' in Qoid.__setitem__(self, key, value)")

    def __sub__(self, other):
        out = copy.deepcopy(self)
        out -= other
        return out

    def __str__(self):
        return format(self)

    def append(self, item: Qoid):
        to_add = copy.deepcopy(item)
        self.val.append(to_add)
        to_add.set_parent(self)

    def count(self, val):
        c = 0
        for e in self:
            c += 1 if e.tag == val else 0
        return c

    def extend(self, val: iter):
        for e in self:
            if not isinstance(val, Qoid):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Property is allowed")
        self.val.extend(val)

    """
    Get the first Qoid which matches the given tag, or the property at the given index.
    If no argument is specified, returns all contents.
    """

    def get(self, tag=None, n=-1):
        if tag:
            tag = str(tag)
            out = Index("")
            for e in self:
                if e.tag == tag:
                    out.append(e)
            if len(out) > 1:
                return out
            elif len(out) == 1:
                return out[0]
            else:
                raise QoidError(f"'{tag}'")
        else:
            if len(self) > n >= 0:
                return self.val[n]
            raise IndexError("Qoid index out of range")

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            raise NoParentError("No parent exists for this Index")

    def glossary(self):
        out = Qoid(self.tag)
        for e in self:
            out += Property(e.tag)
        return out

    """Get the first index of a property with the given tag"""
    def index(self, item):
        if isinstance(item, Qoid):
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
        if isinstance(index, int):
            if isinstance(obj, Qoid):
                self.val = self[:index] + [obj] + self[index:]
            elif isinstance(obj, Index):
                self.val = self[:index] + obj.val + self[index:]
            else:
                raise TypeError(f"Unsupported type '{type(obj)}', must be 'Property' or 'Qoid'")
        else:
            raise TypeError(f"Unsupported type '{type(obj)}', must be 'int'")

    def lower(self):
        return Index(self.tag.lower(), copy.deepcopy(self.val))

    def only(self, *items):
        out = []
        for each in items:
            if each in self:
                out.append(each)
        return Index(tag=self.tag, val=out)

    @staticmethod
    def open(source: str):
        source = source.replace("/", "\\")
        if os.path.isfile(source):
            with open(source, "r") as f:
                if source.endswith(".json"):
                    content = json.load(fp=f)
                else:
                    content = [l.replace("\n", "") for l in f.readlines()]
                tag = source.split("\\")[-1]
                out = Index.parse(content, tag=tag)
                out.source = source
                return out
        else:
            raise FileNotFoundError(f"Invalid source specified: {source}")

    """Pack the contents of this index into a json-serialized format"""
    def pack(self):
        return {q.tag: [q.tags(), q.vals()] for q in self}

    def path_priority(self):
        if self.path:
            return self.path
        elif self.source:
            return self.source
        else:
            return self.tag + (".cxr" if not self.tag.endswith(q_fext) else "")

    def create_path(self):
        p = self.path_priority()
        if self.parent:
            out = self.parent.create_path()
            return os.path.join(out, p)
        else:
            return p

    @staticmethod
    def parse(source, tag: str = "Parsed Index"):
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
            return Index(tag=tag, val=val)
        elif isinstance(source, dict):
            qoids = []
            for key, value in source.items():
                # Step 1: ensure the tag is a string, and value is a 2-length list
                if isinstance(key, str) and isinstance(value, list) and len(value) == 2:
                    t = value[0]
                    v = value[1]
                    # Step 2: ensure both value elements are lists
                    if isinstance(t, list) and isinstance(v, list) and len(t) == len(v):
                        # Step 3: ensure all elements are stringsytz
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
            return Index(tag=tag, val=qoids)
        else:
            raise TypeError(f"Illegal source of type {type(source)}: must be list or dict")

    """Remove either the Qoid at the given index, with the given tag, or which matches the property given"""
    def pop(self, this=None):
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
        elif isinstance(this, Qoid):
            for e in self:
                if e == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError(f"'{this.tag}: {len(this)} item(s)'")
        else:
            raise TypeError(f"Unsupported type {type(this)}, must be int, str, or Property")

    def reverse(self):
        self.val = reversed(self.val)

    def sort(self, ignore_case=True):
        self.val = sorted(self.val, key=Index.lower if ignore_case else None)

    def save(self, echo=False, is_json=False):
        with open(self.create_path() + (".json" if is_json else ""), 'w+') as out:
            if is_json:
                json.dump(obj=self.pack(), fp=out)
            else:
                out.write(format(self))
        if echo:
            print(f"Index {self.tag} saved to {self.create_path()}")

    def set_parent(self, parent):
        if isinstance(parent, Register):
            if self.parent and self in self.parent:
                self.parent.pop(self)
            self.parent = parent
        else:
            raise TypeError(f"Index.parent must be Register, not {type(parent)}")

    """Get the set of all tags in this index"""
    def tags(self):
        return [e.tag for e in self]

    def without(self, *items):
        out = copy.deepcopy(self)
        for each in items:
            try:
                out.pop(each)
            except QoidError:
                # TODO
                # print(qe)
                pass
        return out

    def vals(self):
        return [e.val for e in self]


class Register:
    __doc__ = "A register is a qoid whose elements are all indices"

    def __init__(self, tag: str = "Register", val=None, source=None, path=None, parent=None):
        self.tag = str(tag)
        self.val = []
        self.source = source
        self.path = path
        self.parent = parent
        if val:
            if isinstance(val, (Register, list)):
                for e in val:
                    if isinstance(e, (Register, Index)):
                        self.append(e)
            else:
                raise ValueError(f"Invalid val type {type(val)}, must submit Index or list")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += other
        return out

    def __bool__(self): return bool(self.tag) or bool(self.val)

    def __bytes__(self):
        return str.encode(format(self))

    def __contains__(self, item):
        if isinstance(item, (Register, Index)):
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
            return all(e in other for e in self) and all(e in self for e in other)
        return False

    def __format__(self, format_spec):
        out = ""
        for e in self:
            out += f"/ {e.tag}\n\n"
            out += format(e, format_spec)
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return [self.val[i] for i in range(start, stop, step)]
        elif isinstance(item, int):
            return self.get(n=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        elif isinstance(item, tuple):
            return self.get(item[0])[item[1:]]
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, (Index, Register)):
            out = copy.deepcopy(self)
            out.append(other)
            return out
        elif isinstance(other, Qoid):
            out = copy.deepcopy(self)
            out.get_meta().append(other)
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
        if isinstance(subtra, (int, str, Index)):
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
        elif isinstance(subtra, list):
            out = copy.deepcopy(self)
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
        if isinstance(other, Index):
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
            if isinstance(value, Index):
                self.val[key] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[key] = Index(value[0], value[1])
            else:
                self.val[key] = Index(self.val[key].tag, value)
        elif isinstance(key, str):
            if isinstance(value, Index):
                self.val[self.index(key)] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[self.index(key)] = Index(value[0], value[1])
            else:
                self.val[self.index(key)] = Index(key, value)
        else:
            raise TypeError(f"Unsupported type {type(key)} for 'key' in Qoid.__setitem__(self, key, value)")

    def __sub__(self, other):
        out = copy.deepcopy(self)
        out -= other
        return out

    def __str__(self):
        return format(self)

    def append(self, item):
        if isinstance(item, (Register, Index)):
            to_add = copy.deepcopy(item)
            to_add.set_parent(self)
            self.val.append(to_add)
        else:
            raise ValueError()

    def broadcast(self, key: str):
        out = self.clone()
        var_set = out.get_meta()[key]
        for element in out:
            for qoid in (element.get_meta() if isinstance(element, Register) else element):
                for line in qoid:
                    for var in var_set:
                        if f"@{var.tag}@" in line.val:
                            line.val = line.val.replace(f"@{var.tag}@", var.val)
        return out

    def clone(self):
        return copy.deepcopy(self)

    def count(self, val):
        c = 0
        for e in self:
            c += 1 if e.tag == val else 0
        return c

    def path_priority(self):
        if self.path:
            return self.path
        elif self.source:
            return self.source
        else:
            return self.tag + (".cxr" if not self.tag.endswith(q_fext) else "")

    def create_path(self):
        p = self.path_priority()
        if self.parent:
            out = self.parent.create_path()
            return os.path.join(out, p)
        else:
            return p

    def extend(self, val):
        for e in self:
            if not isinstance(val, (Register, Index)):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Register or Index is allowed")
        self.val.extend(val)

    """Return the value at the given"""
    def get(self, tag=None, n=-1):
        if tag:
            tag = str(tag)
            out = Register("")
            for e in self:
                if e.tag == tag:
                    out.append(e)
            if len(out) > 1:
                return out
            elif len(out) == 1:
                return out[0]
            else:
                raise QoidError(f"'{tag}'")
        else:
            if len(self) > n >= 0:
                return self.val[n]
            raise IndexError("Qoid index out of range")

    def get_meta(self):
        if ".meta" in self:
            return self[".meta"]
        else:
            self.append(Index(tag=".meta", parent=self))
            return self[".meta"]

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            raise NoParentError("No parent exists for this Register")

    def glossary(self):
        out = Register(self.tag)
        for e in self:
            out += e.glossary()
        return out

    def index(self, item):
        if isinstance(item, (Register, Index)):
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
        if isinstance(index, int):
            if isinstance(obj, Index):
                self.val = self[:index] + [obj] + self[index:]
            elif isinstance(obj, Register):
                self.val = self[:index] + obj.val + self[index:]
            else:
                raise TypeError(f"Unsupported type '{type(obj)}', must be 'Property' or 'Qoid'")
        else:
            raise TypeError(f"Unsupported type '{type(obj)}', must be 'int'")

    def lower(self):
        return Register(self.tag.lower(), copy.deepcopy(self.val))

    def only(self, *items):
        out = []
        for each in items:
            if each in self:
                out.append(each)
        return Register(tag=self.tag, val=out)

    @staticmethod
    def open(path: str):
        path = path.replace("/", "\\")
        if os.path.isdir(path):
            out = Register(tag=path.split("\\")[-1])
            out.path = path.rsplit("\\", 1)[0]
            for e in os.listdir(path):
                try:
                    if os.path.isdir(os.path.join(path, e)) and e.endswith(q_dirext):
                        i = Register.open(os.path.join(path, e))
                    elif e.endswith((".cxr", ".meta", ".txt")):
                        i = Index.open(os.path.join(path, e))
                    else:
                        raise QoidError("Invalid file type")
                    out += i
                except QoidError:
                    print(f"Ignoring invalid file type at {os.path.join(path, e)}")
            return out
        else:
            raise NotADirectoryError(f"Invalid source specified: {path}")

    def pack(self):
        out = {}
        reg = []
        ind = []
        for e in self:
            if isinstance(e, Register):
                reg.append(e)
            else:
                ind.append(e)
        out.update({"Register": {e.tag: e.pack() for e in reg}})
        out.update({"Index": {e.tag: e.pack() for e in ind}})
        return {self.tag: [self.tags(), self.vals()]}

    def pop(self, this=None):
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
        elif isinstance(this, (Register, Index)):
            for e in self:
                if e == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError(f"'{this.tag}: {len(this)} item(s) not found in {self.tag}'")
        else:
            raise TypeError(f"Unsupported type {type(this)}, must be int, str, Register, or Index")

    def reverse(self):
        self.val = reversed(self.val)

    def sort(self, ignore_case=True):
        self.val = sorted(self.val, key=Register.lower if ignore_case else None)

    def save(self, echo=False, echo_all=False):
        p = self.create_path()
        if not os.path.isdir(p):
            os.mkdir(p)
        for e in self:
            if isinstance(e, Register):
                p = e.create_path()
                if not os.path.isdir(p):
                    os.mkdir(p)
            e.save(echo=echo_all)
        if echo:
            print(f"Register {self.tag} saved to {self.create_path()}")

    def set_parent(self, parent):
        if isinstance(parent, Register):
            if self.parent and self in self.parent:
                self.parent.pop(self)
            self.parent = parent
        else:
            raise TypeError(f"Register.parent must be Register, not {type(parent)}")

    def tags(self):
        return [e.tag for e in self]

    def without(self, *items):
        out = copy.deepcopy(self)
        for each in items:
            try:
                out.pop(each)
            except QoidError:
                # TODO
                # print(qe)
                pass
        return out

    def vals(self):
        return [e.val for e in self]
