from pygdbmi.gdbcontroller import GdbController
from pprint import pprint

# Start gdb process
gdbmi = GdbController()
# Print actual command run as subprocess
print(gdbmi.command)

# Load binary a.out and its debug symbols
response = gdbmi.write('-file-exec-and-symbols a.out')
pprint(response)
print()

# Actually run it
response = gdbmi.write('-exec-run')
pprint(response)
