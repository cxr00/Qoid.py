from qoid import Index, Register

# First we'll instantiate a Register and an Index
r = Register("register")
i = Index("index")
r += i

# Next, we'll instantiate another Register and add a copy of i to it
r2 = Register("register2")
r2 += i

# Now we'll add r2 as a subregister of r
r += r2

# We can tell where a register will save by using create_path()
print(r.create_path())

# Notice that tags lacking the .cxr extension will be saved with them added, even folders
print(r2.create_path())
print()

# When saving, we can choose to have every sub-folder echo, or just the register
r.save(echo=True, echo_all=False)
print()
r.save(echo=True, echo_all=True)
