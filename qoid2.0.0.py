import copy


class QoidError(KeyError):
    __doc__ = "A QoidError is raised for KeyErrors and KeyError-like problems which occur specifically in qoid.py."


class QoidParseError(SyntaxError):
    __doc__ = "A QoidParseError is raised for any SyntaxError involving the parsing of a file using Co-oid markup."


class Complexor:

    # all possible content types for the value set
    # eg Qoid contains Property, Register contains Register and Index
    content_types = tuple()

    # the primary child type of the value set;
    # eg Index parents Qoid, Register parents Index
    child_type = None

    def __init__(self, tag: str, val):
        # TODO
        self.tag = tag
        self.val = val
        pass

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += other
        return out

    def __bytes__(self):
        return str.encode(format(self))

    def __contains__(self, item):
        if isinstance(item, Complexor.content_types):
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
            raise ValueError("Invalid type {0}, must use int or str".format(type(key)))

    def __eq__(self, other):
        """
        Equality is the state of tag and value being an exact match
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.tag == other.tag\
            and all(e in other for e in self)\
            and all(e in self for e in other)

    def __format__(self, format_spec):
        # TODO
        pass

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [self.val[i].val for i in range(item.start, item.stop, item.step)]
        elif isinstance(item, int):
            return self.get(index=item).val
        elif isinstance(item, str):
            return self.get(tag=item).val
        else:
            raise ValueError("Invalid type {0}, must use slice, int, or str".format(type(item)))

    def __gt__(self, other):
        return self.tag > other.tag

    def __iadd__(self, other):
        if isinstance(other, self.content_types):
            out = copy.deepcopy(self)
            out.append(copy.deepcopy(other))
            return out
        elif isinstance(other, self.__class__):
            out = copy.deepcopy(self)
            for e in other:
                out.append(e)
            return out
        else:
            raise ValueError("Incompatible operands {0} and {1}".format(type(self), type(other)))

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
            self.val[key] = value
        elif isinstance(key, str):
            self.val[self.index(key)] = value
        else:
            raise TypeError(f"Unsupported type {type(key)} for key in {self.__name__}.__setitem__(self, key, value)")

    def __str__(self):
        return format(self)

    def __sub__(self, subtra):
        out = copy.deepcopy(self)
        if isinstance(subtra, (int, str, self.content_types)):
            try:
                out.remove(subtra)
            except QoidError:
                pass
            return out
        elif isinstance(subtra, self.__class__):
            for e in subtra:
                if e.val is None:
                    try:
                        out.remove(e.tag)
                    except QoidError:
                        pass
                else:
                    try:
                        out.remove(e)
                    except QoidError:
                        pass
            return out
        else:
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in {self.__name__}.__sub__(self, subtra)")

    def append(self, item):
        if isinstance(item, self.content_types):
            self.val.append(item)
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

    def get(self, tag=None, index=-1):
        if tag:
            tag = str(tag)
            for e in self:
                if e.tag == tag:
                    return e
            raise QoidError("'{0}'".format(tag))
        else:
            if len(self) > index >= 0:
                return self.val[index]
            raise IndexError(f"{self.__name__} index out of range")

    def index(self, item):
        if isinstance(item, self.content_types):
            for e in self:
                if item == e:
                    return self.val.index(e)
            raise QoidError("'{0}'".format(item))
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return self.val.index(e)
            raise QoidError("'{0}'".format(format(item)))
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

    def lower(self):
        return self.__class__(self.tag.lower(), copy.deepcopy(self.val))

    def pop(self, index=-1):
        if index == -1:
            return self.val.pop()
        elif len(self) > index >= 0:
            return self.val.pop(index)
        else:
            raise IndexError(f"{self.__name__} index out of range")


print(Complexor.__name__)
