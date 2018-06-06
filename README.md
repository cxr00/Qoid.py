# Qoid.py

Qoid is a simple markup language which uses tag-value pairs to record data in traditional files and folders with the added depth of tagged elements within each file.

All objects in qoid.py have string tags, with the values adding recursive depth. A Qoid tags a list of Properties, an Index tags a list of Qoids, and a Register tags a list of Indices and other Registers.

```python
>>> a = Property("tag", "value")
>>> b = Property("tag2", "value2")
>>> c = Qoid("qoid tag", [a, b])
>>> d = Qoid("other qoid tag", [b, a, b])
>>> e = Index("test index", [c, d])
>>>> print(e)
/ test index

#qoid tag
tag: value
tag2: value2

#other qoid tag
tag2: value2
tag: value
tag2: value2
```

## Basic usage

Property and Qoid object can be created with four parameters:

*class qoid.Property(tag: str="Property", val=None, parent=None)*  
*class qoid.Qoid(tag: str="Qoid", val=None, parent=None)*

While Indices and Registers have two additional parameters:

*class qoid.Index(tag: str="Index", val=None, source=None, path=None, parent=None)*  
*class qoid.Register(tag: str="Register", val=None, source=None, path=None, parent=None)*
 
List functions including (but not limited to) append, index, pop, and iter are available as class attributes. Elements are automatically parented when added to objects, and should not be set manually
 
 ## Saving and Opening Indices and Registers
 
Indices and Registers construct a file path to save their data by prioritizing (in order): the parent, the path, and the source of the object. If a parent exists, it extends the parent's path. Otherwise it will save locally
 
If an instance variable *path* exists, then that completes the path; if not, and the object has a source specified (e.g. from Index.open or Register.open) then it uses that; if it has neither of them, then it will attempt to use its tag.

When opening an Index or Register, only files ending in .cxr, .meta, and .txt and folders ending in .cxr will be loaded. If one is created with a tag not ending in one of those file formats, then a `.cxr` extension is automatically added

## Built-ins

Comparator | Description
--- | ---
x ( ) y | Checks if an object is ...
x == y | equal to another in terms of tag and value
x != y | not equal to another in terms of tag and value
x > y |  greater than another in terms of tag
x >= y | greater than or equal to another in terms of tag
x < y | less than another in terms of tag
x <= y | less than or equal to another in terms of tag
x in y | contained in the value set of another
**Arithmetic** | 
x + y | combines the elements of the two objects, if applicable (also works with x += y)
x - y | removes an object form another, if applicable (also works with x -= y)
**Other Built-in** | 
len | returns the length of the value
getitem/setitem/delitem | get, set, or delete the member of the value set based on slice, tag (string) or index (int)
format/str | prepares useful string representation of the object
