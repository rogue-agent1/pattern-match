#!/usr/bin/env python3
"""pattern_match - Structural pattern matching engine for Python data."""
import sys

class _Wildcard:
    def __repr__(self): return "_"
_ = _Wildcard()

class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self): return f"Var({self.name})"

class Guard:
    def __init__(self, pattern, predicate):
        self.pattern = pattern
        self.predicate = predicate

def match_pattern(pattern, value, bindings=None):
    if bindings is None:
        bindings = {}
    if isinstance(pattern, _Wildcard):
        return True, bindings
    if isinstance(pattern, Var):
        if pattern.name in bindings:
            return bindings[pattern.name] == value, bindings
        bindings[pattern.name] = value
        return True, bindings
    if isinstance(pattern, Guard):
        ok, b = match_pattern(pattern.pattern, value, bindings)
        if ok and pattern.predicate(value):
            return True, b
        return False, bindings
    if isinstance(pattern, type):
        return isinstance(value, pattern), bindings
    if isinstance(pattern, tuple) and isinstance(value, tuple):
        if len(pattern) != len(value):
            return False, bindings
        for p, v in zip(pattern, value):
            ok, bindings = match_pattern(p, v, bindings)
            if not ok:
                return False, bindings
        return True, bindings
    if isinstance(pattern, list) and isinstance(value, list):
        if len(pattern) != len(value):
            return False, bindings
        for p, v in zip(pattern, value):
            ok, bindings = match_pattern(p, v, bindings)
            if not ok:
                return False, bindings
        return True, bindings
    if isinstance(pattern, dict) and isinstance(value, dict):
        for k, p in pattern.items():
            if k not in value:
                return False, bindings
            ok, bindings = match_pattern(p, value[k], bindings)
            if not ok:
                return False, bindings
        return True, bindings
    return pattern == value, bindings

class Match:
    def __init__(self, value):
        self.value = value
        self.cases = []

    def case(self, pattern, handler):
        self.cases.append((pattern, handler))
        return self

    def execute(self):
        for pattern, handler in self.cases:
            ok, bindings = match_pattern(pattern, self.value)
            if ok:
                return handler(bindings) if bindings else handler({})
        raise ValueError(f"No pattern matched for {self.value!r}")

W = _  # module-level alias to avoid local variable conflict

def test():
    ok, b = match_pattern(W, 42)
    assert ok and b == {}
    ok, b = match_pattern(Var("x"), 42)
    assert ok and b == {"x": 42}
    ok, b = match_pattern((Var("a"), Var("b")), (1, 2))
    assert ok and b == {"a": 1, "b": 2}
    ok, b = match_pattern({"name": Var("n"), "age": W}, {"name": "Alice", "age": 30, "extra": True})
    assert ok and b == {"n": "Alice"}
    ok, _b = match_pattern((1, 2), (1, 3))
    assert not ok
    ok, b = match_pattern([Var("x"), Var("x")], [5, 5])
    assert ok
    ok, _b = match_pattern([Var("x"), Var("x")], [5, 6])
    assert not ok
    ok, _b = match_pattern(Guard(Var("x"), lambda v: v > 10), 15)
    assert ok
    ok, _b = match_pattern(Guard(Var("x"), lambda v: v > 10), 5)
    assert not ok
    result = (Match(("+", 3, 4))
              .case(("+", Var("a"), Var("b")), lambda b: b["a"] + b["b"])
              .case(("-", Var("a"), Var("b")), lambda b: b["a"] - b["b"])
              .execute())
    assert result == 7
    result = (Match(("*", 5, 6))
              .case(("+", W, W), lambda b: "add")
              .case(("*", Var("a"), Var("b")), lambda b: b["a"] * b["b"])
              .execute())
    assert result == 30
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("pattern_match: Pattern matching. Use --test")
