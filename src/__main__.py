"""Package entry point for python -m src."""

import sys

from dotenv import load_dotenv

from src.cli.main import main

if __name__ == "__main__":
    load_dotenv()
    sys.exit(main())
