import os
import sys
import ctypes
import subprocess
import threading
import random
import string
import customtkinter as ctk
from tkinter import filedialog

# اجرای خودکار در حالت ادمین
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# رفرش بی‌صدا و بدون پرش صفحه اکسپلورر
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
        self.title("⚡ Wizard Ghost Drive (Ultimate Edition)")
        self.geometry("640x780")
        self.resizable(False, False)

        self.lbl_title = ctk.CTkLabel(self, text="🪄 مدیریت جامع هاردهای مجازی روح", font=("Segoe UI", 20, "bold"))
        self.lbl_title.pack(pady=10)

        # ۱. انتخاب هارد واقعی (مبدأ)
        self.frame_src = ctk.CTkFrame(self)
        self.frame_src.pack(fill="x", padx=25, pady=5)
        self.lbl_src = ctk.CTkLabel(self.frame_src, text=":هارد واقعی (مبدأ)", font=("Segoe UI", 13))
        self.lbl_src.pack(side="right", padx=10, pady=8)
        self.cmb_source = ctk.CTkComboBox(self.frame_src, values=self.get_available_drives(), width=120)
        self.cmb_source.pack(side="right", padx=5)
        self.btn_refresh = ctk.CTkButton(self.frame_src, text="🔄 رفرش", width=70, command=self.refresh_drives)
        self.btn_refresh.pack(side="left", padx=10)

        # ۲. محل ذخیره فایل دیسک مجازی
        self.frame_path = ctk.CTkFrame(self)
        self.frame_path.pack(fill="x", padx=25, pady=5)
        self.lbl_path = ctk.CTkLabel(self.frame_path, text=":محل ذخیره دیسک", font=("Segoe UI", 13))
        self.lbl_path.pack(side="right", padx=10, pady=8)
        self.txt_save_path = ctk.CTkEntry(self.frame_path, width=240)
        self.txt_save_path.insert(0, r"D:\OfflineDrives")
        self.txt_save_path.pack(side="right", padx=5)
        self.btn_browse = ctk.CTkButton(self.frame_path, text="📁 انتخاب پوشه", width=95, fg_color="#34495e", hover_color="#2c3e50", command=self.browse_save_folder)
        self.btn_browse.pack(side="left", padx=10)

        # ۳. نام درایو
        self.frame_name = ctk.CTkFrame(self)
        self.frame_name.pack(fill="x", padx=25, pady=5)
        self.lbl_name = ctk.CTkLabel(self.frame_name, text=":نام درایو روح", font=("Segoe UI", 13))
        self.lbl_name.pack(side="right", padx=10, pady=8)
        self.txt_name = ctk.CTkEntry(self.frame_name, width=220, placeholder_text="مثلا Golden Snitch")
        self.txt_name.pack(side="right", padx=5)
        self.btn_suggest = ctk.CTkButton(self.frame_name, text="🎲 اسم جادویی", width=100, fg_color="#6C5CE7", hover_color="#5844D8", command=self.suggest_name)
        self.btn_suggest.pack(side="left", padx=10)

        # ۴. حرف درایو مجازی
        self.frame_target = ctk.CTkFrame(self)
        self.frame_target.pack(fill="x", padx=25, pady=5)
        self.lbl_target = ctk.CTkLabel(self.frame_target, text=":حرف درایو مجازی", font=("Segoe UI", 13))
        self.lbl_target.pack(side="right", padx=10, pady=8)
        self.cmb_target = ctk.CTkComboBox(self.frame_target, values=["H:", "S:", "B:", "X:", "Y:", "Z:", "V:", "W:"], width=90)
        self.cmb_target.set("S:")
        self.cmb_target.pack(side="right", padx=5)

        # دکمه ساخت
        self.btn_create = ctk.CTkButton(self, text="✨ ساخت هارد روح جدید و تنظیم حجم", font=("Segoe UI", 14, "bold"), height=38, fg_color="#00b894", hover_color="#00a383", command=self.start_create)
        self.btn_create.pack(fill="x", padx=25, pady=5)

        # دکمه همگام‌سازی
        self.btn_sync = ctk.CTkButton(self, text="🔄 همگام‌سازی و آپدیت تغییرات فایل‌ها", font=("Segoe UI", 14, "bold"), height=38, fg_color="#0984e3", hover_color="#0773c5", command=self.start_sync)
        self.btn_sync.pack(fill="x", padx=25, pady=5)

        # فریم مدیریت
        self.frame_manage = ctk.CTkFrame(self)
        self.frame_manage.pack(fill="x", padx=25, pady=5)
        
        self.btn_unmount = ctk.CTkButton(self.frame_manage, text="🔌 آن‌مانت / مخفی کردن", fg_color="#d63031", hover_color="#b71517", width=135, command=self.start_unmount)
        self.btn_unmount.pack(side="left", padx=8, pady=8)

        self.btn_mount = ctk.CTkButton(self.frame_manage, text="🔗 اتصال مجدد (Mount)", fg_color="#e17055", hover_color="#d35400", width=135, command=self.start_mount)
        self.btn_mount.pack(side="left", padx=5)

        self.btn_startup = ctk.CTkButton(self.frame_manage, text="🚀 اتصال در استارتاپ", fg_color="#2d3436", hover_color="#636e72", width=150, command=self.setup_startup)
        self.btn_startup.pack(side="right", padx=8)

        # گزارش لاگ
        self.log_box = ctk.CTkTextbox(self, height=150, font=("Consolas", 11))
        self.log_box.pack(fill="both", padx=25, pady=10)
        self.log("Ready. Select options and start...")

    def log(self, text):
        self.log_box.insert("end", f"> {text}\n")
        self.log_box.see("end")

    def browse_save_folder(self):
        folder = filedialog.askdirectory(title="انتخاب پوشه برای ذخیره فایل‌های هارد مجازی (VHDX)")
        if folder:
            win_path = os.path.normpath(folder)
            self.txt_save_path.delete(0, "end")
            self.txt_save_path.insert(0, win_path)
            self.log(f"Storage path set to: {win_path}")

    def get_save_dir(self):
        path = self.txt_save_path.get().strip() or r"D:\OfflineDrives"
        os.makedirs(path, exist_ok=True)
        return path

    def get_available_drives(self):
        drives = []
        for letter in string.ascii_uppercase:
            if os.path.exists(f"{letter}:\\") and letter != "C":
                drives.append(f"{letter}:")
        return drives if drives else ["E:"]

    def refresh_drives(self):
        self.cmb_source.configure(values=self.get_available_drives())
        self.log("Drives refreshed.")

    def suggest_name(self):
        chosen = random.choice(MAGIC_NAMES)
        self.txt_name.delete(0, "end")
        self.txt_name.insert(0, chosen)
        self.log(f"Magic Suggestion: {chosen}")

    def run_cmd(self, cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)

    def start_create(self):
        threading.Thread(target=self._task_create, daemon=True).start()

    def _task_create(self):
        src = self.cmb_source.get().replace(":", "").replace("\\", "") + ":"
        target = self.cmb_target.get().replace(":", "").replace("\\", "") + ":"
        drive_name = self.txt_name.get().strip() or "MagicDrive"
        save_folder = self.get_save_dir()
        vhdx_path = os.path.join(save_folder, f"{drive_name.replace(' ', '_')}.vhdx")

        self.log(f"Creating VHDX inside: {save_folder}...")
        dp = f"""create vdisk file="{vhdx_path}" maximum=1000000 type=expandable
select vdisk file="{vhdx_path}"
attach vdisk
create partition primary
format fs=ntfs quick label="{drive_name}"
assign letter={target[0]}
"""
        with open("dp.txt", "w") as f: f.write(dp)
        self.run_cmd("diskpart /s dp.txt")
        if os.path.exists("dp.txt"): os.remove("dp.txt")

        self.log("Creating 0-byte ghost structures...")
        self.run_cmd(f'robocopy "{src}" "{target}" /E /CREATE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{target}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')

        self.log("Activating folder icons...")
        ps_icons = f"Get-ChildItem -Path '{target}\\' -Filter 'desktop.ini' -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {{ attrib +h +s $_.FullName; attrib +r $_.DirectoryName }}"
        subprocess.run(["powershell", "-Command", ps_icons])

        self.log("Matching exact disk capacity...")
        ps_size = f"""$E = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='{src}'"; $S = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='{target}'"; $N = $S.FreeSpace - $E.FreeSpace; if ($N -gt 0) {{ fsutil file createnew "{target}\\SpaceFiller.dat" $N; attrib +h +s "{target}\\SpaceFiller.dat" }}"""
        subprocess.run(["powershell", "-Command", ps_size])

        refresh_explorer_silently()
        self.log(f"SUCCESS: Drive {drive_name} ({target}) is completely ready!")

    def start_sync(self):
        threading.Thread(target=self._task_sync, daemon=True).start()

    def _task_sync(self):
        src = self.cmb_source.get().replace(":", "").replace("\\", "") + ":"
        target = self.cmb_target.get().replace(":", "").replace("\\", "") + ":"

        if not os.path.exists(f"{target}\\"):
            self.log(f"ERROR: Drive {target} is not mounted!")
            return

        self.log(f"Syncing changes from {src} to {target}...")
        self.run_cmd(f'robocopy "{src}" "{target}" /E /CREATE /PURGE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{target}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')
        refresh_explorer_silently()
        self.log(f"SUCCESS: Drive {target} updated smoothly!")

    def start_unmount(self):
        drive_name = self.txt_name.get().strip() or "MagicDrive"
        save_folder = self.get_save_dir()
        vhdx_path = os.path.join(save_folder, f"{drive_name.replace(' ', '_')}.vhdx")

        if not os.path.exists(vhdx_path):
            self.log("ERROR: VHDX file not found in selected directory!")
            return
        dp = f"""select vdisk file="{vhdx_path}"\ndetach vdisk\n"""
        with open("dp.txt", "w") as f: f.write(dp)
        self.run_cmd("diskpart /s dp.txt")
        if os.path.exists("dp.txt"): os.remove("dp.txt")
        refresh_explorer_silently()
        self.log(f"Drive {drive_name} unmounted/hidden.")

    def start_mount(self):
        drive_name = self.txt_name.get().strip() or "MagicDrive"
        target = self.cmb_target.get().replace(":", "").replace("\\", "")
        save_folder = self.get_save_dir()
        vhdx_path = os.path.join(save_folder, f"{drive_name.replace(' ', '_')}.vhdx")

        if not os.path.exists(vhdx_path):
            self.log("ERROR: VHDX file not found in selected directory!")
            return
        dp = f"""select vdisk file="{vhdx_path}"\nattach vdisk\nselect partition 1\nassign letter={target}\n"""
        with open("dp.txt", "w") as f: f.write(dp)
        self.run_cmd("diskpart /s dp.txt")
        if os.path.exists("dp.txt"): os.remove("dp.txt")
        refresh_explorer_silently()
        self.log(f"Drive {drive_name} mounted as {target}:")

    def setup_startup(self):
        save_folder = self.get_save_dir()
        bat_content = f'@echo off\npowershell -Command "Get-ChildItem -Path \'{save_folder}\\*.vhdx\' | ForEach-Object {{ Mount-DiskImage -ImagePath $_.FullName }}"\n'
        startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        bat_path = os.path.join(startup_dir, "AutoMountGhostDrives.bat")
        with open(bat_path, "w") as f:
            f.write(bat_content)
        self.log(f"SUCCESS: Auto-mount on Windows Startup enabled for: {save_folder}")

if __name__ == "__main__":
    app = GhostDriveApp()
    app.mainloop()
