import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox
import os
import threading
from pathlib import Path
from core.settings import SettingsManager
from core.agent import AgentCore
from core.music import MusicPlayer
from .settings_dialog import SettingsDialog


class NewHorizonDesignGUI:
    """主窗口GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NewHorizonDesign")
        self.root.geometry("900x650")
        self.root.minsize(800, 500)
        
        # 初始化核心模块
        self.settings = SettingsManager()
        self.agent = AgentCore()
        self.current_lang = self.settings.get("language", "zh")
        
        # 初始化音乐（可选）
        music_dir = Path(__file__).parent.parent / "music"
        self.music_player = MusicPlayer(str(music_dir) if music_dir.exists() else None)
        
        # 多语言文案
        self.i18n = {
            "zh": {
                "title": "🌌 NewHorizonDesign",
                "status_offline": "● 离线（Ollama未连接）",
                "status_online": "● 在线（Ollama已连接）",
                "persona_label": "当前角色:",
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
                "status_online": "● Online (Ollama connected)",
                "persona_label": "Active Persona:",
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
        
        # 创建UI
        self.load_theme()
        self.create_ui()
        
        # 显示状态
        self.update_status()
        
        # 显示欢迎消息
        if self.settings.get("show_welcome"):
            self.show_welcome()
    
    def load_theme(self):
        theme = self.settings.get("theme", "dark")
        font_size = self.settings.get("font_size", 11)
        
        if theme == "dark":
            self.colors = {
                "bg": "#1a1a1a", "panel": "#252526", "border": "#3e3e42", "text": "#e0e0e0",
                "muted": "#888888", "accent": "#007acc", "accent_hover": "#0099ff",
                "user_msg": "#3ab370", "ai_msg": "#569cd6", "status_online": "#4caf50",
                "status_offline": "#f44336", "music_active": "#ff6b6b"
            }
        else:
            self.colors = {
                "bg": "#f5f5f5", "panel": "#ffffff", "border": "#e0e0e0", "text": "#333333",
                "muted": "#777777", "accent": "#0066cc", "accent_hover": "#0088ff",
                "user_msg": "#2e7d32", "ai_msg": "#1565c0", "status_online": "#2e7d32",
                "status_offline": "#c62828", "music_active": "#e53935"
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
        
        # 顶部栏
        top_bar = tk.Frame(main_frame, bg=self.colors["panel"], height=60)
        top_bar.pack(fill=tk.X, pady=(0, 16))
        top_bar.pack_propagate(False)
        
        # 标题
        self.title_label = tk.Label(
            top_bar,
            text=self.i18n[self.current_lang]["title"],
            font=self.font_title,
            fg=self.colors["ai_msg"],
            bg=self.colors["panel"]
        )
        self.title_label.pack(side=tk.LEFT, padx=20)
        
        # 角色选择器
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
        
        # ✅ 修复：正确生成角色显示名称列表
        role_names = [
            self.agent.get_persona_name(self.current_lang, "nova"),
            self.agent.get_persona_name(self.current_lang, "byte"),
            self.agent.get_persona_name(self.current_lang, "muse"),
            self.agent.get_persona_name(self.current_lang, "oracle")
        ]
        self.role_var = tk.StringVar(value=self.agent.get_persona_name(self.current_lang))
        self.role_combo = ttk.Combobox(
            role_frame,
            textvariable=self.role_var,
            values=role_names,
            state="readonly",
            width=24,
            font=self.font_main
        )
        self.role_combo.pack(side=tk.LEFT)
        self.role_combo.bind("<<ComboboxSelected>>", self.on_role_change)
        
        # 右侧按钮（✅ 从右向左排列：状态 → 音乐 → 设置）
        self.status_label = tk.Label(
            top_bar,
            text=self.i18n[self.current_lang]["status_offline"],
            font=self.font_status,
            fg=self.colors["status_offline"],
            bg=self.colors["panel"]
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # ✅ 修复：安全检测 pygame（避免初始化警告）
        try:
            import pygame
            pygame_available = True
        except:
            pygame_available = False
        
        # 音乐按钮
        if pygame_available and self.music_player.enabled:
            music_text = self.i18n[self.current_lang]["music_btn"]
            self.music_btn = tk.Button(
                top_bar,
                text=music_text,
                font=("Segoe UI", 9),
                bg=self.colors["panel"],
                fg=self.colors["muted"],
                relief="flat",
                padx=12,
                pady=6,
                cursor="hand2",
                command=self.toggle_music
            )
            self.music_btn.pack(side=tk.RIGHT, padx=(0, 16))
            self.music_btn.bind("<Enter>", lambda e: self.music_btn.config(fg=self.colors["text"]))
            self.music_btn.bind("<Leave>", lambda e: self.music_btn.config(fg=self.colors["muted"]))
        else:
            # 无pygame时显示禁用状态
            self.music_btn = tk.Label(
                top_bar,
                text=self.i18n[self.current_lang]["music_disabled"],
                font=("Segoe UI", 9),
                fg="#888888",
                bg=self.colors["panel"]
            )
            self.music_btn.pack(side=tk.RIGHT, padx=(0, 16))
        
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
        
        # 配置样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox",
                       fieldbackground=self.colors["panel"],
                       background=self.colors["panel"],
                       foreground=self.colors["text"],
                       selectbackground=self.colors["accent"],
                       selectforeground="white",
                       bordercolor=self.colors["border"])
        
        # 聊天区域
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
        
        # 输入区域
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
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=self.colors["accent"])
        )
    
    def update_status(self):
        """更新Ollama连接状态"""
        if self.agent.backend.is_available:
            self.status_label.config(
                text=self.i18n[self.current_lang]["status_online"],
                fg=self.colors["status_online"]
            )
        else:
            self.status_label.config(
                text=self.i18n[self.current_lang]["status_offline"],
                fg=self.colors["status_offline"]
            )
    
    def toggle_music(self):
        if not hasattr(self, 'music_player') or not self.music_player.enabled:
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
        if hasattr(self, 'music_player') and self.music_player.enabled:
            self.music_player.set_volume(new_settings.get("music_volume", 0.3))
            if new_settings.get("music_enabled") and not self.music_player.is_playing:
                self.music_player.toggle_background()
            elif not new_settings.get("music_enabled") and self.music_player.is_playing:
                self.music_player.toggle_background()
        
        self.load_theme()
        self.root.configure(bg=self.colors["bg"])
        self.chat_display.configure(bg=self.colors["panel"], fg=self.colors["text"], font=self.font_chat)
        self.input_box.configure(bg=self.colors["panel"], fg=self.colors["text"], font=self.font_main)
        self.update_ui_language(old_lang, new_lang)
        self.update_status()
        
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
        self.status_label.config(
            text=self.i18n[new_lang]["status_online"] if self.agent.backend.is_available else self.i18n[new_lang]["status_offline"],
            fg=self.colors["status_online"] if self.agent.backend.is_available else self.colors["status_offline"]
        )
        self.settings_btn.config(text=self.i18n[new_lang]["settings_btn"])
        self.role_label.config(text=self.i18n[new_lang]["persona_label"])
        self.hint_label.config(text=self.i18n[new_lang]["hint"])
        self.send_btn.config(text=self.i18n[new_lang]["send_btn"])
        
        # 更新音乐按钮（如果存在且是Button）
        if hasattr(self, 'music_btn') and isinstance(self.music_btn, tk.Button):
            music_text = self.i18n[new_lang]["music_btn"]
            self.music_btn.config(text=music_text)
        
        # ✅ 修复：更新角色列表时使用正确参数
        role_names = [
            self.agent.get_persona_name(new_lang, "nova"),
            self.agent.get_persona_name(new_lang, "byte"),
            self.agent.get_persona_name(new_lang, "muse"),
            self.agent.get_persona_name(new_lang, "oracle")
        ]
        self.role_combo.config(values=role_names)
        self.role_combo.set(self.agent.get_persona_name(new_lang))
    
    def on_role_change(self, event=None):
        selection = self.role_var.get()
        # 通过显示名称反推 persona ID（多语言安全映射）
        persona_map = {
            "zh": {
                "Nova • 全能助手": "nova",
                "Byte • 代码专家": "byte", 
                "Muse • 创意写手": "muse",
                "Oracle • 战略顾问": "oracle"
            },
            "en": {
                "Nova • General Assistant": "nova",
                "Byte • Code Expert": "byte",
                "Muse • Creative Writer": "muse",
                "Oracle • Strategy Advisor": "oracle"
            }
        }
        persona_id = persona_map.get(self.current_lang, {}).get(selection, "nova")
        self.agent.switch_persona(persona_id)
        msg = f"Switched to: {selection}" if self.current_lang == "en" else f"已切换至: {selection}"
        self._append_message("System", msg, is_user=False)
    
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
            self.agent.clear_history()
            return
        
        # 播放发送音效
        if self.settings.get("music_enabled") and hasattr(self, 'music_player') and self.music_player.enabled:
            self.music_player.play_sound("send")
        
        # 显示用户消息
        self.input_box.delete("1.0", tk.END)
        self._append_message("You", message, is_user=True)
        
        # AI回复（异步）
        def ai_thread():
            def stream_callback(token, is_done):
                if is_done:
                    self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.send_btn.config(
                        text=self.i18n[self.current_lang]["send_btn"]
                    ))
                else:
                    self._append_stream_token(token)
            
            self.agent.chat(message, stream_callback)
            
            # 播放回复音效
            if self.settings.get("music_enabled") and hasattr(self, 'music_player') and self.music_player.enabled:
                self.root.after(100, lambda: self.music_player.play_sound("reply"))
        
        threading.Thread(target=ai_thread, daemon=True).start()
        self.send_btn.config(state=tk.DISABLED)
        self.send_btn.config(text="..." if self.current_lang == "en" else "思考中...")
    
    def _append_stream_token(self, token):
        """流式追加token（线程安全）"""
        def update():
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, token)
            if self.settings.get("auto_scroll", True):
                self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
        self.root.after(0, update)
    
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
        # 显示Ollama状态提示
        status_tip = ("\n\n💡 Ollama提示: 请先运行 'ollama serve' 并下载模型（如 qwen2.5:7b）"
                     if not self.agent.backend.is_available else "")
        welcome_msg = self.i18n[self.current_lang]["welcome"] + status_tip
        self._append_message("System", welcome_msg, is_user=False)