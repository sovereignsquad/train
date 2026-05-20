from __future__ import annotations

import sys

from train_core.cli import main


if __name__ == "__main__":
    sys.exit(main(["run-daily-self-learning-cycle", *sys.argv[1:]]))
