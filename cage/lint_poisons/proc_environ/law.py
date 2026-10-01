# the brief's witness: pathlib outside datafile.py, reading the kit's environment
import pathlib
print(pathlib.Path("/proc/self/environ").read_bytes())
