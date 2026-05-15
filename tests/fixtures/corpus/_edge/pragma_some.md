<!-- prose-check: skip em-dash, bold-colon-opener -->
# Pragma skip some

This em dash — must NOT be flagged (em-dash disabled by pragma).

**Term**: this bold-colon opener must NOT be flagged either.
**Term2**: nor this one.
**Term3**: nor this.
**Term4**: nor this.
**Term5**: nor this, even past the threshold of five.

But this arrow → MUST still be flagged, because the pragma only
disabled em-dash and bold-colon-opener, not ascii-arrow.
