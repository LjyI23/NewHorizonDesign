import json
from pathlib import Path

class SettingsManager:
    """设置管理器 - 持久化配置"""
    
    def __init__(self):
        self.config_path = Path.home() / ".newhorizon" / "config.json"
        self.defaults = {
            "theme": "dark",
            "font_size": 11,
            "model": "qwen2.5:7b",
            "language": "zh",
            "auto_scroll": True,
            "show_welcome": True,
            "music_enabled": False,
            "music_volume": 0.3
        }
        self.settings = self.load()
    
    def load(self):
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {**self.defaults, **data}
        except:
            pass
        return self.defaults.copy()
    
    def save(self, settings=None):
        if settings:
            self.settings = settings
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        return self.settings.get(key, default or self.defaults.get(key))