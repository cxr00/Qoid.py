from qoid import Qoid, Index

# First the file is opened and parsed from cxr format
i = Index.open("example_2_sample_file.cxr")

# Create the message Qoid
q = Qoid("messages")

# We iterate through each element of the index
for each in i:
    # This gets and displays every Property tagged "message"
    # Using addition is a great way to add things!
    q += each.get("message")

    # This statement is equivalent to the one above!
    # q = q + each.get("message")

# Iterate through values since we already know the tags are message
for m in q.vals():
    print(m)
