from qoid import Property

p_a = Property("PropertyA", "valueA")
p_b = Property("PropertyB", "valueB")
p_c = Property("PropertyC")

print("p_a", p_a)
print("p_b", p_b)
print("p_c", p_c)
print()

p_ba = p_b + p_a

print("add")
print(p_ba)
print()

print("bool")
print(bool(p_a))
print()

print("bytes")
print(bytes(p_b))
print()

print("equal")
print("p_a == p_a", p_a == p_a)
print("p_a == p_b", p_a == p_b)
print()

print("greater/less than")
print("p_a > p_c", p_a > p_c)
print("p_c < p_b", p_c < p_b)
print()

print("Not equal to")
print(p_a != p_b)
print()

print("len")
print(len(p_a))
print(len(p_c))
print()

print("hash")
print(hash(p_a))
print()

print("repr")
print(repr(p_b))
print()

print("lower")
print(p_a.lower())
print()

print("set")
p_c.set("PropertyC updated", "new PropertyC value")
print(p_c)
