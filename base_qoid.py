import copy


class BaseQoid:

    _set_assoc = {}

    __doc__ = "The base class for all Qoid objects"

    def __init__(self, tag: str = "BaseQoid", val=None, source=None, path=None, parent=None):
        self.tag = tag
        self.val = val
        self.source = source
        self.path = path
        self.parent = parent
        self.T = BaseQoid._set_assoc[self.__class__.__name__]

    def __bool__(self):
        return bool(self.tag)

    def __delitem__(self, key):
        if isinstance(key, int):
            del self.val[key]
        elif isinstance(key, str):
            del self.val[self.index(key)]
        else:
            raise ValueError(f"Invalid type {type(key)}, must use int or str")

    def __eq__(self, other):
        return self.tag == other.tag and self.val == other.val

    def __format__(self, format_spec):
        pass

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return [self.val[i] for i in range(start, stop, step)]
        elif isinstance(item, int):
            return self.get(index=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError(f"Invalid tag type {type(item)} for {self.__name__}")

    def __gt__(self, other):
        return self.tag > other.tag

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return len(self.val)

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __setitem__(self, key, value):
        # T = BaseQoid._set_assoc[self.__name__]
        if isinstance(key, int):
            if isinstance(value, self.T):
                self.val[key] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[key] = self.T(value[0], value[1])
            else:
                self.val[key] = self.T(self.val[key].tag, value)
        elif isinstance(key, str):
            if isinstance(value, self.T):
                self.val[self.index(key)] = value
            elif isinstance(value, tuple) and len(value) == 2:
                self.val[self.index(key)] = self.T(value[0], value[1])
            else:
                self.val[self.index(key)] = self.T(key, value)
        else:
            raise TypeError(f"Unsupported type {type(key)} for key in {self.__name__}.__setitem__(self, key, value)")

    def append(self, item):
        if isinstance(item, type(self.T())):
            to_add = copy.deepcopy(item)
            to_add.set_parent(self)
            self.val.append(to_add)
        else:
            raise QoidError("Cannot add {type(item)} to {self.__class__}")

    def get(self, tag=None, index=None):
        pass

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            raise NoParentError(f"No parent exists for this {self.__name__}")

    def index(self, item):
        if isinstance(item, self.T):
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
            raise TypeError(f"Invalid type {type(item)}, must use {self.T.__name__} or str")

    def set_parent(self, parent):
        self.parent = parent

    pass

