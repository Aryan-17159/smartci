"""Toggle the exact incorrect assertion requested by Lab 2.

Usage: python scripts/failure_demo.py enable
       python scripts/failure_demo.py disable
"""

import argparse
from pathlib import Path


TEST_FILE = Path(__file__).resolve().parents[1] / "tests" / "test_pricing.py"
CORRECT = "    assert apply_discount(100, 0) == 100.0"
INCORRECT = "    assert apply_discount(100, 0) == 101.0"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("enable", "disable"))
    args = parser.parse_args()
    original = TEST_FILE.read_bytes().decode("utf-8")
    lines = original.splitlines(keepends=True)
    contents = [line.rstrip("\r\n") for line in lines]
    before, after = (CORRECT, INCORRECT) if args.mode == "enable" else (INCORRECT, CORRECT)

    if contents.count(after) == 1 and before not in contents:
        print(f"Failure demo already {args.mode}d; no change needed.")
        return
    if contents.count(before) != 1 or after in contents:
        parser.error("Expected assertion was changed. Review test_pricing.py; no file was modified.")

    index = contents.index(before)
    lines[index] = after + lines[index][len(before):]
    TEST_FILE.write_bytes("".join(lines).encode("utf-8"))
    print(f"Failure demo {args.mode}d in tests/test_pricing.py.")
    print("Run python -m pytest -v to see the result.")


if __name__ == "__main__":
    main()
