#!/usr/bin/env python3
"""Pattern matching engine (ML-style)."""
class Wildcard: pass
class Var:
    def __init__(self,name): self.name=name
class Cons:
    def __init__(self,tag,*fields): self.tag=tag;self.fields=list(fields)
class Lit:
    def __init__(self,value): self.value=value
def match(value,pattern,bindings=None):
    if bindings is None: bindings={}
    if isinstance(pattern,Wildcard): return True,bindings
    if isinstance(pattern,Var):
        if pattern.name in bindings: return bindings[pattern.name]==value,bindings
        bindings[pattern.name]=value;return True,bindings
    if isinstance(pattern,Lit): return value==pattern.value,bindings
    if isinstance(pattern,Cons):
        if not isinstance(value,tuple) or len(value)<1: return False,bindings
        if value[0]!=pattern.tag: return False,bindings
        if len(value)-1!=len(pattern.fields): return False,bindings
        for v,p in zip(value[1:],pattern.fields):
            ok,bindings=match(v,p,bindings)
            if not ok: return False,bindings
        return True,bindings
    if isinstance(pattern,(list,tuple)) and isinstance(value,(list,tuple)):
        if len(pattern)!=len(value): return False,bindings
        for v,p in zip(value,pattern):
            ok,bindings=match(v,p,bindings)
            if not ok: return False,bindings
        return True,bindings
    return value==pattern,bindings
def match_cases(value,cases):
    for pattern,action in cases:
        ok,bindings=match(value,pattern)
        if ok: return action(bindings)
    raise ValueError("No matching case")
if __name__=="__main__":
    ok,b=match(42,Var("x"));assert ok and b["x"]==42
    ok,b=match(("Just",5),Cons("Just",Var("v")));assert ok and b["v"]==5
    ok,_=match(("Nothing",),Cons("Just",Wildcard()));assert not ok
    result=match_cases(("Some",42),[
        (Cons("None"),lambda b:"nothing"),
        (Cons("Some",Var("x")),lambda b:f"got {b['x']}"),
    ])
    assert result=="got 42"
    print(f"Pattern match result: {result}"); print("Pattern matching OK")
