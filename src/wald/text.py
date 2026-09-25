"""SURFACE v0.2 V2.11: what a pack's text may be before it is parsed.

A pack is UTF-8 text with LF line endings, read as its bytes are written. Refused, all by the
name NOT_A_DECLARATION: a coding declaration naming another encoding, a CR anywhere, a surrogate
code point in any string, paired or not, and an identifier outside ASCII. Each closes a way for one
pack's bytes to be read as two packs: a cookie gives the bytes a second set of names; Python's
parser turns CR LF inside a string into LF where a text reader keeps both (attack session 3, 3.1);
a surrogate pair spelt by escapes is the character spelt as itself to an encoder (session 2, 1.3);
and Python folds identifiers to NFKC, so `ſcore` is `score` to the parser (session 4, 4.4).

The identifiers are found in the text, not in the tree: the tree has already folded them, and on
a full-width `Ｎｏｎｅ` Python's parser raises ValueError instead of building one. So a small lexer
walks the text, skipping string literals and comments, and a non-ASCII character anywhere else
that can stand in an identifier is refused."""
import ast

from .refusals import NOT_A_DECLARATION, Refused

UTF8 = ("utf-8", "utf8")


def refuse_unlawful(text):
    """The rules V2.11 states of the text, before it is parsed."""
    for line in text.splitlines()[:2]:
        named = _coding(line)
        if named is not None and named.lower().replace("_", "-") not in UTF8:
            raise Refused(NOT_A_DECLARATION, "[V2.11] a pack is UTF-8, and this one declares "
                          + repr(named))
    if "\r" in text:
        raise Refused(NOT_A_DECLARATION, "[V2.11] a pack's lines end in LF: it holds no CR, so a"
                      + " name is the same to every reader")
    if text.isascii():
        return
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise Refused(NOT_A_DECLARATION, "[V2.11] a surrogate code point, which no UTF-8 text holds")
    for i, ch in _outside_strings(text):
        if not ch.isascii() and ("a" + ch).isidentifier():
            line = text.count("\n", 0, i) + 1
            raise Refused(NOT_A_DECLARATION, "[V2.11] line " + str(line) + ": an identifier is"
                          + " ASCII; " + repr(ch) + " would be folded to another name")


def refuse_surrogates(tree, text):
    """V2.11 once the escapes are read: no string holds a surrogate, spelt by escapes or not. The
    text holds none as itself (`refuse_unlawful`), so only a `\\u` or `\\U` escape can spell one,
    and a pack with neither -- every Wordle pack -- need not be walked again."""
    if "\\u" not in text and "\\U" not in text:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and not node.value.isascii():
            try:
                node.value.encode("utf-8")
            except UnicodeEncodeError:
                raise Refused(NOT_A_DECLARATION, "[V2.11] line " + str(node.lineno)
                              + ": a name holds a surrogate code point, which no text can")


def _coding(line):
    """The encoding a line declares, as Python's `^[ \\t\\f]*#.*?coding[:=][ \\t]*([-\\w.]+)`
    finds it, or None."""
    i = 0
    while i < len(line) and line[i] in " \t\f":
        i += 1
    if not line.startswith("#", i):
        return None
    at = line.find("coding", i + 1)
    while at != -1:
        j = at + len("coding")
        if j < len(line) and line[j] in ":=":
            j += 1
            while j < len(line) and line[j] in " \t":
                j += 1
            end = j
            while end < len(line) and (line[end] in "-._" or line[end].isalnum()):
                end += 1
            if end > j:
                return line[j:end]
        at = line.find("coding", at + 1)
    return None


def _outside_strings(text):
    """Every (index, character) outside string literals and comments. A backslash in a string,
    raw or not, keeps the next character from closing it."""
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "#":
            newline = text.find("\n", i)
            i = n if newline == -1 else newline
            continue
        if ch in "'\"":
            quote = ch * 3 if text.startswith(ch * 3, i) else ch
            i += len(quote)
            while i < n and not text.startswith(quote, i):
                if text[i] == "\\":
                    i += 1
                elif len(quote) == 1 and text[i] == "\n":
                    break                           # unterminated: the parser will say SYNTAX
                i += 1
            i += len(quote)
            continue
        yield i, ch
        i += 1
