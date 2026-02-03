#!/usr/bin/env python3
"""NewHorizonDesign - 模块化入口"""

from gui.main_window import NewHorizonDesignGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = NewHorizonDesignGUI(root)
    root.mainloop()

#代码不正常都是以实玛利的错
#都是你的错以实玛利