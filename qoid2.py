import copy
import os
import json

from cxr import *

# Permitted file and directory extensions to read as Qoid
q_fext = (".cxr", ".txt")
q_dirext = tuple(".cxr")


class Property(Complexor):
    __doc__ = "A Property is a tag-value pair, where the tag is used to refer to the value given"

    def __init__(self, tag: str ="Property", val=None, parent=None):
        super().__init__(tag, val, tuple(str))
        self.tag = str(tag)
        self.val = val
        self.parent = parent

    def __add__(self, other):
        if isinstance(other, Property):
            return Qoid(f"{self.tag} + {other.tag}", [self, other])
        else:
            return NotImplemented

    def __getitem__(self, item): return NotImplemented

    def __str__(self):
        return self.tag + (f": {self.val}" if self.val else "")

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            raise NoParentError("No parent exists for this Property")

    """Set the property's tag, value, or both"""
    def set(self, tag=None, val=None):
        if tag:
            self.tag = tag
        if val:
            self.val = val


class Qoid(Complexor):
    __doc__ = "A Qoid is a set of Properties. Each Qoid has a tag which functions as a key."

    def __init__(self, tag: str="Qoid", val=None, parent=None):
        super().__init__(tag, val, tuple(Property))
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

    def __str__(self):
        out = f"#{self.tag}\n" if len(self.tag) else ""
        for e in self:
            out += str(e) + "\n"
        return out

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

    def only(self, *items):
        out = []
        for each in items:
            if each in self:
                out.append(each)
        return Qoid(tag=self.tag, val=out)

    """Pack the contents of this qoid into a json-serialized format"""
    def pack(self): return {self.tag: [self.tags(), self.vals()]}

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

    def update_parent(self):
        for e in self:
            e.parent = self

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


class Index(Complexor):
    __doc__ = "An Index is a Qoid whose elements are Qoids"

    def __init__(self, tag: str = "Index", val=None, parent=None):
        super().__init__(tag, val, tuple(Qoid))
        self.tag = str(tag)
        self.val = []
        self.source = None
        self.path = None
        self.parent = parent
        if val:
            if isinstance(val, (Index, list)):
                for e in val:
                    if isinstance(e, Qoid):
                        self.append(e)
            else:
                raise ValueError(f"Invalid val type {type(val)}, must submit Index or list")

    def __str__(self):
        out = ""
        for e in self:
            out += str(e) + "\n"
        return out

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

    def save(self, echo=False, is_json=False):
        with open(self.create_path() + (".json" if is_json else ""), 'w+') as out:
            if is_json:
                json.dump(obj=self.pack(), fp=out)
            else:
                out.write(format(self))
        if echo:
            print(f"Index {self.tag} saved to {self.create_path()}")

    def update_parent(self):
        for e in self:
            e.parent = self
            e.update_parent()

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


class Register(Complexor):

    __doc__ = "A register is a qoid whose elements are all indices"

    def __init__(self, tag: str = "Register", val=None, parent=None):
        super().__init__(tag, val, tuple(Index, self.__class__))
        self.tag = str(tag)
        self.val = []
        self.source = None
        self.path = None
        self.parent = parent
        if val:
            if isinstance(val, (Register, list)):
                for e in val:
                    if isinstance(e, (Register, Index)):
                        self.append(e)
            else:
                raise ValueError(f"Invalid val type {type(val)}, must submit Index or list")

    def __str__(self):
        out = ""
        for e in self:
            out += f"/ {e.tag}\n\n"
            out += str(e)
        return out

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
                    elif e.endswith(q_fext):
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

    def save(self, echo=False, echo_all=False):
        p = self.create_path()
        if not os.path.isdir(p):
            os.mkdir(p)
        for e in self:
            if isinstance(e, Register):
                p = e.create_path()
                if not os.path.isdir(p):
                    os.mkdir(p)
            # print(f"{self.tag}\t{e.tag}\t{e.create_path()}")
            e.save(echo=echo_all)
        if echo:
            print(f"Register {self.tag} saved to {self.create_path()}")

    def update_parent(self):
        for e in self:
            e.parent = self
            e.update_parent()

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
