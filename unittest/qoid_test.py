from qoid import Property, Qoid

p_a = Property("PropertyA", "valueA")
p_b = Property("PropertyB", "valueB")
p_c = Property("PropertyC")

q_a = Qoid("Qoid A", [p_a, p_b])
q_b = Qoid("Qoid B", [p_b])
q_c = Qoid("Qoid C", [p_b, p_c])

print(q_a)
print(q_b)
print(q_c)

print("add qoid")
print(q_a + q_b)
print()

print("add property")
print(q_a + p_a)

print("bool")
print(bool(q_a))
print()

print("bytes")
print(bytes(q_b))
print()

print("contains (in)")
print("p_a in q_a", p_a in q_a)
print("p_a in q_b", p_a in q_b)
print()

print("del")
del q_a[0]
print(q_a)

print("iadd")
q_a += p_a
q_b += p_b
q_c += q_c
print(q_a)
print(q_b)
print(q_c)

print("equal to")
print("q_a == q_a", q_a == q_a)
print("q_b == q_a", q_b == q_a)
print()

print("format")
print(format(q_c))

print("getitem")
q_ba = q_b + q_a
print(q_ba[:3])
print(q_ba[::2])
print(q_ba["PropertyB"])
print(q_ba[1])
print()

print("hash")
print(hash(q_ba))
print()

print("isub")
q_a -= p_a
q_ba -= q_b
print(q_a)
print(q_ba)
print()

print("len")
print(len(q_a))
print(len(q_ba))
print()

print("radd")
q_a = p_a + q_a
print(q_a)
print()

print("repr")
print(repr(q_a))

print("reversed")
print(reversed(q_a))
print()

print("setitem")
q_a[0] = Property("New property", "with a new value")
q_a["PropertyB"] = Property("PropertyA", "valueA")
print(q_a)

print("sub")
print(q_a - p_a)

print("append")
q_a.append(p_c)
print(q_a)
print()

print("count")
print(q_b.count("PropertyB"))
print()

print("extend")
q_a.extend([p_b, p_c])
print(q_a)
print()

print("all of")
print(q_a.all_of("PropertyC"))
print()

print("index")
print(q_a.index(p_c))
print(q_a.index("New property"))
print()

print("insert")
q_a.insert(1, p_a)
print(q_a)
q_a.insert(3, q_b)
print(q_a)
print()

print("pack")
print(q_a.pack())
print()

print("pop")
q_a.pop(2)
print(q_a)
print()

print("reverse")
q_a.reverse()
print(q_a)
print()

print("sort")
q_a.sort()
print(q_a)
print()

print("tags")
print(q_a.tags())
print()

print("vals")
print(q_a.vals())
print()
