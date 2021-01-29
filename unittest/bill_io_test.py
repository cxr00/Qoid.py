from qoid import Property, Qoid, Bill

p_a = Property("PropertyA", "valueA")
p_b = Property("PropertyB", "valueB")
p_c = Property("PropertyC")

q_a = Qoid("Qoid A", [p_a, p_b])
q_b = Qoid("Qoid B", [p_b])
q_c = Qoid("Qoid C", [p_b, p_c])

b_a = Bill("Example Bill", [q_a, q_b, q_c])

b_a -= q_b

b_a.save()

b_a += q_b

print(b_a)

b_a = Bill.open("Example Bill.cxr")

print(b_a)
