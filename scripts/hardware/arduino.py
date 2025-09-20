from typing import Any, Callable
import sys
import os

if __name__ == "__main__" or os.path.dirname(sys.argv[0])==os.path.dirname(__file__):
    from motion_map import MotionMap, BottomMotionMap, emoji_to_motion_map
else:
    from .motion_map import MotionMap, BottomMotionMap, emoji_to_motion_map

if os.path.basename(sys.argv[0]) != "main.py":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

