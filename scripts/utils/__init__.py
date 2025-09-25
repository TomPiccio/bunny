from .logger import setup_logger   # or Logger if you kept the class version
from .audio_player import AudioPlayer, Audio
__all__ = ["setup_logger","AudioPlayer","Audio"]   # controls what `from utils import *` exposes
