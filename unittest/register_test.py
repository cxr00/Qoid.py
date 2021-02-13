from qoid import Property, Qoid, Bill, Register

p_a = Property("PropertyA", "valueA")
p_b = Property("PropertyB", "valueB")
p_c = Property("PropertyC")

q_a = Qoid("Qoid A", [p_a, p_b])
q_b = Qoid("Qoid B", [p_b])
q_c = Qoid("Qoid C", [p_b, p_c])

b_a = Bill("Bill A", [q_a, q_b, q_c])
b_b = Bill("Bill B", [q_b, q_c])
b_c = Bill("Bill C", [q_c])

r_a = Register("Register A", [b_a, b_b])
r_b = Register("Register B", [b_b, b_c])
r_c = Register("Register C", [b_c])

print("add")
print(r_a + r_c)
print(r_a + b_c)
print()

print("bool")
print(bool(r_a))
print()

print("bytes")
print(bytes(r_b))
print()

print("contains")
print("b_a in r_a", b_a in r_a)
print("b_b in r_c", b_b in r_c)
print()

print("delitem")
del r_a["Bill A"]
print(r_a)
print()

print("making r_a larger for getitem")
r_d = Register("Register D", [b_c])
r_a += [b_a, b_c, r_d]
print(r_a)
print()

print("getitem")
print(r_a[1::2])
print(r_a[2])
print(r_a["Bill C"])
print()

print("hash")
print(hash(r_a))
print()

print("isub")
r_a -= r_d
print(r_a)
print()

print("isub again")
r_a -= b_c
print(r_a)
print()

print("len")
print(len(r_a))
print()

print("repr")
print(repr(r_a))
print()

print("setitem")
r_a += r_d
r_a[2] = r_b
print(r_a)
print()

print("insert")
r_a.insert(2, b_c)
print(r_a)
print()

print("reverse")
r_a.reverse()
print(r_a)
print()

print("tags")
print(r_a.tags())
print()

print("vals")
print(r_a.vals())
print()
