#!/usr/bin/env python3
"""pattern_match - ML/Rust-style pattern matching with exhaustiveness checking."""
import sys, json
from dataclasses import dataclass
from typing import Any

@dataclass
class Pat:
    pass

@dataclass
class PWild(Pat):
    def __repr__(self): return "_"

@dataclass
class PVar(Pat):
    name: str
    def __repr__(self): return self.name

@dataclass
class PLit(Pat):
    value: Any
    def __repr__(self): return repr(self.value)

@dataclass
class PCons(Pat):
    name: str; args: list
    def __repr__(self): return f"{self.name}({', '.join(map(str, self.args))})" if self.args else self.name

@dataclass
class PTuple(Pat):
    elems: list
    def __repr__(self): return f"({', '.join(map(str, self.elems))})"

@dataclass
class POr(Pat):
    alts: list
    def __repr__(self): return " | ".join(map(str, self.alts))

class MatchCompiler:
    def __init__(self, constructors=None):
        self.constructors = constructors or {}
    
    def match_pat(self, pat, value, bindings=None):
        if bindings is None: bindings = {}
        if isinstance(pat, PWild): return True, bindings
        if isinstance(pat, PVar): bindings[pat.name] = value; return True, bindings
        if isinstance(pat, PLit): return value == pat.value, bindings
        if isinstance(pat, PCons):
            if not isinstance(value, tuple) or len(value) < 1: return False, bindings
            if value[0] != pat.name: return False, bindings
            args = value[1:] if len(value) > 1 else []
            if len(args) != len(pat.args): return False, bindings
            for p, v in zip(pat.args, args):
                ok, bindings = self.match_pat(p, v, bindings)
                if not ok: return False, bindings
            return True, bindings
        if isinstance(pat, PTuple):
            if not isinstance(value, tuple) or len(value) != len(pat.elems): return False, bindings
            for p, v in zip(pat.elems, value):
                ok, bindings = self.match_pat(p, v, bindings)
                if not ok: return False, bindings
            return True, bindings
        if isinstance(pat, POr):
            for alt in pat.alts:
                ok, b = self.match_pat(alt, value, dict(bindings))
                if ok: return True, b
            return False, bindings
        return False, bindings
    
    def match(self, value, arms):
        for pat, action in arms:
            ok, bindings = self.match_pat(pat, value)
            if ok: return action(bindings)
        raise RuntimeError(f"Non-exhaustive match for {value}")
    
    def check_exhaustive(self, type_name, patterns):
        if any(isinstance(p, (PWild, PVar)) for p in patterns): return True, []
        cons = self.constructors.get(type_name, [])
        if not cons: return True, []
        covered = {p.name for p in patterns if isinstance(p, PCons)}
        missing = set(cons) - covered
        return len(missing) == 0, list(missing)

def main():
    mc = MatchCompiler(constructors={"Option": ["Some", "None"], "Result": ["Ok", "Err"]})
    
    print("Pattern matching demo\n")
    
    # Match on Option
    for val in [("Some", 42), ("None",)]:
        r = mc.match(val, [
            (PCons("Some", [PVar("x")]), lambda b: f"Got {b['x']}"),
            (PCons("None", []), lambda b: "Nothing"),
        ])
        print(f"  match {val} => {r}")
    
    # Tuple matching
    r = mc.match((1, "hello"), [
        (PTuple([PLit(1), PVar("s")]), lambda b: f"One and {b['s']}"),
        (PTuple([PWild(), PWild()]), lambda b: "other"),
    ])
    print(f"  match (1, 'hello') => {r}")
    
    # Or patterns
    r = mc.match(("Ok", 200), [
        (POr([PCons("Ok", [PLit(200)]), PCons("Ok", [PLit(201)])]), lambda b: "success"),
        (PCons("Ok", [PVar("code")]), lambda b: f"ok({b['code']})"),
        (PCons("Err", [PVar("e")]), lambda b: f"err({b['e']})"),
    ])
    print(f"  match Ok(200) => {r}")
    
    # Exhaustiveness
    exh, missing = mc.check_exhaustive("Option", [PCons("Some", [PWild()])])
    print(f"\n  Exhaustive? {exh}, missing: {missing}")
    exh2, m2 = mc.check_exhaustive("Option", [PCons("Some", [PWild()]), PCons("None", [])])
    print(f"  With None? {exh2}, missing: {m2}")

if __name__ == "__main__":
    main()
