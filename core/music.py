import pygame
from pathlib import Path

class MusicPlayer:
    """音乐播放器 - 可选依赖"""
    
    def __init__(self, music_dir=None):
        self.enabled = False
        self.music_dir = None
        self.is_playing = False
        self.volume = 0.3
        self.sounds = {}
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
        except:
            return
        
        if music_dir and Path(music_dir).exists():
            self.music_dir = Path(music_dir)
            self._load_sounds()
    
    def _load_sounds(self):
        for f in self.music_dir.glob("*.wav"):
            try:
                name = f.stem.lower()
                self.sounds[name] = pygame.mixer.Sound(str(f))
            except:
                pass
    
    def play_sound(self, name):
        if not self.enabled or not self.sounds:
            return
        
        aliases = {
            "send": ["message_send", "send", "click"],
            "reply": ["agent_reply", "reply", "beep"]
        }
        
        for alias in aliases.get(name, [name]):
            if alias in self.sounds:
                try:
                    self.sounds[alias].set_volume(self.volume * 0.7)
                    self.sounds[alias].play()
                    return
                except:
                    pass
    
    def toggle_background(self):
        if not self.enabled or not self.music_dir:
            return False
        
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            return False
        else:
            bg_files = list(self.music_dir.glob("background.*")) + list(self.music_dir.glob("bg.*"))
            if bg_files:
                try:
                    pygame.mixer.music.load(str(bg_files[0]))
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play(-1)
                    self.is_playing = True
                    return True
                except:
                    return False
            return False
    
    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        if self.enabled:
            pygame.mixer.music.set_volume(self.volume)
            for snd in self.sounds.values():
                snd.set_volume(self.volume * 0.7)