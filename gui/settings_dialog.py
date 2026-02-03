import tkinter as tk
from tkinter import ttk

class SettingsDialog:
    """设置对话框 - 带滚动条（Apply按钮在底部）"""
    
    def __init__(self, parent, settings_mgr, on_apply_callback, language="zh"):
        self.parent = parent
        self.settings_mgr = settings_mgr
        self.on_apply = on_apply_callback
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
        self.dialog.geometry("620x500")  # 稍微加宽
        self.dialog.minsize(620, 400)    # 允许最小高度
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # ✅ 关键：创建带滚动条的主框架
        main_frame = tk.Frame(self.dialog, bg="#252526")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动区域容器
        canvas = tk.Canvas(main_frame, bg="#252526", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#252526")
        
        # 配置滚动
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮（Windows）
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        # Linux 鼠标滚轮支持
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True, padx=24, pady=(20, 12))
        scrollbar.pack(side="right", fill="y", pady=20)
        
        # 标题
        tk.Label(
            scrollable_frame,
            text=self.i18n[self.lang]["title"],
            font=("Segoe UI", 18, "bold"),
            fg="#569cd6",
            bg="#252526"
        ).pack(anchor=tk.W, pady=(0, 24))
        
        # 外观设置
        self.create_section(scrollable_frame, self.i18n[self.lang]["section_appearance"], [
            (self.i18n[self.lang]["label_theme"], self.create_theme_selector),
            (self.i18n[self.lang]["label_language"], self.create_language_selector),
            (self.i18n[self.lang]["label_font_size"], self.create_fontsize_selector)
        ])
        
        # 模型设置
        self.create_section(scrollable_frame, self.i18n[self.lang]["section_model"], [
            (self.i18n[self.lang]["label_model"], self.create_model_selector)
        ])
        
        # 行为设置
        self.create_section(scrollable_frame, self.i18n[self.lang]["section_behavior"], [
            (self.i18n[self.lang]["label_auto_scroll"], self.create_toggle(self.auto_scroll_var)),
            (self.i18n[self.lang]["label_show_welcome"], self.create_toggle(self.show_welcome_var))
        ])
        
        # 音乐设置
        self.create_section(scrollable_frame, self.i18n[self.lang]["section_music"], [
            (self.i18n[self.lang]["label_music_enabled"], self.create_toggle(self.music_enabled_var)),
        ])
        
        # 音量滑块
        try:
            import pygame
            vol_frame = tk.Frame(scrollable_frame, bg="#252526")
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
        except:
            pass
        
        # 音乐提示
        tip_frame = tk.Frame(scrollable_frame, bg="#252526")
        tip_frame.pack(fill=tk.X, pady=(8, 24))
        tk.Label(
            tip_frame,
            text=self.i18n[self.lang]["label_music_tip"],
            font=("Segoe UI", 9, "italic"),
            fg="#888888",
            bg="#252526",
            wraplength=550
        ).pack(anchor=tk.W)
        
        # ✅ 关键：底部按钮栏（固定在对话框底部，不在滚动区域内）
        btn_frame = tk.Frame(self.dialog, bg="#252526", height=60)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        btn_frame.pack_propagate(False)  # 保持高度
        
        # 恢复默认按钮
        restore_btn = tk.Button(
            btn_frame,
            text=self.i18n[self.lang]["btn_restore"],
            font=("Segoe UI", 9),
            bg="#252526",
            fg="#888888",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.restore_defaults
        )
        restore_btn.pack(side=tk.LEFT, padx=24)
        restore_btn.bind("<Enter>", lambda e: restore_btn.config(fg="#aaaaaa"))
        restore_btn.bind("<Leave>", lambda e: restore_btn.config(fg="#888888"))
        
        # 取消按钮
        cancel_btn = tk.Button(
            btn_frame,
            text=self.i18n[self.lang]["btn_cancel"],
            font=("Segoe UI", 10),
            bg="#3e3e42",
            fg="#d4d4d4",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.cancel
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 16))
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#4a4a52", fg="white"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg="#3e3e42", fg="#d4d4d4"))
        
        # ✅ Apply 按钮（最右侧，醒目蓝色）
        apply_btn = tk.Button(
            btn_frame,
            text=self.i18n[self.lang]["btn_apply"],
            font=("Segoe UI", 10, "bold"),
            bg="#007acc",
            fg="white",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.apply_and_save
        )
        apply_btn.pack(side=tk.RIGHT, padx=(0, 16))
        apply_btn.bind("<Enter>", lambda e: apply_btn.config(bg="#0099ff"))
        apply_btn.bind("<Leave>", lambda e: apply_btn.config(bg="#007acc"))
        
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
        tk.Radiobutton(
            frame, 
            text=self.i18n[self.lang]["theme_dark"],
            variable=self.theme_var, 
            value="dark",
            bg="#252526",
            fg="#d4d4d4",
            selectcolor="#007acc",
            activebackground="#252526",
            activeforeground="#d4d4d4"
        ).pack(side=tk.LEFT, padx=(0, 16))
        tk.Radiobutton(
            frame, 
            text=self.i18n[self.lang]["theme_light"],
            variable=self.theme_var, 
            value="light",
            bg="#252526",
            fg="#d4d4d4",
            selectcolor="#007acc",
            activebackground="#252526",
            activeforeground="#d4d4d4"
        ).pack(side=tk.LEFT)
        return frame
    
    def create_language_selector(self, parent):
        frame = tk.Frame(parent, bg="#252526")
        languages = ["zh • 中文", "en • English"]
        current = self.settings_mgr.get("language")
        display_value = "zh • 中文" if current == "zh" else "en • English"
        self.lang_var.set(display_value)
        
        combo = ttk.Combobox(
            frame,
            textvariable=self.lang_var,
            values=languages,
            state="readonly",
            width=24,
            font=("Segoe UI", 10)
        )
        combo.pack(side=tk.LEFT)
        return frame
    
    def create_fontsize_selector(self, parent):
        frame = tk.Frame(parent, bg="#252526")
        spin = ttk.Spinbox(
            frame,
            from_=9,
            to=16,
            increment=1,
            textvariable=self.fontsize_var,
            width=6,
            font=("Segoe UI", 10)
        )
        spin.pack(side=tk.LEFT)
        return frame
    
    def create_model_selector(self, parent):
        frame = tk.Frame(parent, bg="#252526")
        models = ["qwen2.5:7b", "llama3.2:8b", "mistral:7b", "phi3:3.8b", "custom..."]
        combo = ttk.Combobox(
            frame,
            textvariable=self.model_var,
            values=models,
            state="readonly",
            width=28,
            font=("Segoe UI", 10)
        )
        combo.pack(side=tk.LEFT)
        return frame
    
    def create_toggle(self, var):
        def creator(parent):
            frame = tk.Frame(parent, bg="#252526")
            check = tk.Checkbutton(
                frame,
                variable=var,
                bg="#252526",
                activebackground="#252526",
                selectcolor="#007acc",
                fg="#d4d4d4",
                activeforeground="#d4d4d4"
            )
            check.pack(side=tk.LEFT)
            return frame
        return creator
    
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