import sys

import pytest


def main(argv=None) -> int:
    """Run pytest programmatically.

    Usage: uv run test
    """
    if argv is None:
        argv = sys.argv[1:]
    # default to tests under app/tests
    if not argv:
        argv = ["-q", "app/tests"]
    return pytest.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
