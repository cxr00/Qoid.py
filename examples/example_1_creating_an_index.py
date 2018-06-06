from qoid import Property, Qoid, Index

"""

This example showcases some of the typical ways by which
an Index is created, modified, and saved.

"""

# Create an empty index
i = Index("index")

# Create two empty qoids
q1 = Qoid("qoid 1")
q2 = Qoid("qoid 2")

# Create some properties
p1 = Property("p1", "foo")
p2 = Property("p2")
p2.set(val="bar")
p3 = Property("p3")

# Add the properties to the qoids
q1 += [p1, p3]
q2.append(p2)

# You can add and subtract properties from qoids and qoids from one another

# Modify a property from within the qoid
q1["p3"] = "baz lehrman"

# Add the qoids to the index
i += [q1, q2]
i.append(q1)

# This is the string representation of i put in cxr format
print(i)

# This is the string representation of i translated to json
print(i.pack())
print()

# This is the string representation of i translated to and from json
# Note the difference between the cxr format
print(Index.parse(i.pack()))

# This will simply save the index locally.
# When echo is True, save confirmation will print for your index.
i.save(echo=True)

# This will export the index to JSON format
i.save(echo=True, is_json=True)

# If a path is specified, the index will save to a different file
i.path = "output.cxr"
i.save(echo=True)
