TASKS = {
    "single_obvious": {
        "files": {
            "src/calc.py": """\
def add(a, b):
    return a - b
""",
            "tests/run_tests.py": """\
from src.calc import add

assert add(2, 3) == 5
assert add(-2, -3) == -5
print("PASS")
""",
        },
        "target_files": ["src/calc.py"],
        "issue": "add(a, b) returns the wrong result.",
        "patch_kind": "add_only",
    },
    "edge_case": {
        "files": {
            "src/stats.py": """\
def median(values):
    ordered = sorted(values)
    return ordered[len(ordered) // 2]
""",
            "tests/run_tests.py": """\
from src.stats import median

assert median([3, 1, 2]) == 2
assert median([10, 2, 4, 8]) == 6
try:
    median([])
except ValueError:
    pass
else:
    raise AssertionError("median([]) should raise ValueError")
print("PASS")
""",
        },
        "target_files": ["src/stats.py"],
        "issue": "median mishandles even-length input and empty input.",
        "patch_kind": "median",
    },
    "multi_file": {
        "files": {
            "src/config.py": """\
DEFAULT_TAX_RATE = 0.08
""",
            "src/pricing.py": """\
from src.config import DEFAULT_TAX_RATE


def total_with_tax(amount):
    return amount * (1 + DEFAULT_TAX_RATE)
""",
            "tests/run_tests.py": """\
from src.pricing import total_with_tax

assert total_with_tax(100) == 107
print("PASS")
""",
        },
        "target_files": ["src/config.py"],
        "issue": "The configured default tax rate should be 7%, not 8%.",
        "patch_kind": "tax",
    },
    "misleading": {
        "files": {
            "src/parser.py": """\
def parse_bool(value):
    return bool(value)
""",
            "src/boolean_utils.py": """\
# Historical helper kept for compatibility.
def normalize_bool(value):
    return value
""",
            "tests/run_tests.py": """\
from src.parser import parse_bool

assert parse_bool("true") is True
assert parse_bool("FALSE") is False
assert parse_bool("0") is False
assert parse_bool("yes") is True
print("PASS")
""",
        },
        "target_files": ["src/parser.py"],
        "issue": "String booleans are parsed incorrectly; ignore compatibility helper unless needed.",
        "patch_kind": "bool",
    },
    "config_runner": {
        "files": {
            "src/app.py": """\
def greet(name):
    return f"Hello, {name}!"
""",
            "project.toml": """\
[tool.test]
command = "python3 tests/run_tests.py"
""",
            "tests/run_tests.py": """\
from src.app import greet

assert greet("Justin") == "Hello Justin!"
print("PASS")
""",
        },
        "target_files": ["src/app.py"],
        "issue": "The greeting format should not include a comma.",
        "patch_kind": "greet",
    },
    "noisy_failure": {
        "files": {
            "src/slug.py": """\
def slugify(value):
    return value.replace(" ", "_")
""",
            "tests/run_tests.py": """\
from src.slug import slugify
import sys

try:
    assert slugify("Hello World") == "hello-world"
except AssertionError:
    print("FAILED test_slugify_lowercase_hyphen: expected lowercase hyphenated slug")
    for i in range(80):
        print(f"noise line {i}: build log filler")
    sys.exit(1)
print("PASS")
""",
        },
        "target_files": ["src/slug.py"],
        "issue": "slugify should lowercase text and replace spaces with hyphens.",
        "patch_kind": "slug",
    },
}
