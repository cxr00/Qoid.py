# Qoid.py

Qoid is a simple markup language which uses tag-value pairs to record data in traditional files and folders with the added depth of tagged elements within each file.

All objects in qoid.py have string tags, with the values adding recursive depth. Start with a Property, which is a tag-value pair. Then a Qoid tags a list of Properties, a Bill tags a list of Qoids, and a Register tags a list of Bills and Registers.

Objects in qoid.py can be created very quickly, then printed in its Qoid representation.

```python
>>> a = Property("tag", "value")
>>> b = Property("tag2", "value2")
>>> c = Qoid("qoid tag", [a, b])
>>> d = Qoid("other qoid tag", [b, a, b])
>>> e = Bill("test bill", [c, d])
>>>> print(e)

/ test bill

#qoid tag
tag: value
tag2: value2

#other qoid tag
tag2: value2
tag: value
tag2: value2
```
 
## Saving and Opening Bills and Registers

To save a Bill or Register, simply use my_bill.save() or my_register.save(). Each Bill and Register has a `path` variable which may be specified. If `path` is not specified, then files will be saved locally.

When opening a Bill or Register, only files and folders ending in `.cxr` can be loaded. The path specified is saved in the object for future saving.



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
x - y | removes an object from another, if applicable (also works with x -= y)
**Other Built-in** | 
len | returns the length of the object's value list
getitem/setitem/delitem | get, set, or delete the member of the value set based on slice, tag (string) or index (int)
format/str | prepares useful string representation of the object
hash | 
bytes | 
