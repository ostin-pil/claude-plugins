# Fenced code stripping

This paragraph outside the fence has an em dash — it should be flagged.

```python
# This em dash — inside a fence must NOT be flagged.
x = a → b  # this arrow inside a fence must NOT be flagged either
print("It's not X, it's Y")  # structural inside fence: ignored
```

After the fence, another arrow → here should be flagged.
