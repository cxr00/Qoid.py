"""
Qoid is a database-like serialization API for reading and writing miscellaneous data in a readable way
"""

import os
import json
import copy


class QoidError(KeyError): pass


class Property:
    """
    A Property is a tag-value pair, where the tag is used to refer to the value given
    """

    def __init__(self, tag: str, val=None):
        self.tag = str(tag)
        self.val = val

    def __add__(self, other):
        if isinstance(other, Property):
            return Qoid("{0} + {1}".format(self.tag, other.tag), [self, other])
        else:
            return NotImplemented

    def __bytes__(self):
        return str.encode(format(self))

    def __eq__(self, other):
        if isinstance(other, Property):
            return self.tag == other.tag and self.val == other.val
        return False

    def __format__(self, format_spec):
        if format_spec:
            return self.tag + ((format_spec + " " + self.val) if self.val else "")
        else:
            return self.tag + ((": " + self.val) if self.val else "")

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

    def __repr__(self):
        return "Property({0}, {1})".format(self.tag, self.val)

    def __str__(self):
        return str(self.val)

    def lower(self):
        return Property(self.tag.lower(), copy.deepcopy(self.val))

    """Set the property's tag, value, or both"""
    def set(self, tag=None, val=None):
        if tag:
            self.tag = tag
        if val:
            self.val = val


class Qoid:
    """
    A Qoid is a set of Properties. Each Qoid has a tag which functions as a key.
    """

    def __init__(self, tag: str = "", val=None):
        self.tag = str(tag)
        self.val = []
        if val:
            if isinstance(val, Qoid) or isinstance(val, list):
                for e in val:
                    if isinstance(e, Property):
                        self.append(e)
            else:
                raise ValueError("Invalid val type {0}, must submit Qoid or list".format(type(val)))

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
            raise ValueError("Invalid type {0}, must use int or str".format(type(key)))

    def __eq__(self, other):
        if isinstance(other, Qoid):
            return all(e in other for e in self) and all(e in self for e in other)
        return False

    def __format__(self, format_spec):
        out = "#{0}\n".format(self.tag)
        for e in self:
            out += format(e, format_spec) + "\n"
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [self.val[i] for i in range(item.start, item.stop, item.step)]
        elif isinstance(item, int):
            return self.get(index=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError("Invalid type {0}, must use slice, int, or str".format(type(item)))

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Property):
            out = copy.deepcopy(self)
            out.append(copy.deepcopy(other))
            return out
        elif isinstance(other, Qoid):
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

    def __radd__(self, other):
        if isinstance(other, Property):
            out = Qoid(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return "Qoid({0}, {1})".format(self.tag, self.val)

    def __reversed__(self):
        return Qoid(self.tag, val=reversed(self.val))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.val[key] = value
        elif isinstance(key, str):
            self.val[self.index(key)] = value
        else:
            raise TypeError("Unsupported type {0} for key in Qoid.__setitem__(self, key, value)".format(type(key)))

    def __sub__(self, subtra):
        out = copy.deepcopy(self)
        if isinstance(subtra, int) or isinstance(subtra, str) or isinstance(subtra, Property):
            try:
                out.remove(subtra)
            except QoidError:
                pass
            return out
        elif isinstance(subtra, Qoid):
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
            raise TypeError("Unsupported type {0} for subtrahend in Qoid.__sub__(self, subtra)".format(type(subtra)))

    def __str__(self):
        return format(self)

    def append(self, item: Property):
        self.val.append(item)

    def count(self, val):
        c = 0
        for e in self:
            c += 1 if e.tag == val else 0
        return c

    def extend(self, val: iter):
        for e in self:
            if not isinstance(val, Property):
                raise TypeError("Unsupported {0} in iterable, only Property is allowed".format(type(e)))
        self.val.extend(val)

    def find(self, tag: str):
        for e in self:
            if e.tag == tag:
                return e
        raise QoidError("'{0}'".format(tag))

    """
    Get the first property which matches the given tag, or the property at the given index.
    If no argument is specified, returns all contents.
    """
    def get(self, tag=None, index=-1):
        if tag is None and index == -1:
            return self.val
        elif tag is not None:
            tag = str(tag)
            for e in self:
                if e.tag == tag:
                    return e.val
            raise QoidError("'{0}'".format(tag))
        else:
            if len(self) > index >= 0:
                return self[index]
            raise IndexError("Qoid index out of range".format(index))

    """Get the first index of a property with the given tag"""
    def index(self, item):
        if isinstance(item, Property):
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
            raise TypeError("Invalid type {0}, must use Property or str".format(type(item)))

    def insert(self, index, obj):
        if isinstance(index, int):
            if isinstance(obj, Property):
                self.val = self[:index] + [obj] + self[index:]
            elif isinstance(obj, Qoid):
                self.val = self[:index] + obj.val + self[index:]
            else:
                raise TypeError("Unsupported type '{0}', must be 'Property' or 'Qoid'".format(type(obj)))
        else:
            raise TypeError("Unsupported type '{0}', must be 'int'".format(type(obj)))

    """Pack the contents of this qoid into a json-serialized format"""
    def pack(self): return {self.tag: [self.tags(), self.vals()]}

    def pop(self, index=-1):
        if index == -1:
            return self.val.pop()
        elif len(self) > index >= 0:
            return self.val.pop(index)
        else:
            raise IndexError("Qoid index out of range")

    """Remove either the property at the given index, with the given tag, or which matches the property given"""
    def remove(self, this):
        if isinstance(this, int):
            if len(self) > this >= 0:
                return self.val.pop(this)
            raise IndexError("Qoid index out of range")
        elif isinstance(this, str):
            for e in self:
                if e.tag == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError("'{0}'".format(this))
        elif isinstance(this, Property):
            for e in self:
                if e == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError("'{0}'".format(format(this)))
        else:
            raise TypeError("Unsupported type {0}, must be int, str, or Property".format(type(this)))

    def reverse(self):
        self.val = reversed(self.val)

    def sort(self, ignore_case=True):
        self.val = sorted(self.val, key=Property.lower if ignore_case else None)

    """Get the set of all tags in this qoid"""
    def tags(self): return [e.tag for e in self]

    """Get the set of all values in this qoid"""
    def vals(self): return [e.val for e in self]


class Index:
    """
    An Index is a Qoid whose elements are iterable; thus an Index may contain Indices
    """

    def __init__(self, tag: str, val=None):
        self.tag = str(tag)
        self.val = []
        if val:
            if isinstance(val, Index) or isinstance(val, list):
                for e in val:
                    if isinstance(e, Qoid):
                        self.append(e)
            else:
                raise ValueError("Invalid val type {0}, must submit Index or list".format(type(val)))

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
            raise ValueError("Invalid type {0}, must use int or str".format(type(key)))

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
            return [self.val[i] for i in range(item.start, item.stop, item.step)]
        elif isinstance(item, int):
            return self.get(index=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError("Invalid type {0}, must use slice, int, or str".format(type(item)))

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Qoid):
            out = copy.deepcopy(self)
            out.append(copy.deepcopy(other))
            return out
        elif isinstance(other, Index):
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

    def __radd__(self, other):
        if isinstance(other, Qoid):
            out = Index(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return "Index({0}, {1})".format(self.tag, self.val)

    def __reversed__(self):
        return Index(self.tag, val=reversed(self.val))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.val[key] = value
        elif isinstance(key, str):
            self.val[self.index(key)] = value
        else:
            raise TypeError("Unsupported type {0} for 'key' in Qoid.__setitem__(self, key, value)".format(type(key)))

    def __sub__(self, subtra):
        out = copy.deepcopy(self)
        if isinstance(subtra, int) or isinstance(subtra, str) or isinstance(subtra, Qoid):
            try:
                out.remove(subtra)
            except QoidError:
                pass
            return out
        elif isinstance(subtra, Index):
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
            raise TypeError("Unsupported type {0} for subtrahend in Index.__sub__(self, subtra)".format(type(subtra)))

    def __str__(self):
        return format(self)

    def append(self, item: Qoid):
        self.val.append(item)

    def count(self, val):
        c = 0
        for e in self:
            c += 1 if e.tag == val else 0
        return c

    def extend(self, val: iter):
        for e in self:
            if not isinstance(val, Qoid):
                raise TypeError("Unsupported {0} in iterable, only Property is allowed".format(type(e)))
        self.val.extend(val)

    def find(self, tag: str):
        for e in self:
            if e.tag == tag:
                return e
        raise QoidError("'{0}'".format(tag))

    """
    Get the first Qoid which matches the given tag, or the property at the given index.
    If no argument is specified, returns all contents.
    """

    def get(self, tag=None, index=-1):
        if tag is None and index == -1:
            return self.val
        elif tag is not None:
            tag = str(tag)
            for e in self:
                if e.tag == tag:
                    return e.val
            raise QoidError("'{0}'".format(tag))
        else:
            if len(self) > index >= 0:
                return self[index]
            raise IndexError("Qoid index out of range".format(index))

    """Get the first index of a property with the given tag"""
    def index(self, item):
        if isinstance(item, Qoid):
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
            raise TypeError("Invalid type {0}, must use Property or str".format(type(item)))

    def insert(self, index, obj):
        if isinstance(index, int):
            if isinstance(obj, Qoid):
                self.val = self[:index] + [obj] + self[index:]
            elif isinstance(obj, Index):
                self.val = self[:index] + obj.val + self[index:]
            else:
                raise TypeError("Unsupported type '{0}', must be 'Property' or 'Qoid'".format(type(obj)))
        else:
            raise TypeError("Unsupported type '{0}', must be 'int'".format(type(obj)))

    """Pack the contents of this index into a json-serialized format"""
    def pack(self):
        return {q.tag: [q.tags(), q.vals()] for q in self}

    def pop(self, index=-1):
        if index == -1:
            return self.val.pop()
        elif len(self) > index >= 0:
            return self.val.pop(index)
        else:
            raise IndexError("Qoid index out of range")

    """Remove either the Qoid at the given index, with the given tag, or which matches the property given"""
    def remove(self, this):
        if isinstance(this, int):
            if len(self) > this >= 0:
                return self.val.pop(this)
            raise IndexError("Qoid index out of range")
        elif isinstance(this, str):
            for e in self:
                if e.tag == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError("'{0}'".format(this))
        elif isinstance(this, Qoid):
            for e in self:
                if e == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError("'{0}: {1} item(s)'".format(this.tag, len(this)))
        else:
            raise TypeError("Unsupported type {0}, must be int, str, or Property".format(type(this)))

    def reverse(self):
        self.val = reversed(self.val)

    def sort(self, ignore_case=True):
        self.val = sorted(self.val, key=Property.lower if ignore_case else None)

    """Get the set of all tags in this qoid"""

    def tags(self):
        return [e.tag for e in self]
