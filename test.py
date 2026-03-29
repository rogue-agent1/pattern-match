from pattern_match import match, _, guard
assert match(42, (42, "found"), (_, "other")) == "found"
assert match(99, (42, "found"), (_, "other")) == "other"
assert match(5, (guard(lambda x: x>0), "positive"), (_, "other")) == "positive"
assert match(-1, (guard(lambda x: x>0), "positive"), (_, "negative")) == "negative"
assert match([1,2,3], ([1,_,3], "matched"), (_, "no")) == "matched"
assert match({"a":1,"b":2}, ({"a":1}, "has a=1"), (_, "no")) == "has a=1"
assert match("hello", (str, "string"), (int, "int")) == "string"
# Variable binding
result = match([1,2], (["$x","$y"], lambda x,y: x+y))
assert result == 3
print("pattern_match tests passed")
