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

r_b = Register("Register B", [b_c])
r_a = Register("Example Register", [b_a, b_b, r_b])

print("save")
r_a.save()

r_a -= b_b
print(r_a)

print("open")
r_a = Register.open("Example Register.cxr")
print(r_a)
