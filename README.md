# Qoid.py

Qoid is a markup language similar to ini which is designed to aid in recording arbitrary amounts of sometimes duplicitous data. It's designed to be simple to learn and use, and to export as easily to JSON as it reads in the native CXR file type.

Qoid uses a tag-value system for class objects. Properties consist of both string tag and value, while a Qoid has a string tag and an array of Properties as values. These are contained in a file called an Index, which is contained in a folder called a Register.

```
/ Index

#Qoid tag
Property tag1: val1
Property tag2: val2
```

... into the file `Index.cxr`:

```json
{
"Index":[
  {
    "Qoid tag": [["Property tag", "Property tag2"], ["val1", "val2"]]
  }
  ]
}
```

While Indices and Registers both have the name limitations of files and folders, Indices and Qoids permit duplicate keys called *tags* for each element in their respective value sets.

```

#Same tag
tag1: val1
tag1: val2

#Same tag
tag2: val1
tag2: val2

```

### Lots to do to clean this up
