from .logger import setup_logger   # or Logger if you kept the class version
from .audio_player import AudioPlayer
__all__ = ["setup_logger","AudioPlayer"]   # controls what `from utils import *` exposes
