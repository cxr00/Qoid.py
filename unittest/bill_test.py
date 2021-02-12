from qoid import Property, Qoid, Bill

p_a = Property("PropertyA", "valueA")
p_b = Property("PropertyB", "valueB")
p_c = Property("PropertyC")

q_a = Qoid("Qoid A", [p_a, p_b])
q_b = Qoid("Qoid B", [p_b])
q_c = Qoid("Qoid C", [p_b, p_c])

b_a = Bill("Bill A", [q_a, q_b, q_c])
b_b = Bill("Bill B", [q_b, q_c])
b_c = Bill("Bill C", [q_c])

print("Bill A")
print(b_a)
print("Bill B")
print(b_b)
print("Bill C")
print(b_c)

print("add")
print(b_a + b_b)
print()

print("bool")
print(bool(b_a))
print(bool(b_b))
print()

print("bytes")
print(bytes(b_c))
print()

print("contains")
print("q_a in b_a", q_a in b_a)
print("q_b in b_c", q_b in b_c)
print()

print("del")
del b_a["Qoid B"]
print(b_a)
print()

print("equal")
print(b_a == b_a)
print(b_b == b_c)
print()

print("format")
print(format(b_a))
print(format(b_c))
print()

print("isub")
b_a -= q_c
print(b_a)
print()

print("getitem")
print(b_b[:1])
print(b_b[1])
print(b_b["Qoid B"])
print()

print("hash")
print(hash(b_c))
print()

print("iadd")
b_b += q_a
b_c += b_c
print(b_b)
print(b_c)
print()

print("isub")
b_b -= q_a
b_a -= b_a
print(b_b)
print(b_a)

print("repr")
print(repr(b_b))
print()

print("reversed")
b_b = reversed(b_b)
print(b_b)
print()

print("setitem")
b_a.append(q_a)
b_a.append(q_b)
b_a[0] = q_c
b_a["Qoid B"] = q_a
print(b_a)
print()

print("all_of")
print(b_a.all_of("Qoid A"))
print()

print("count")
print(b_a.count("Qoid B"))
print(b_a.count("Qoid C"))
print()

print("insert")
b_a.insert(1, b_a)
b_a.insert(3, q_c)
print(b_a)
print()

print("reverse")
b_a.reverse()
print(b_a)
print()

print("sort")
b_a.sort()
print(b_a)
print()

print("tags")
print(b_a.tags())
print()

print("vals")
print(b_a.vals())
print()

