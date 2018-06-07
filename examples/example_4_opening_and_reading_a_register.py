from qoid import Register

# Open example_4_register.cxr
r = Register.open("example_4_register.cxr")

# See the contents of r; currently it only contains test-file.cxr
print(r)

# Create a register with a clone of test-file.cxr in it
r2 = Register("subregister.cxr")
r2 += r["test-file.cxr"]
r += r2

# By specifying an output path, the register will save in a different location
r.path = "output_4_register.cxr"
r.save(echo=True, echo_all=True)
