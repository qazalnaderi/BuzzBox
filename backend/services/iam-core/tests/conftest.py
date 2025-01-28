import sys
import os
from pathlib import Path

# Get the absolute path to the project root
project_root = Path(__file__).parent.parent

# Add the project root to PYTHONPATH
sys.path.append(str(project_root))