import os
import sys

# Use explicit path modification to resolve the package properly.
# Read more: http://docs.python-guide.org/en/latest/writing/structure/#test-suite
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiociscospark  # noqa
