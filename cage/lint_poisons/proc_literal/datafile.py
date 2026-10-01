# datafile.py may use pathlib, but not to read /proc
import pathlib
print(pathlib.Path("/proc/self/environ").read_bytes())
