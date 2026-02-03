#!/usr/bin/env python3
"""
NewHorizonDesign - 完整版：设置按钮回归 + 音乐支持
单文件 | 深色主题 | 角色切换 | 设置面板 | 语言切换 | 自定义音乐（可选）
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox
import os
import json
from pathlib import Path

# ========== 音乐模块（可选依赖，自动降级）==========
MUSIC_AVAILABLE = False
pygame = None

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    MUSIC_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    print(f"[Music] Disabled (pygame not installed): {e}")

class MusicPlayer:
    """音乐播放器 - 自动检测可用性"""
    
    def __init__(self, music_dir=None):
        self.enabled = MUSIC_AVAILABLE and music_dir is not None
        self.music_dir = Path(music_dir) if music_dir else None
        self.is_playing = False
        self.volume = 0.3
        
        if self.enabled and self.music_dir.exists():
            self.sounds = {}
            for f in self.music_dir.glob("*.wav"):
                try:
                    name = f.stem.lower()
                    self.sounds[name] = pygame.mixer.Sound(str(f))
                    print(f"[Music] Loaded: {name}")
                except Exception as e:
                    print(f"[Music] Failed to load {f.name}: {e}")
        else:
            self.sounds = {}
    
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
                except Exception as e:
                    print(f"[Music] Failed to play background: {e}")
                    return False
            return False
    
    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        if self.enabled:
            pygame.mixer.music.set_volume(self.volume)
            for snd in self.sounds.values():
                snd.set_volume(self.volume * 0.7)


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
    
    def set(self, key, value):
        self.settings[key] = value
        self.save()


class SettingsDialog:
    """设置对话框 - 模态窗口（支持中英文 + 音乐设置）"""
    
    def __init__(self, parent, settings_mgr, on_apply_callback, language="zh"):
        self.parent = parent
        self.settings_mgr = settings_mgr
        self.on_apply = on_apply_callback
        self.dialog = None
        self.lang = language
        
        self.i18n = {
            "zh": {
                "title": "⚙️ 设置",
                "section_appearance": ".外观",
                "section_model": ".AI 模型",
                "section_behavior": ".行为",
                "section_music": ".🎵 音乐",
                "label_theme": "主题",
                "label_language": "语言",
                "label_font_size": "字体大小",
                "label_model": "Ollama 模型",
                "label_auto_scroll": "聊天自动滚动",
                "label_show_welcome": "显示欢迎消息",
                "label_music_enabled": "启用自定义音乐",
                "label_music_volume": "音量",
                "label_music_tip": "🎵 音乐文件请放入 music/ 文件夹",
                "theme_dark": "深色",
                "theme_light": "浅色",
                "btn_restore": "恢复默认",
                "btn_cancel": "取消",
                "btn_apply": "应用并保存"
            },
            "en": {
                "title": "⚙️ Settings",
                "section_appearance": ".Appearance",
                "section_model": ".AI Model",
                "section_behavior": ".Behavior",
                "section_music": ".🎵 Music",
                "label_theme": "Theme",
                "label_language": "Language",
                "label_font_size": "Font Size",
                "label_model": "Ollama Model",
                "label_auto_scroll": "Auto-scroll chat",
                "label_show_welcome": "Show welcome message",
                "label_music_enabled": "Enable custom music",
                "label_music_volume": "Volume",
                "label_music_tip": "🎵 Place audio files in music/ folder",
                "theme_dark": "Dark",
                "theme_light": "Light",
                "btn_restore": "Restore Defaults",
                "btn_cancel": "Cancel",
                "btn_apply": "Apply & Save"
            }
        }
        
        self.theme_var = tk.StringVar(value=settings_mgr.get("theme"))
        self.fontsize_var = tk.IntVar(value=settings_mgr.get("font_size"))
        self.model_var = tk.StringVar(value=settings_mgr.get("model"))
        self.lang_var = tk.StringVar(value=settings_mgr.get("language"))
        self.auto_scroll_var = tk.BooleanVar(value=settings_mgr.get("auto_scroll"))
        self.show_welcome_var = tk.BooleanVar(value=settings_mgr.get("show_welcome"))
        self.music_enabled_var = tk.BooleanVar(value=settings_mgr.get("music_enabled"))
        self.music_volume_var = tk.DoubleVar(value=settings_mgr.get("music_volume"))
    
    def show(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.i18n[self.lang]["title"].replace("⚙️ ", "") + " • NewHorizonDesign")
        self.dialog.geometry("600x620")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(self.dialog, bg="#252526", padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text=self.i18n[self.lang]["title"],
            font=("Segoe UI", 18, "bold"),
            fg="#569cd6",
            bg="#252526"
        ).pack(anchor=tk.W, pady=(0, 24))
        
        # === 外观设置 ===
        self.create_section(main_frame, self.i18n[self.lang]["section_appearance"], [
            (self.i18n[self.lang]["label_theme"], self.create_theme_selector),
            (self.i18n[self.lang]["label_language"], self.create_language_selector),
            (self.i18n[self.lang]["label_font_size"], self.create_fontsize_selector)
        ])
        
        # === 模型设置 ===
        self.create_section(main_frame, self.i18n[self.lang]["section_model"], [
            (self.i18n[self.lang]["label_model"], self.create_model_selector)
        ])
        
        # === 行为设置 ===
        self.create_section(main_frame, self.i18n[self.lang]["section_behavior"], [
            (self.i18n[self.lang]["label_auto_scroll"], self.create_toggle(self.auto_scroll_var)),
            (self.i18n[self.lang]["label_show_welcome"], self.create_toggle(self.show_welcome_var))
        ])
        
        # === 音乐设置 ===
        self.create_section(main_frame, self.i18n[self.lang]["section_music"], [
            (self.i18n[self.lang]["label_music_enabled"], self.create_toggle(self.music_enabled_var)),
        ])
        
        # 音量滑块（仅当pygame可用时显示）
        if MUSIC_AVAILABLE:
            vol_frame = tk.Frame(main_frame, bg="#252526")
            vol_frame.pack(fill=tk.X, pady=4)
            tk.Label(
                vol_frame,
                text=self.i18n[self.lang]["label_music_volume"],
                font=("Segoe UI", 10),
                fg="#d4d4d4",
                bg="#252526",
                width=20,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            ttk.Scale(
                vol_frame,
                from_=0.0,
                to=1.0,
                orient=tk.HORIZONTAL,
                variable=self.music_volume_var,
                length=150
            ).pack(side=tk.LEFT)
            tk.Label(
                vol_frame,
                textvariable=self.music_volume_var,
                font=("Segoe UI", 9),
                fg="#d4d4d4",
                bg="#252526",
                width=4
            ).pack(side=tk.LEFT, padx=(8, 0))
        
        # 音乐提示
        tip_frame = tk.Frame(main_frame, bg="#252526")
        tip_frame.pack(fill=tk.X, pady=(8, 16))
        tk.Label(
            tip_frame,
            text=self.i18n[self.lang]["label_music_tip"],
            font=("Segoe UI", 9, "italic"),
            fg="#888888",
            bg="#252526",
            wraplength=550
        ).pack(anchor=tk.W)
        
        # 底部按钮
        btn_frame = tk.Frame(main_frame, bg="#252526")
        btn_frame.pack(fill=tk.X, pady=(12, 0))
        
        ttk.Button(
            btn_frame,
            text=self.i18n[self.lang]["btn_restore"],
            style="Ghost.TButton",
            command=self.restore_defaults
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            btn_frame,
            text=self.i18n[self.lang]["btn_cancel"],
            style="Secondary.TButton",
            command=self.cancel
        ).pack(side=tk.RIGHT, padx=(12, 0))
        
        ttk.Button(
            btn_frame,
            text=self.i18n[self.lang]["btn_apply"],
            style="Primary.TButton",
            command=self.apply_and_save
        ).pack(side=tk.RIGHT)
        
        self.setup_styles()
        self.parent.wait_window(self.dialog)
    
    def create_section(self, parent, title, items):
        tk.Label(
            parent,
            text=title,
            font=("Segoe UI", 12, "bold"),
            fg="#a0a0a0",
            bg="#252526"
        ).pack(anchor=tk.W, pady=(16, 8))
        
        tk.Frame(parent, bg="#3e3e42", height=1).pack(fill=tk.X, pady=(0, 12))
        
        for label, creator in items:
            item_frame = tk.Frame(parent, bg="#252526")
            item_frame.pack(fill=tk.X, pady=4)
            
            tk.Label(
                item_frame,
                text=label,
                font=("Segoe UI", 10),
                fg="#d4d4d4",
                bg="#252526",
                width=20,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            creator(item_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_theme_selector(self, parent):
        frame = tk.Frame(parent, bg="#252526")
        ttk.Radiobutton(
            frame, 
            text=self.i18n[self.lang]["theme_dark"],
            variable=self.theme_var, 
            value="dark",
            style="Theme.TRadiobutton"
        ).pack(side=tk.LEFT, padx=(0, 16))
        ttk.Radiobutton(
            frame, 
            text=self.i18n[self.lang]["theme_light"],
            variable=self.theme_var, 
            value="light",
            style="Theme.TRadiobutton"
        ).pack(side=tk.LEFT)
        return frame
    
    def create_language_selector(self, parent):
        frame = tk.Frame(parent, bg="#252526")
        languages = ["zh • 中文", "en • English"]
        current = self.settings_mgr.get("language")
        display_value = "zh • 中文" if current == "zh" else "en • English"
        self.lang_var.set(display_value)
        
        ttk.Combobox(
            frame,
            textvariable=self.lang_var,
            values=languages,
            state="readonly",
            width=24,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)
        return frame
    
    def create_fontsize_selector(self, parent):
        frame = tk.Frame(parent, bg="#252526")
        ttk.Spinbox(
            frame,
            from_=9, to=16, increment=1,
            textvariable=self.fontsize_var,
            width=6,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)
        return frame
    
    def create_model_selector(self, parent):
        frame = tk.Frame(parent, bg="#252526")
        models = ["qwen2.5:7b", "llama3.2:8b", "mistral:7b", "phi3:3.8b", "custom..."]
        ttk.Combobox(
            frame,
            textvariable=self.model_var,
            values=models,
            state="readonly",
            width=28,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)
        return frame
    
    def create_toggle(self, var):
        def creator(parent):
            frame = tk.Frame(parent, bg="#252526")
            ttk.Checkbutton(
                frame,
                variable=var,
                style="Toggle.TCheckbutton"
            ).pack(side=tk.LEFT)
            return frame
        return creator
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Primary.TButton", background="#007acc", foreground="white",
                       font=("Segoe UI", 10, "bold"), padding=(16, 8), borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#0099ff")])
        
        style.configure("Secondary.TButton", background="#3e3e42", foreground="#d4d4d4",
                       font=("Segoe UI", 10), padding=(16, 8), borderwidth=0)
        style.map("Secondary.TButton", background=[("active", "#4a4a52")])
        
        style.configure("Ghost.TButton", background="#252526", foreground="#888888",
                       font=("Segoe UI", 9), padding=(8, 4), borderwidth=0)
        style.map("Ghost.TButton", foreground=[("active", "#aaaaaa")])
        
        style.configure("Theme.TRadiobutton", background="#252526", foreground="#d4d4d4",
                       font=("Segoe UI", 10))
        style.configure("Toggle.TCheckbutton", background="#252526", foreground="#d4d4d4")
    
    def restore_defaults(self):
        self.theme_var.set(self.settings_mgr.defaults["theme"])
        self.fontsize_var.set(self.settings_mgr.defaults["font_size"])
        self.model_var.set(self.settings_mgr.defaults["model"])
        self.lang_var.set("zh • 中文" if self.settings_mgr.defaults["language"] == "zh" else "en • English")
        self.auto_scroll_var.set(self.settings_mgr.defaults["auto_scroll"])
        self.show_welcome_var.set(self.settings_mgr.defaults["show_welcome"])
        self.music_enabled_var.set(self.settings_mgr.defaults["music_enabled"])
        self.music_volume_var.set(self.settings_mgr.defaults["music_volume"])
    
    def cancel(self):
        self.dialog.destroy()
    
    def apply_and_save(self):
        lang_display = self.lang_var.get()
        lang_code = lang_display.split("•")[0].strip()
        
        new_settings = {
            "theme": self.theme_var.get(),
            "font_size": self.fontsize_var.get(),
            "model": self.model_var.get(),
            "language": lang_code,
            "auto_scroll": self.auto_scroll_var.get(),
            "show_welcome": self.show_welcome_var.get(),
            "music_enabled": self.music_enabled_var.get(),
            "music_volume": self.music_volume_var.get()
        }
        
        self.settings_mgr.save(new_settings)
        self.on_apply(new_settings)
        self.dialog.destroy()


class NewHorizonDesignGUI:
    """NewHorizonDesign 主GUI（含音乐支持）"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NewHorizonDesign")
        self.root.geometry("900x650")
        self.root.minsize(800, 500)
        
        self.settings = SettingsManager()
        self.current_lang = self.settings.get("language", "zh")
        
        music_dir = Path(__file__).parent / "music"
        self.music_player = MusicPlayer(str(music_dir) if music_dir.exists() else None)
        
        self.i18n = {
            "zh": {
                "title": "🌌 NewHorizonDesign",
                "status_offline": "● 离线模式（Ollama未连接）",
                "persona_label": "当前角色:",
                "role_options": [
                    "Nova • 全能助手",
                    "Byte • 代码专家",
                    "Muse • 创意写手",
                    "Oracle • 战略顾问"
                ],
                "send_btn": "发送消息",
                "hint": "⏎ 发送  |  ⇧⏎ 换行  |  /clear 清空历史",
                "settings_btn": "⚙️ 设置",
                "music_btn": "🎵 音乐",
                "music_disabled": "🎵 (需pygame)",
                "welcome": """🌌 欢迎使用 NewHorizonDesign

从上方下拉菜单选择角色开始对话：

• Nova — 你的全能AI伙伴
• Byte — 全栈开发专家
• Muse — 灵感创作伙伴
• Oracle — 战略决策顾问

所有处理均通过本地Ollama完成 — 你的数据完全私有。

💡 提示：按 ⏎ 发送消息，⇧⏎ 换行，输入 /clear 清空历史"""
            },
            "en": {
                "title": "🌌 NewHorizonDesign",
                "status_offline": "● Offline (Ollama not connected)",
                "persona_label": "Active Persona:",
                "role_options": [
                    "Nova • General Assistant",
                    "Byte • Code Expert",
                    "Muse • Creative Writer",
                    "Oracle • Strategy Advisor"
                ],
                "send_btn": "Send Message",
                "hint": "⏎ Send  |  ⇧⏎ New line  |  /clear to clear history",
                "settings_btn": "⚙️ Settings",
                "music_btn": "🎵 Music",
                "music_disabled": "🎵 (pygame required)",
                "welcome": """🌌 Welcome to NewHorizonDesign

Select a persona from the dropdown above to begin:

• Nova — Your versatile AI companion
• Byte — Full-stack development expert
• Muse — Creative writing partner
• Oracle — Strategic decision advisor

All processing happens locally via Ollama — your data stays private.

💡 Tip: Press ⏎ to send, ⇧⏎ for new line, type /clear to reset history"""
            }
        }
        
        self.load_theme()
        self.create_ui()
        
        if self.settings.get("show_welcome"):
            self.show_welcome()
    
    def load_theme(self):
        theme = self.settings.get("theme", "dark")
        font_size = self.settings.get("font_size", 11)
        
        if theme == "dark":
            self.colors = {
                "bg": "#1a1a1a",
                "panel": "#252526",
                "border": "#3e3e42",
                "text": "#e0e0e0",
                "muted": "#888888",
                "accent": "#007acc",
                "accent_hover": "#0099ff",
                "user_msg": "#3ab370",
                "ai_msg": "#569cd6",
                "status_online": "#4caf50",
                "status_offline": "#f44336",
                "music_active": "#ff6b6b"
            }
        else:
            self.colors = {
                "bg": "#f5f5f5",
                "panel": "#ffffff",
                "border": "#e0e0e0",
                "text": "#333333",
                "muted": "#777777",
                "accent": "#0066cc",
                "accent_hover": "#0088ff",
                "user_msg": "#2e7d32",
                "ai_msg": "#1565c0",
                "status_online": "#2e7d32",
                "status_offline": "#c62828",
                "music_active": "#e53935"
            }
        
        if os.name == 'nt':
            self.font_main = font.Font(family="Segoe UI", size=10)
            self.font_title = font.Font(family="Segoe UI", size=16, weight="bold")
            self.font_chat = font.Font(family="Consolas", size=font_size)
            self.font_status = font.Font(family="Segoe UI", size=9)
        elif os.name == 'posix':
            self.font_main = font.Font(family="SF Pro Text", size=10)
            self.font_title = font.Font(family="SF Pro Display", size=16, weight="bold")
            self.font_chat = font.Font(family="Menlo", size=font_size)
            self.font_status = font.Font(family="SF Pro Text", size=9)
        else:
            self.font_main = font.Font(family="Arial", size=10)
            self.font_title = font.Font(family="Arial", size=16, weight="bold")
            self.font_chat = font.Font(family="Courier New", size=font_size)
            self.font_status = font.Font(family="Arial", size=9)
        
        self.root.configure(bg=self.colors["bg"])
    
    def create_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ============ 顶部栏（✅ 修复：按钮从左到右合理排列）============
        top_bar = tk.Frame(main_frame, bg=self.colors["panel"], height=60)
        top_bar.pack(fill=tk.X, pady=(0, 16))
        top_bar.pack_propagate(False)
        
        # 左侧：标题
        self.title_label = tk.Label(
            top_bar,
            text=self.i18n[self.current_lang]["title"],
            font=self.font_title,
            fg=self.colors["ai_msg"],
            bg=self.colors["panel"]
        )
        self.title_label.pack(side=tk.LEFT, padx=20)
        
        # 中部：角色选择器
        role_frame = tk.Frame(top_bar, bg=self.colors["panel"])
        role_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        self.role_label = tk.Label(
            role_frame,
            text=self.i18n[self.current_lang]["persona_label"],
            font=self.font_main,
            fg=self.colors["muted"],
            bg=self.colors["panel"]
        )
        self.role_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.role_var = tk.StringVar(value=self.i18n[self.current_lang]["role_options"][0])
        self.role_combo = ttk.Combobox(
            role_frame,
            textvariable=self.role_var,
            values=self.i18n[self.current_lang]["role_options"],
            state="readonly",
            width=24,
            font=self.font_main
        )
        self.role_combo.pack(side=tk.LEFT)
        self.role_combo.bind("<<ComboboxSelected>>", self.on_role_change)
        
        # 右侧：功能按钮（✅ 从右向左排列：状态 → 音乐 → 设置）
        self.status_label = tk.Label(
            top_bar,
            text=self.i18n[self.current_lang]["status_offline"],
            font=self.font_status,
            fg=self.colors["status_offline"],
            bg=self.colors["panel"]
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # 音乐按钮
        music_text = self.i18n[self.current_lang]["music_btn"] if MUSIC_AVAILABLE else self.i18n[self.current_lang]["music_disabled"]
        self.music_btn = tk.Button(
            top_bar,
            text=music_text,
            font=("Segoe UI", 9),
            bg=self.colors["panel"],
            fg=self.colors["muted"] if MUSIC_AVAILABLE else "#888888",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2" if MUSIC_AVAILABLE else "arrow",
            command=self.toggle_music if MUSIC_AVAILABLE else None
        )
        self.music_btn.pack(side=tk.RIGHT, padx=(0, 16))
        if MUSIC_AVAILABLE:
            self.music_btn.bind("<Enter>", lambda e: self.music_btn.config(fg=self.colors["text"]))
            self.music_btn.bind("<Leave>", lambda e: self.music_btn.config(fg=self.colors["muted"]))
        
        # ✅ 修复：设置按钮现在正确显示在音乐按钮左侧
        self.settings_btn = tk.Button(
            top_bar,
            text=self.i18n[self.current_lang]["settings_btn"],
            font=("Segoe UI", 9),
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.open_settings
        )
        self.settings_btn.pack(side=tk.RIGHT, padx=(0, 16))
        self.settings_btn.bind("<Enter>", lambda e: self.settings_btn.config(fg=self.colors["text"]))
        self.settings_btn.bind("<Leave>", lambda e: self.settings_btn.config(fg=self.colors["muted"]))
        
        # 配置Combobox样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox",
                       fieldbackground=self.colors["panel"],
                       background=self.colors["panel"],
                       foreground=self.colors["text"],
                       selectbackground=self.colors["accent"],
                       selectforeground="white",
                       bordercolor=self.colors["border"])
        
        # ============ 聊天区域 ============
        chat_frame = tk.Frame(main_frame, bg=self.colors["border"], relief="flat", bd=1)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=self.font_chat,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            padx=20,
            pady=20,
            spacing1=4,
            spacing2=3,
            spacing3=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.chat_display.config(state=tk.DISABLED)
        
        # ============ 输入区域 ============
        input_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        input_frame.pack(fill=tk.X)
        
        input_container = tk.Frame(input_frame, bg=self.colors["border"], relief="flat", bd=1)
        input_container.pack(fill=tk.X, pady=(0, 4))
        
        self.input_box = tk.Text(
            input_container,
            height=4,
            font=self.font_main,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            padx=16,
            pady=10,
            wrap=tk.WORD
        )
        self.input_box.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.input_box.focus_set()
        
        self.input_box.bind('<Return>', self.on_send_key)
        self.input_box.bind('<Shift-Return>', lambda e: self.input_box.insert(tk.END, '\n'))
        
        toolbar = tk.Frame(input_frame, bg=self.colors["bg"])
        toolbar.pack(fill=tk.X, pady=(8, 0))
        
        self.hint_label = tk.Label(
            toolbar,
            text=self.i18n[self.current_lang]["hint"],
            font=self.font_status,
            fg=self.colors["muted"],
            bg=self.colors["bg"]
        )
        self.hint_label.pack(side=tk.LEFT)
        
        self.send_btn = tk.Button(
            toolbar,
            text=self.i18n[self.current_lang]["send_btn"],
            font=self.font_main,
            bg=self.colors["accent"],
            fg="white",
            relief="flat",
            padx=24,
            pady=8,
            cursor="hand2",
            command=self.on_send
        )
        self.send_btn.pack(side=tk.RIGHT)
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg=self.colors["accent_hover"]))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=self.colors["accent"]))
    
    def toggle_music(self):
        if not self.music_player.enabled:
            return
        
        is_playing = self.music_player.toggle_background()
        self.music_btn.config(
            fg=self.colors["music_active"] if is_playing else self.colors["muted"]
        )
    
    def open_settings(self):
        SettingsDialog(self.root, self.settings, self.on_settings_applied, language=self.current_lang).show()
    
    def on_settings_applied(self, new_settings):
        new_lang = new_settings.get("language", "zh")
        old_lang = self.current_lang
        self.current_lang = new_lang
        
        # 应用音乐设置
        if MUSIC_AVAILABLE:
            self.music_player.set_volume(new_settings.get("music_volume", 0.3))
            if new_settings.get("music_enabled") and not self.music_player.is_playing:
                self.music_player.toggle_background()
            elif not new_settings.get("music_enabled") and self.music_player.is_playing:
                self.music_player.toggle_background()
        
        self.load_theme()
        self.root.configure(bg=self.colors["bg"])
        self.chat_display.configure(
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=self.font_chat
        )
        self.input_box.configure(
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=self.font_main
        )
        self.update_ui_language(old_lang, new_lang)
        
        if old_lang != new_lang:
            messagebox.showinfo(
                "Language Updated" if new_lang == "en" else "语言已更新",
                "Language updated successfully!\nSome static elements may require restarting the application to fully apply." 
                if new_lang == "en" else
                "语言切换成功！\n部分静态元素（如窗口标题）需重启应用才能完全生效。",
                parent=self.root
            )
    
    def update_ui_language(self, old_lang, new_lang):
        self.title_label.config(text=self.i18n[new_lang]["title"])
        self.status_label.config(text=self.i18n[new_lang]["status_offline"], 
                               fg=self.colors["status_offline"])
        self.settings_btn.config(text=self.i18n[new_lang]["settings_btn"])
        self.role_label.config(text=self.i18n[new_lang]["persona_label"])
        self.hint_label.config(text=self.i18n[new_lang]["hint"])
        self.send_btn.config(text=self.i18n[new_lang]["send_btn"])
        
        # 更新音乐按钮文本
        music_text = self.i18n[new_lang]["music_btn"] if MUSIC_AVAILABLE else self.i18n[new_lang]["music_disabled"]
        self.music_btn.config(text=music_text)
        
        self.role_combo.config(values=self.i18n[new_lang]["role_options"])
        self.role_combo.set(self.i18n[new_lang]["role_options"][0])
    
    def on_role_change(self, event=None):
        role = self.role_var.get()
        name = role.split("•")[0].strip()
        self._append_message("System", f"Switched to: {name}" if self.current_lang == "en" else f"已切换至: {name}", is_user=False)
    
    def on_send_key(self, event):
        self.on_send()
        return "break"
    
    def on_send(self):
        message = self.input_box.get("1.0", tk.END).strip()
        if not message:
            return
        
        if message == "/clear":
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.input_box.delete("1.0", tk.END)
            return
        
        # 播放发送音效（如果启用）
        if self.settings.get("music_enabled") and self.music_player.enabled:
            self.music_player.play_sound("send")
        
        self.input_box.delete("1.0", tk.END)
        self._append_message("You", message, is_user=True)
        
        agent_name = self.role_var.get().split("•")[0].strip()
        reply = ("This is a UI demonstration. In the real application, your message would be processed by the selected AI persona via Ollama."
                if self.current_lang == "en" else
                "这是UI演示。在实际应用中，您的消息将通过Ollama由所选AI角色处理。")
        
        # 播放回复音效（延迟后）
        if self.settings.get("music_enabled") and self.music_player.enabled:
            self.root.after(400, lambda: self.music_player.play_sound("reply"))
        
        self.root.after(400, lambda: self._append_message(agent_name, reply, is_user=False))
    
    def _append_message(self, sender, text, is_user=False):
        self.chat_display.config(state=tk.NORMAL)
        
        prefix = f"\n{'▌ ' if is_user else '│ '}{sender}\n"
        prefix_color = self.colors["user_msg"] if is_user else self.colors["ai_msg"]
        
        self.chat_display.insert(tk.END, prefix)
        self.chat_display.tag_add("sender", "end-2c linestart", "end-1c")
        self.chat_display.tag_config("sender", foreground=prefix_color, font=self.font_main)
        
        self.chat_display.insert(tk.END, f"{text}\n\n")
        self.chat_display.tag_add("content", "end-3c linestart", "end-2c")
        self.chat_display.tag_config("content", 
                                   foreground=self.colors["text"],
                                   lmargin1=24,
                                   lmargin2=24)
        
        if self.settings.get("auto_scroll", True):
            self.chat_display.see(tk.END)
        
        self.chat_display.config(state=tk.DISABLED)
    
    def show_welcome(self):
        self._append_message("System", self.i18n[self.current_lang]["welcome"], is_user=False)


def main():
    root = tk.Tk()
    
    try:
        if os.name == 'nt':
            root.iconbitmap(default='')
        else:
            root.iconphoto(True, tk.PhotoImage(width=1, height=1))
    except:
        pass
    
    # 创建 music 目录（如果不存在）
    music_dir = Path(__file__).parent / "music"
    music_dir.mkdir(exist_ok=True)
    readme_path = music_dir / "README.txt"
    if not readme_path.exists():
        readme_path.write_text("""NewHorizonDesign - Custom Music Folder
======================================

Place your own music files here to enable background audio during conversations.

Supported formats:
  • .wav (recommended, no extra dependencies)
  • .mp3 (requires pygame[base] + ffmpeg)

Suggested usage:
  • message_send.wav   → Plays when you send a message
  • agent_reply.wav    → Plays when agent replies
  • background.mp3     → Loops as ambient background music

How to enable:
  1. Install pygame (optional): pip install pygame
  2. Place audio files in this folder
  3. Restart NewHorizonDesign
  4. Click the 🎵 button in top bar to control playback

Note: Music is DISABLED by default if pygame is not installed.
      Your privacy is respected — no audio is transmitted anywhere.
""", encoding='utf-8')
    
    app = NewHorizonDesignGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

#代码不正常都是以实玛利的错
#都是你的错以实玛利