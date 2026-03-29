#!/usr/bin/env python3
"""Pattern matching DSL. Zero dependencies."""

class _Any: 
    def __repr__(self): return "_"
_ = _Any()

class _Guard:
    def __init__(self, fn): self.fn = fn
    def __repr__(self): return f"Guard({self.fn})"

def guard(fn): return _Guard(fn)

def _matches(pattern, value, bindings):
    if isinstance(pattern, _Any): return True
    if isinstance(pattern, _Guard): return pattern.fn(value)
    if isinstance(pattern, str) and pattern.startswith("$"):
        name = pattern[1:]
        if name in bindings: return bindings[name] == value
        bindings[name] = value; return True
    if isinstance(pattern, type): return isinstance(value, pattern)
    if isinstance(pattern, (list, tuple)) and isinstance(value, (list, tuple)):
        if len(pattern) != len(value): return False
        return all(_matches(p, v, bindings) for p, v in zip(pattern, value))
    if isinstance(pattern, dict) and isinstance(value, dict):
        return all(k in value and _matches(v, value[k], bindings) for k, v in pattern.items())
    return pattern == value

def match(value, *cases):
    for pattern, handler in cases:
        bindings = {}
        if _matches(pattern, value, bindings):
            if callable(handler):
                import inspect
                sig = inspect.signature(handler)
                if sig.parameters:
                    return handler(**{k: bindings[k] for k in sig.parameters if k in bindings})
            return handler() if callable(handler) else handler
    raise ValueError(f"No match for {value!r}")

if __name__ == "__main__":
    result = match(42,
        (0, lambda: "zero"),
        (guard(lambda x: x > 0), lambda: "positive"),
        (_, lambda: "other"))
    print(result)
