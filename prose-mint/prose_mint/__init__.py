"""prose-mint: a structural-tells linter for AI-flavored prose.

v1 detects structural tells only (em dashes, ASCII arrows, "not X but Y" and
friends, bold-colon openers, hard-wrapped paragraphs). The banned-word and
banned-phrase list documented in a project's prose rule is advisory in v1
(operator discipline), not mechanically enforced. Mechanized banlist
enforcement is planned for v2; see CHANGELOG.

Engine behavior is a faithful port of the Untype scanner so a project
migrating to this tool sees identical findings.
"""

__version__ = "0.1.1"

REQUIRES_PYTHON = (3, 11)
