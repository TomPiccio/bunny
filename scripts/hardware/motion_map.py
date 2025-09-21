from enum import Enum
from random import choice

class MotionMap(Enum):
    '''
    Motion for the OpenRB Top Arduino
    '''
    IDLE = 0
    RAISE_EAR = 1
    COVER_EYES = 2
    FORWARD_EAR = 3
    BEND_EAR = 4
    FLAP_EAR = 5 # Flap the lower ear
    NOD = 6
    SHAKE = 7
    PET = 8
    SAD_SHAKE = 9 # Bend Down Hand and shake
    BEND_HEAD = 10
    #TODO: Not yet implemented EAR_WAVE DROP_EARS SLOW_NOD
    EAR_WAVE = 11 # Slowly wave the lower portion of the Ears
    DROP_EARS = 12 # Raise Ear slowly and drop it
    SLOW_NOD  = 13
    DETACH = -1

class BottomMotionMap(Enum):
    '''
    Motion for the Bottom Arduino
    '''
    IDLE = 0
    FLUTTER_KICK = 1
    HEART_PUMP = 2
    TOGGLE_SIT_STAND = 3
    STAND = 4
    SIT = 5

class EmotionMap(Enum):
    IDLE = 0
    HAPPY = 1
    SAD = 2
    DENY = 3
    AFFIRM = 4
    ANGRY = 5
    CRYING = 6
    SHY = 7
    SLEEPY = 8
    RELAXED = 9
    COMFORT = 10

EMOTION_TO_MOTION_MAP = {
    EmotionMap.IDLE : [MotionMap.IDLE],
    EmotionMap.HAPPY : [MotionMap.FLAP_EAR, MotionMap.NOD, MotionMap.RAISE_EAR],
    EmotionMap.SAD : [MotionMap.SAD_SHAKE, MotionMap.BEND_HEAD, MotionMap.DROP_EARS],
    EmotionMap.AFFIRM: [MotionMap.NOD, MotionMap.BEND_EAR],
    EmotionMap.DENY: [MotionMap.SHAKE, MotionMap.SAD_SHAKE],
    EmotionMap.ANGRY: [MotionMap.SHAKE, MotionMap.BEND_EAR, MotionMap.DROP_EARS],
    EmotionMap.CRYING: [MotionMap.COVER_EYES, MotionMap.BEND_HEAD],
    EmotionMap.SHY: [MotionMap.COVER_EYES, MotionMap.RAISE_EAR],
    EmotionMap.SLEEPY: [MotionMap.BEND_HEAD],
    EmotionMap.RELAXED: [MotionMap.IDLE, MotionMap.EAR_WAVE],
    EmotionMap.COMFORT: [MotionMap.PET, MotionMap.SAD_SHAKE, MotionMap.BEND_HEAD, MotionMap.SLOW_NOD]
}


EMOJI_MAP = {
    "😂": ("laughing",EmotionMap.HAPPY),
    "😭": ("crying",EmotionMap.SAD),
    "😠": ("angry",EmotionMap.ANGRY),
    "😔": ("sad",EmotionMap.SAD),
    "😍": ("loving",EmotionMap.COMFORT),
    "😲": ("surprised",EmotionMap.HAPPY),
    "😱": ("shocked",EmotionMap.DENY),
    "🤔": ("thinking",EmotionMap.HAPPY),
    "😌": ("relaxed",EmotionMap.RELAXED),
    "😴": ("sleepy",EmotionMap.SLEEPY),
    "😜": ("silly",EmotionMap.HAPPY),
    "🙄": ("confused",EmotionMap.SLEEPY),
    "😶": ("neutral",EmotionMap.IDLE),
    "🙂": ("happy",EmotionMap.HAPPY),
    "😆": ("laughing",EmotionMap.HAPPY),
    "😳": ("embarrassed",EmotionMap.SHY),
    "😉": ("winking",EmotionMap.HAPPY),
    "😎": ("cool",EmotionMap.AFFIRM),
    "🤤": ("delicious",EmotionMap.AFFIRM),
    "😘": ("kissy",EmotionMap.HAPPY),
    "😏": ("confident",EmotionMap.AFFIRM),
}

def emoji_to_motion_map(emoji: str):
    _top_motion_map = None
    _bottom_motion_map = None
    if emoji in EMOJI_MAP:
        #Top Actions
        actions = EMOTION_TO_MOTION_MAP[EMOJI_MAP[emoji][1]]
        _top_motion_map = choice(actions)
        # TODO: Integrate with Bottom Arduino
    else:
        _top_motion_map = MotionMap.IDLE
    #TODO: temporary default
    _bottom_motion_map = None
    return _top_motion_map, _bottom_motion_map
