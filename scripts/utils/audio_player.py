from random import randint
from enum import Enum
import pygame
import os

class Audio(Enum):
    WAKEUP = "wakeup"
    READY = "ready"
    ERROR = "error"
    WIFI = "wifi"
    SLEEP = "sleep"
    REST = "rest"

class AudioPlayer:
    def __init__(self):
        self.directory = os.path.dirname(__file__)
        pygame.mixer.init()

    def play(self, audio: Audio):
        choice = randint(1, 3)
        filename = f"{audio.value}_{choice}.mp3"
        filepath = os.path.join(self.directory, filename)

        if os.path.exists(filepath):
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        else:
            print(f"❌ File not found: {filepath}")


if __name__ == "__main__":
    # Example usage
    player = AudioPlayer(library)
    player.play(Audio.WAKEUP)
