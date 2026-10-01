# open() reached through __builtins__ rather than called by its bare name
print(getattr(__builtins__, "open"))
