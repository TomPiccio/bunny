import pygame
from random import randint
import os

class AudioPlayer:
    def __init__(self):
        self.audios = ["wakeup","ready","error","wifi","sleep","rest"]
        self.directory = os.path.dirname(__file__)

    def play(self, audio_name: str):
        if audio_name in self.audios:
            choice = randint(1,3)
            pygame.mixer.music.load(os.path.join(self.directory, f"{audio_name}_{choice}"))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # keep alive until finished
        else:
            print(f"Audio '{audio_name}' not found in library.")


if __name__ == "__main__":
    # Example usage
    library = AudioLibrary()
    player = AudioPlayer(library)

    player.play("wakeup")
