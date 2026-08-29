import os
import sys
import ctypes
import subprocess
import threading
import random
import string
from tkinter import filedialog
import customtkinter as ctk

# اجرای خودکار با دسترسی Administrator
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# رفرش بی‌صدا و بدون پرش اکسپلورر
def refresh_explorer_silently():
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MAGIC_NAMES = [
    "Rubeus Hagrid", "Golden Snitch", "Dobby",
    "Gringotts Vault", "Hermione's Bag", "Firebolt", "Chamber of Secrets"
]

class GhostDriveApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚡ Wizard Ghost Drive (Custom Storage Edition)")
        self.geometry("640x790")
        self.resizable(False, False)

        self.lbl_title = ctk.CTkLabel(self, text="🪄 مدیریت جامع هاردهای مجازی روح", font=("Segoe UI", 20, "bold"))
        self.lbl_title.pack(pady=10)

        # انتخاب درایو واقعی مبدأ
        self.frame_src = ctk.CTkFrame(self)
        self.frame_src.pack(fill="x", padx=25, pady=5)
        self.lbl_src = ctk.CTkLabel(self.frame_src, text=":هارد واقعی (مبدأ)", font=("Segoe UI", 13))
        self.lbl_src.pack(side="right", padx=10, pady=8)
        self.cmb_source = ctk.CTkComboBox(self.frame_src, values=self.get_available_drives(), width=120)
        self.cmb_source.pack(side="right", padx=5)
        self.btn_refresh = ctk.CTkButton(self.frame_src, text="🔄 رفرش", width=70, command=self.refresh_drives)
        self.btn_refresh.pack(side="left", padx=10)

        # انتخاب مسیر ذخیره‌سازی VHDX (امکان جدید)
        self.frame_save = ctk.CTkFrame(self)
        self.frame_save.pack(fill="x", padx=25, pady=5)
        self.lbl_save = ctk.CTkLabel(self.frame_save, text=":محل ذخیره فایل دیسک", font=("Segoe UI",
