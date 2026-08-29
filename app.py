import os
import sys
import ctypes
import subprocess
import threading
import random
import string
import customtkinter as ctk
from tkinter import filedialog

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def refresh_explorer_silently():
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)

# تابع خواندن نام واقعی (Label) هر هارد از ویندوز
def get_drive_label(drive_letter):
    try:
        kernel32 = ctypes.windll.kernel32
        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        root = drive_letter.rstrip("\\") + "\\"
        rc = kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(root),
            volumeNameBuffer,
            ctypes.sizeof(volumeNameBuffer),
            None, None, None,
            fileSystemNameBuffer,
            ctypes.sizeof(fileSystemNameBuffer)
        )
        if rc and volumeNameBuffer.value.strip():
            return volumeNameBuffer.value.strip()
    except:
        pass
    return ""

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MAGIC_NAMES = [
    "Rubeus Hagrid", "Golden Snitch", "Dobby",
    "Gringotts Vault", "Hermione's Bag", "Firebolt", "Chamber of Secrets"
]

class GhostDriveApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚡ Wizard Ghost Drive (Auto-Label Edition)")
        self.geometry("660x860")
        self.resizable(False, False)

        self.lbl_title = ctk.CTkLabel(self, text="🪄 مدیریت جامع هاردهای مجازی روح", font=("Segoe UI", 20, "bold"))
        self.lbl_title.pack(pady=10)

        # ۱. انتخاب هارد واقعی مبدأ (با تشخیص خودکار اسم)
        self.frame_src = ctk.CTkFrame(self)
        self.frame_src.pack(fill="x", padx=25, pady=4)
        self.lbl_src = ctk.CTkLabel(self.frame_src, text=":هارد واقعی (مبدأ)", font=("Segoe UI", 13))
        self.lbl_src.pack(side="right", padx=10, pady=6)
        
        available_drives = self.get_available_drives()
        self.cmb_source = ctk.CTkComboBox(self.frame_src, values=available_drives, width=130, command=self.on_source_changed)
        self.cmb_source.pack(side="right", padx=5)
        self.btn_refresh = ctk.CTkButton(self.frame_src, text="🔄 رفرش", width=70, command=self.refresh_drives)
        self.btn_refresh.pack(side="left", padx=10)

        # ۲. محل ذخیره دیسک
        self.frame_path = ctk.CTkFrame(self)
        self.frame_path.pack(fill="x", padx=25, pady=4)
        self.lbl_path = ctk.CTkLabel(self.frame_path, text=":محل ذخیره دیسک", font=("Segoe UI", 13))
        self.lbl_path.pack(side="right", padx=10, pady=6)
        self.txt_save_path = ctk.CTkEntry(self.frame_path, width=240)
        self.txt_save_path.insert(0, r"D:\OfflineDrives")
        self.txt_save_path.pack(side="right", padx=5)
        self.btn_browse = ctk.CTkButton(self.frame_path, text="📁 انتخاب پوشه", width=95, fg_color="#34495e", hover_color="#2c3e50", command=self.browse_save_folder)
        self.btn_browse.pack(side="left", padx=10)

        # ۳. نام درایو
        self.frame_name = ctk.CTkFrame(self)
        self.frame_name.pack(fill="x", padx=25, pady=4)
        self.lbl_name = ctk.CTkLabel(self.frame_name, text=":نام درایو روح", font=("Segoe UI", 13))
        self.lbl_name.pack(side="right", padx=10, pady=6)
        self.txt_name = ctk.CTkEntry(self.frame_name, width=220, placeholder_text="نام هارد خودکار خوانده می‌شود")
        self.txt_name.pack(side="right", padx=5)
        self.btn_suggest = ctk.CTkButton(self.frame_name, text="🎲 اسم جادویی", width=100, fg_color="#6C5CE7", hover_color="#5844D8", command=self.suggest_name)
        self.btn_suggest.pack(side="left", padx=10)

        # ۴. حرف درایو مجازی
        self.frame_target = ctk.CTkFrame(self)
        self.frame_target.pack(fill="x", padx=25, pady=4)
        self.lbl_target = ctk.CTkLabel(self.frame_target, text=":حرف درایو مجازی", font=("Segoe UI", 13))
        self.lbl_target.pack(side="right", padx=10, pady=6)
        self.cmb_target = ctk.CTkComboBox(self.frame_target, values=["H:", "S:", "B:", "Z:", "X:", "Y:", "V:"], width=90)
        self.cmb_target.set("Z:")
        self.cmb_target.pack(side="right", padx=5)

        # دکمه ساخت و همگام‌سازی
        self.btn_create = ctk.CTkButton(self, text="✨ ساخت هارد روح جدید و تنظیم حجم", font=("Segoe UI", 14, "bold"), height=36, fg_color="#00b894", hover_color="#00a383", command=self.start_create)
        self.btn_create.pack(fill="x", padx=25, pady=4)

        self.btn_sync = ctk.CTkButton(self, text="🔄 همگام‌سازی و آپدیت تغییرات فایل‌ها", font=("Segoe UI", 14, "bold"), height=36, fg_color="#0984e3", hover_color="#0773c5", command=self.start_sync)
        self.btn_sync.pack(fill="x", padx=25, pady=4)

        # ۵. بخش مدیریت درایوهای مجازی موجود
        self.frame_v_manage = ctk.CTkFrame(self)
        self.frame_v_manage.pack(fill="x", padx=25, pady=6)

        self.lbl_v_title = ctk.CTkLabel(self.frame_v_manage, text="🎛️ مدیریت درایوهای مجازی موجود در سیستم", font=("Segoe UI", 12, "bold"), text_color="#74b9ff")
        self.lbl_v_title.pack(pady=4)

        self.frame_single_unmount = ctk.CTkFrame(self.frame_v_manage, fg_color="transparent")
        self.frame_single_unmount.pack(fill="x", padx=10, pady=3)
        
        self.cmb_mounted_vhds = ctk.CTkComboBox(self.frame_single_unmount, values=["درحال بررسی..."], width=230)
        self.cmb_mounted_vhds.pack(side="right", padx=5)
        
        self.btn_refresh_vhds = ctk.CTkButton(self.frame_single_unmount, text="🔄 لیست", width=65, command=self.refresh_mounted_vhds)
        self.btn_refresh_vhds.pack(side="right", padx=5)

        self.btn_unmount_single = ctk.CTkButton(self.frame_single_unmount, text="🔌 آن‌مانت تکی", fg_color="#d63031", hover_color="#b71517", width=110, command=self.start_unmount_single)
        self.btn_unmount_single.pack(side="left", padx=5)

        self.btn_mount_single = ctk.CTkButton(self.frame_single_unmount, text="🔗 اتصال تکی", fg_color="#e17055", hover_color="#d35400", width=100, command=self.start_mount_single)
        self.btn_mount_single.pack(side="left", padx=5)

        # ردیف عملیات گروهی
        self.frame_bulk = ctk.CTkFrame(self.frame_v_manage, fg_color="transparent")
        self.frame_bulk.pack(fill="x", padx=10, pady=6)

        self.btn_unmount_all = ctk.CTkButton(self.frame_bulk, text="💥 آن‌مانت همه درایوها (Eject All)", fg_color="#c0392b", hover_color="#962d22", font=("Segoe UI", 12, "bold"), command=self.start_unmount_all)
        self.btn_unmount_all.pack(side="left", fill="x", expand=True, padx=4)

        self.btn_mount_all = ctk.CTkButton(self.frame_bulk, text="⚡ اتصال همه درایوها (Mount All)", fg_color="#27ae60", hover_color="#219150", font=("Segoe UI", 12, "bold"), command=self.start_mount_all)
        self.btn_mount_all.pack(side="left", fill="x", expand=True, padx=4)

        # استارتاپ
        self.btn_startup = ctk.CTkButton(self, text="🚀 تنظیم اتصال خودکار همه هاردها در استارتاپ ویندوز", fg_color="#2d3436", hover_color="#636e72", height=32, command=self.setup_startup)
        self.btn_startup.pack(fill="x", padx=25, pady=4)

        # لاگ‌باکس
        self.log_box = ctk.CTkTextbox(self, height=130, font=("Consolas", 11))
        self.log_box.pack(fill="both", padx=25, pady=6)
        
        # اجرای اولیه خواندن نام هارد
        if available_drives:
            self.on_source_changed(available_drives[0])

        self.refresh_mounted_vhds()
        self.log("Ready. Auto-label detection active.")

    def log(self, text):
        self.log_box.insert("end", f"> {text}\n")
        self.log_box.see("end")

    def on_source_changed(self, choice):
        drive_letter = choice.split()[0]
        real_label = get_drive_label(drive_letter)
        if real_label:
            self.txt_name.delete(0, "end")
            self.txt_name.insert(0, real_label)
            self.log(f"Auto-detected name from drive {drive_letter}: '{real_label}'")

    def browse_save_folder(self):
        folder = filedialog.askdirectory(title="انتخاب پوشه ذخیره VHDX")
        if folder:
            win_path = os.path.normpath(folder)
            self.txt_save_path.delete(0, "end")
            self.txt_save_path.insert(0, win_path)
            self.log(f"Path set to: {win_path}")
            self.refresh_mounted_vhds()

    def get_save_dir(self):
        path = self.txt_save_path.get().strip() or r"D:\OfflineDrives"
        os.makedirs(path, exist_ok=True)
        return path

    def get_available_drives(self):
        drives = []
        for letter in string.ascii_uppercase:
            if os.path.exists(f"{letter}:\\") and letter != "C":
                label = get_drive_label(f"{letter}:")
                display = f"{letter}: ({label})" if label else f"{letter}:"
                drives.append(display)
        return drives if drives else ["E:"]

    def refresh_drives(self):
        drives = self.get_available_drives()
        self.cmb_source.configure(values=drives)
        if drives:
            self.cmb_source.set(drives[0])
            self.on_source_changed(drives[0])
        self.log("Drives refreshed.")

    def suggest_name(self):
        chosen = random.choice(MAGIC_NAMES)
        self.txt_name.delete(0, "end")
        self.txt_name.insert(0, chosen)
        self.log(f"Magic Suggested: {chosen}")

    def refresh_mounted_vhds(self):
        save_folder = self.get_save_dir()
        vhdx_files = [f for f in os.listdir(save_folder) if f.endswith(".vhdx")] if os.path.exists(save_folder) else []
        if vhdx_files:
            self.cmb_mounted_vhds.configure(values=vhdx_files)
            self.cmb_mounted_vhds.set(vhdx_files[0])
        else:
            self.cmb_mounted_vhds.configure(values=["هیچ دیسکی یافت نشد"])
            self.cmb_mounted_vhds.set("هیچ دیسکی یافت نشد")

    def run_cmd(self, cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)

    def start_create(self):
        threading.Thread(target=self._task_create, daemon=True).start()

    def _task_create(self):
        src_raw = self.cmb_source.get().split()[0]
        src = src_raw.replace(":", "").replace("\\", "") + ":"
        target_letter = self.cmb_target.get().replace(":", "").replace("\\", "")
        target = f"{target_letter}:"
        
        # اگر کاربر اسمی ننوشته باشد، نام واقعی هارد مبدا انتخاب می‌شود
        drive_name = self.txt_name.get().strip() or get_drive_label(src) or "MagicDrive"
        save_folder = self.get_save_dir()
        vhdx_path = os.path.join(save_folder, f"{drive_name.replace(' ', '_')}.vhdx")

        self.log(f"Preparing VHDX for: {drive_name}...")
        self.run_cmd(f'powershell -Command "Dismount-DiskImage -ImagePath \'{vhdx_path}\' -ErrorAction SilentlyContinue"')
        if os.path.exists(vhdx_path):
            try: os.remove(vhdx_path)
            except: pass

        dp = f"""create vdisk file="{vhdx_path}" maximum=1000000 type=expandable
select vdisk file="{vhdx_path}"
attach vdisk
create partition primary
format fs=ntfs quick label="{drive_name}"
assign letter={target_letter}
"""
        with open("dp.txt", "w") as f: f.write(dp)
        self.run_cmd("diskpart /s dp.txt")
        if os.path.exists("dp.txt"): os.remove("dp.txt")

        self.log("Copying 0-byte ghost files...")
        self.run_cmd(f'robocopy "{src}" "{target}" /E /CREATE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{target}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')

        self.log("Activating folder icons...")
        ps_icons = f"Get-ChildItem -Path '{target}\\' -Filter 'desktop.ini' -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {{ attrib +h +s $_.FullName; attrib +r $_.DirectoryName }}"
        subprocess.run(["powershell", "-Command", ps_icons])

        self.log("Simulating exact disk space...")
        ps_size = f"""$E = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='{src}'"; $S = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='{target}'"; $N = $S.FreeSpace - $E.FreeSpace; if ($N -gt 0) {{ fsutil file createnew "{target}\\SpaceFiller.dat" $N; attrib +h +s "{target}\\SpaceFiller.dat" }}"""
        subprocess.run(["powershell", "-Command", ps_size])

        refresh_explorer_silently()
        self.refresh_mounted_vhds()
        self.log(f"SUCCESS: Drive {drive_name} ({target}) is completely ready!")

    def start_sync(self):
        threading.Thread(target=self._task_sync, daemon=True).start()

    def _task_sync(self):
        src_raw = self.cmb_source.get().split()[0]
        src = src_raw.replace(":", "").replace("\\", "") + ":"
        target = self.cmb_target.get().replace(":", "").replace("\\", "") + ":"

        if not os.path.exists(f"{target}\\"):
            self.log(f"ERROR: Drive {target} is not mounted!")
            return

        self.log(f"Syncing changes from {src} to {target}...")
        self.run_cmd(f'robocopy "{src}" "{target}" /E /CREATE /PURGE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{target}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')
        refresh_explorer_silently()
        self.log(f"SUCCESS: Drive {target} updated smoothly!")

    def start_unmount_single(self):
        selected_file = self.cmb_mounted_vhds.get()
        if not selected_file or selected_file == "هیچ دیسکی یافت نشد":
            self.log("ERROR: No VHD selected!")
            return
        save_folder = self.get_save_dir()
        vhdx_path = os.path.join(save_folder, selected_file)
        self.run_cmd(f'powershell -Command "Dismount-DiskImage -ImagePath \'{vhdx_path}\' -ErrorAction SilentlyContinue"')
        refresh_explorer_silently()
        self.log(f"Unmounted: {selected_file}")

    def start_mount_single(self):
        selected_file = self.cmb_mounted_vhds.get()
        if not selected_file or selected_file == "هیچ دیسکی یافت نشد":
            self.log("ERROR: No VHD selected!")
            return
        save_folder = self.get_save_dir()
        vhdx_path = os.path.join(save_folder, selected_file)
        self.run_cmd(f'powershell -Command "Mount-DiskImage -ImagePath \'{vhdx_path}\' -ErrorAction SilentlyContinue"')
        refresh_explorer_silently()
        self.log(f"Mounted: {selected_file}")

    def start_unmount_all(self):
        save_folder = self.get_save_dir()
        self.log("Unmounting ALL virtual drives...")
        ps_cmd = f'Get-ChildItem -Path \'{save_folder}\\*.vhdx\' -ErrorAction SilentlyContinue | ForEach-Object {{ Dismount-DiskImage -ImagePath $_.FullName -ErrorAction SilentlyContinue }}'
        self.run_cmd(f'powershell -Command "{ps_cmd}"')
        refresh_explorer_silently()
        self.log("SUCCESS: All virtual drives unmounted!")

    def start_mount_all(self):
        save_folder = self.get_save_dir()
        self.log("Mounting ALL virtual drives...")
        ps_cmd = f'Get-ChildItem -Path \'{save_folder}\\*.vhdx\' -ErrorAction SilentlyContinue | ForEach-Object {{ Mount-DiskImage -ImagePath $_.FullName -ErrorAction SilentlyContinue }}'
        self.run_cmd(f'powershell -Command "{ps_cmd}"')
        refresh_explorer_silently()
        self.log("SUCCESS: All virtual drives mounted!")

    def setup_startup(self):
        save_folder = self.get_save_dir()
        bat_content = f'@echo off\npowershell -Command "Get-ChildItem -Path \'{save_folder}\\*.vhdx\' -ErrorAction SilentlyContinue | ForEach-Object {{ Mount-DiskImage -ImagePath $_.FullName }}"\n'
        startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        bat_path = os.path.join(startup_dir, "AutoMountGhostDrives.bat")
        with open(bat_path, "w") as f:
            f.write(bat_content)
        self.log(f"SUCCESS: Auto-mount enabled on Startup for: {save_folder}")

if __name__ == "__main__":
    app = GhostDriveApp()
    app.mainloop()
