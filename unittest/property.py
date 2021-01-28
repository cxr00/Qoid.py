from qoid import Property

p_a = Property("PropertyA", "valueA")
p_b = Property("PropertyB", "valueB")
p_c = Property("PropertyC")

p_ba = p_b + p_a

print(p_ba)
print(p_c)
print()

print(bool(p_a))
print()

print(bytes(p_b))
print()

print(p_a == p_a)
print(p_a == p_b)
print()

print(p_a > p_c)
print(p_c > p_b)
print()

print(len(p_a))
print(len(p_c))
print()

print(hash(p_a))
print()

print(p_a != p_b)
print()

print(repr(p_b))
print()

p_c.set("PropertyC updated", "new PropertyC value")
print(p_c)
