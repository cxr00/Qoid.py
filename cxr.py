import copy


class QoidError(KeyError):
    __doc__ = "A QoidError is raised for KeyErrors and KeyError-like problems which occur specifically in qoid.py."


class QoidParseError(SyntaxError):
    __doc__ = "A QoidParseError is raised for any SyntaxError involving the parsing of a file using Co-oid markup."


class NoParentError(TypeError):
    __doc__ = "A NoParentError is raised when attempting parent-requiring functions on Qoids where none exist"


class NoPathError(ValueError):
    __doc__ = "A NoSourcePathError is raised when attempting to save anything without a source, root, or target file path"


class Complexor:

    # all possible content types for the value set
    # eg Qoid contains Property, Register contains Register and Index
    content_types = tuple()

    # the primary child type of the value set;
    # eg Index parents Qoid, Register parents Index
    child_type = None

    def __init__(self, tag: str, val=None, contents: tuple=None, child_type: type=None):
        # TODO
        self.tag = ""
        self.val = []
        self.content_types = contents
        self.child_type = child_type if child_type else self.content_types[0]
        pass

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += other
        return out

    def __bool__(self): return bool(self.tag) or bool(self.val)

    def __bytes__(self): return str.encode(format(self))

    def __contains__(self, item):
        if isinstance(item, self.content_types):
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
        """
        Equality is the state of tag and value being an exact match
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.tag == other.tag\
            and all(e in other for e in self)\
            and all(e in self for e in other)

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
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __iadd__(self, other):
        if isinstance(other, self.content_types):
            out = copy.deepcopy(self)
            out.append(other.__class__(other.tag, other.val))
            return out
        elif isinstance(other, self.__class__):
            out = copy.deepcopy(self)
            for e in other:
                out.append(e.__class__(e.tag, e.val))
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
        if isinstance(subtra, (int, str, self.child_type)):
            try:
                out.pop(subtra)
            except QoidError:
                pass
            return out
        elif isinstance(subtra, self.content_types):
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
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in {self.__name__}.__isub__(self, subtra)")

    def __iter__(self):
        return iter(self.val)

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return len(self.val)

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self == other

    def __radd__(self, other):
        if isinstance(other, self.content_types):
            out = self.__class__(self.tag, val=[other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return f"{self.__name__} ({self.tag}, {self.val})"

    def __reversed__(self):
        return self.__class__(self.tag, val=reversed(self.val))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, self.content_types):
                self.val[key] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[key] = self.child_type(value[0], value[1])
            else:
                self.val[key] = self.child_type(self.val[key].tag, value)
        elif isinstance(key, str):
            if isinstance(value, self.content_types):
                self.val[self.index(key)] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[self.index(key)] = self.child_type(value[0], value[1])
            else:
                self.val[self.index(key)] = self.child_type(key, value)
        else:
            raise TypeError(f"Unsupported type {type(key)} for key in Qoid.__setitem__(self, key, value)")

    def __sub__(self, subtra):
        out = copy.deepcopy(self)
        out -= subtra
        return out

    def append(self, item):
        if isinstance(item, self.content_types):
            to_add = copy.deepcopy(item) if item.parent else item
            to_add.parent = self
            self.val.append(to_add)
        else:
            raise TypeError(f"Unsupported type {type(item)}, must be {self.content_types}")

    def count(self, tag):
        out = 0
        for e in self:
            out += 1 if e.tag == tag else 0
        return out

    def extend(self, val):
        for e in self:
            if not isinstance(val, self.content_types):
                raise TypeError(f"Unsupported {type(e)} in iterable, only {self.content_types} is allowed")
        self.val.extend(val)

    def get(self, tag=None, n=-1):
        if tag:
            tag = str(tag)
            out = self.__class__(tag)
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

    def index(self, item):
        if isinstance(item, self.content_types):
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
            raise TypeError(f"Invalid type {type(item)}, must use {self.content_types} or str")

    def insert(self, index, obj):
        if isinstance(index, int):
            if isinstance(obj, self.child_type):
                self.val = self[:index] + [obj] + self[index:]
            elif isinstance(obj, self.__class__):
                self.val = self[:index] + obj.val + self[index:]
            else:
                raise TypeError(f"Unsupported type {type(obj)}, must be {self.child_type} or {self.__name__}")
        else:
            raise TypeError(f"Unsupported index '{type(obj)}', must be int")

    def lower(self): return self.__class__(self.tag.lower(), copy.deepcopy(self.val))

    def pop(self, this=None):
        if not this:
            return self.val.pop()
        elif isinstance(this, int):
            if len(self) > this >= 0:
                return self.val.pop(this)
            else:
                raise IndexError("Index out of range")
        elif isinstance(this, str):
            for e in self:
                if e.tag == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError(f"'{this}'")
        elif isinstance(this, self.content_types):
            for e in self:
                if e == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError(f"'{this.tag}: {len(this)} item(s) not found in {self.tag}'")
        else:
            raise TypeError(f"Unsupported type {type(this)}, must be int, str, Register, or Index")

    def reverse(self): self.val = reversed(self.val)

    def sort(self, ignore_case=True): self.val = sorted(self.val, key=self.__class__.lower if ignore_case else None)

    def tags(self): return [e.tag for e in self]

    def upper(self): return self.__class__(self.tag.upper(), copy.deepcopy(self.val))

    def vals(self): return [e.val for e in self]
