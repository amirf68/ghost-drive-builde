import os
import sys
import ctypes
import subprocess
import threading
import random
import string
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# اجرای خودکار در حالت Administrator
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
        self.title("⚡ Wizard Ghost Drive (Disk Management Edition)")
        self.geometry("700x920")
        self.resizable(False, False)

        self.lbl_title = ctk.CTkLabel(self, text="🪄 مدیریت جامع هاردهای مجازی روح", font=("Segoe UI", 20, "bold"))
        self.lbl_title.pack(pady=10)

        # ۱. انتخاب هارد واقعی مبدأ
        self.frame_src = ctk.CTkFrame(self)
        self.frame_src.pack(fill="x", padx=25, pady=4)
        self.lbl_src = ctk.CTkLabel(self.frame_src, text=":هارد واقعی (مبدأ)", font=("Segoe UI", 13))
        self.lbl_src.pack(side="right", padx=10, pady=6)
        
        available_drives = self.get_available_drives()
        self.cmb_source = ctk.CTkComboBox(self.frame_src, values=available_drives, width=140, command=self.on_source_changed)
        self.cmb_source.pack(side="right", padx=5)
        self.btn_refresh = ctk.CTkButton(self.frame_src, text="🔄 رفرش", width=70, command=self.refresh_drives)
        self.btn_refresh.pack(side="left", padx=10)

        # ۲. محل ذخیره دیسک
        self.frame_path = ctk.CTkFrame(self)
        self.frame_path.pack(fill="x", padx=25, pady=4)
        self.lbl_path = ctk.CTkLabel(self.frame_path, text=":محل ذخیره VHDX", font=("Segoe UI", 13))
        self.lbl_path.pack(side="right", padx=10, pady=6)
        self.txt_save_path = ctk.CTkEntry(self.frame_path, width=250)
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

        # ۴. حرف درایو و ساخت
        self.frame_target = ctk.CTkFrame(self)
        self.frame_target.pack(fill="x", padx=25, pady=4)
        self.lbl_target = ctk.CTkLabel(self.frame_target, text=":حرف درایو مجازی", font=("Segoe UI", 13))
        self.lbl_target.pack(side="right", padx=10, pady=6)
        self.cmb_target = ctk.CTkComboBox(self.frame_target, values=["H:", "S:", "B:", "Z:", "X:", "Y:", "V:"], width=90)
        self.cmb_target.set("Z:")
        self.cmb_target.pack(side="right", padx=5)

        self.btn_create = ctk.CTkButton(self.frame_target, text="✨ ساخت هارد روح جدید و تنظیم حجم", font=("Segoe UI", 13, "bold"), fg_color="#00b894", hover_color="#00a383", command=self.start_create)
        self.btn_create.pack(side="left", fill="x", expand=True, padx=10, pady=6)

        # ۵. باکس شبیه‌ساز Disk Management (فقط برای هاردهای روح)
        self.frame_vbox = ctk.CTkFrame(self)
        self.frame_vbox.pack(fill="both", expand=True, padx=25, pady=8)

        self.frame_vbox_header = ctk.CTkFrame(self.frame_vbox, fg_color="transparent")
        self.frame_vbox_header.pack(fill="x", padx=10, pady=5)
        
        self.lbl_vbox_title = ctk.CTkLabel(self.frame_vbox_header, text="💽 مدیریت هاردهای مجازی فعال (راست‌کلیک برای عملیات)", font=("Segoe UI", 13, "bold"), text_color="#74b9ff")
        self.lbl_vbox_title.pack(side="right", padx=5)

        self.btn_refresh_cards = ctk.CTkButton(self.frame_vbox_header, text="🔄 رفرش دیسک‌ها", width=100, command=self.load_virtual_disks_ui)
        self.btn_refresh_cards.pack(side="left", padx=5)

        self.btn_mount_all = ctk.CTkButton(self.frame_vbox_header, text="⚡ اتصال همه", width=80, fg_color="#27ae60", hover_color="#219150", command=self.start_mount_all)
        self.btn_mount_all.pack(side="left", padx=5)

        self.btn_unmount_all = ctk.CTkButton(self.frame_vbox_header, text="💥 قطع همه", width=80, fg_color="#c0392b", hover_color="#962d22", command=self.start_unmount_all)
        self.btn_unmount_all.pack(side="left", padx=5)

        # اسکرول باکس کارت‌های دیسک مجازی
        self.scroll_disks = ctk.CTkScrollableFrame(self.frame_vbox, height=220)
        self.scroll_disks.pack(fill="both", expand=True, padx=10, pady=5)

        # لاگ باکس کوچک
        self.log_box = ctk.CTkTextbox(self, height=110, font=("Consolas", 11))
        self.log_box.pack(fill="x", padx=25, pady=6)

        # منوی راست‌کلیک مخفی
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2f3542", fg="white", activebackground="#70a1ff", activeforeground="black", font=("Segoe UI", 10))
        self.selected_vhd_context = None

        if available_drives:
            self.on_source_changed(available_drives[0])

        self.load_virtual_disks_ui()
        self.log("Ready. Virtual Disk Management Box loaded.")

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
            self.load_virtual_disks_ui()

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
        self.log(f"Suggested: {chosen}")

    def run_cmd(self, cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # سیستم خواندن و نمایش فقط هاردهای مجازی
    def get_virtual_disks_info(self):
        save_folder = self.get_save_dir()
        vhdx_files = [f for f in os.listdir(save_folder) if f.endswith(".vhdx")] if os.path.exists(save_folder) else []
        
        # دریافت وضعیت اتصالات از ویندوز با پاورشل
        ps_cmd = """
        Get-Disk | Where-Object { $_.BusType -eq 'File Backed Virtual' } | ForEach-Object {
            $disk = $_
            $p = $disk | Get-Partition | Where-Object { $_.DriveLetter } | Select-Object -First 1
            $img = Get-DiskImage -DiskNumber $disk.Number -ErrorAction SilentlyContinue
            if ($img.ImagePath) {
                Write-Output "$($img.ImagePath)|$($p.DriveLetter)"
            }
        }
        """
        res = self.run_cmd(f'powershell -Command "{ps_cmd}"')
        attached_map = {}
        if res.stdout:
            for line in res.stdout.strip().splitlines():
                if "|" in line:
                    path, letter = line.strip().split("|")
                    attached_map[os.path.normpath(path).lower()] = letter

        disks_data = []
        for file in vhdx_files:
            full_path = os.path.normpath(os.path.join(save_folder, file))
            name = file.replace(".vhdx", "").replace("_", " ")
            is_attached = full_path.lower() in attached_map
            letter = attached_map.get(full_path.lower(), "")
            
            disks_data.append({
                "filename": file,
                "path": full_path,
                "name": name,
                "attached": is_attached,
                "letter": f"{letter}:" if letter else "قطع اتصال"
            })
        return disks_data

    def load_virtual_disks_ui(self):
        # پاکسازی کارت‌های قبلی
        for widget in self.scroll_disks.winfo_children():
            widget.destroy()

        disks = self.get_virtual_disks_info()
        if not disks:
            lbl_empty = ctk.CTkLabel(self.scroll_disks, text="هیچ هارد مجازی (VHDX) در این پوشه یافت نشد.", text_color="gray")
            lbl_empty.pack(pady=30)
            return

        for idx, disk in enumerate(disks):
            card = ctk.CTkFrame(self.scroll_disks, corner_radius=8, fg_color="#1e272e")
            card.pack(fill="x", padx=5, pady=4)

            # آیکون و وضعیت دیسک
            status_color = "#2ed573" if disk["attached"] else "#ff4757"
            status_text = f"آنلاین ({disk['letter']})" if disk["attached"] else "آفلاین / غیرمتصل"

            # سمت چپ: دکمه‌های سریع
            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(side="left", padx=10, pady=8)

            if disk["attached"]:
                btn_action = ctk.CTkButton(btn_box, text="🔌 آن‌مانت", width=80, height=28, fg_color="#e74c3c", hover_color="#c0392b",
                                           command=lambda p=disk["path"]: self.unmount_specific_vhd(p))
                btn_action.pack(side="left", padx=3)
            else:
                btn_action = ctk.CTkButton(btn_box, text="🔗 اتصال", width=80, height=28, fg_color="#2ecc71", hover_color="#27ae60",
                                           command=lambda p=disk["path"]: self.mount_specific_vhd(p))
                btn_action.pack(side="left", padx=3)

            # سمت راست: اطلاعات دیسک
            info_box = ctk.CTkFrame(card, fg_color="transparent")
            info_box.pack(side="right", fill="x", expand=True, padx=10, pady=5)

            lbl_name = ctk.CTkLabel(info_box, text=f"💽 دیسک روح: {disk['name']}", font=("Segoe UI", 13, "bold"), anchor="e")
            lbl_name.pack(fill="x")

            lbl_sub = ctk.CTkLabel(info_box, text=f"وضعیت: {status_text} | فایل: {disk['filename']}", font=("Segoe UI", 10), text_color=status_color, anchor="e")
            lbl_sub.pack(fill="x")

            # فعال‌سازی منوی راست‌کلیک روی کل کارت
            card.bind("<Button-3>", lambda event, d=disk: self.show_context_menu(event, d))
            lbl_name.bind("<Button-3>", lambda event, d=disk: self.show_context_menu(event, d))
            lbl_sub.bind("<Button-3>", lambda event, d=disk: self.show_context_menu(event, d))
            info_box.bind("<Button-3>", lambda event, d=disk: self.show_context_menu(event, d))

    def show_context_menu(self, event, disk_data):
        self.selected_vhd_context = disk_data
        self.context_menu.delete(0, "end")

        self.context_menu.add_command(label=f"💽 مدیریت {disk_data['name']}", state="disabled")
        self.context_menu.add_separator()

        if disk_data["attached"]:
            self.context_menu.add_command(label="📂 باز کردن در اکسپلورر (Open)", command=lambda: self.open_in_explorer(disk_data["letter"]))
            self.context_menu.add_command(label="🔤 تغییر حرف درایو (Change Letter)", command=lambda: self.prompt_change_letter(disk_data))
            self.context_menu.add_command(label="🔄 همگام‌سازی فایل‌ها (Sync)", command=lambda: self.sync_specific_vhd(disk_data))
            self.context_menu.add_command(label="🔌 قطع اتصال (Unmount / Eject)", command=lambda: self.unmount_specific_vhd(disk_data["path"]))
        else:
            self.context_menu.add_command(label="🔗 اتصال به ویندوز (Mount)", command=lambda: self.mount_specific_vhd(disk_data["path"]))

        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ حذف کامل هارد مجازی (Delete)", command=lambda: self.delete_specific_vhd(disk_data))

        self.context_menu.tk_popup(event.x_root, event.y_root)

    def open_in_explorer(self, letter):
        if letter and letter != "قطع اتصال":
            os.startfile(f"{letter}\\")

    def prompt_change_letter(self, disk_data):
        dialog = ctk.CTkInputDialog(text=f"حرف جدید را وارد کنید (مثلا H یا X):", title=f"تغییر حرف درایو {disk_data['name']}")
        new_letter = dialog.get_input()
        if new_letter:
            new_letter = new_letter.strip().replace(":", "").upper()
            if len(new_letter) == 1 and new_letter in string.ascii_uppercase:
                old_letter = disk_data["letter"].replace(":", "")
                ps_cmd = f"Get-Partition -DriveLetter {old_letter} | Set-Partition -NewDriveLetter {new_letter}"
                self.run_cmd(f'powershell -Command "{ps_cmd}"')
                refresh_explorer_silently()
                self.log(f"Drive letter changed to {new_letter}:")
                self.load_virtual_disks_ui()
            else:
                messagebox.showerror("خطا", "لطفاً یک حرف معتبر انگلیسی وارد کنید.")

    def mount_specific_vhd(self, vhd_path):
        self.run_cmd(f'powershell -Command "Mount-DiskImage -ImagePath \'{vhd_path}\' -ErrorAction SilentlyContinue"')
        refresh_explorer_silently()
        self.log(f"Mounted: {os.path.basename(vhd_path)}")
        self.load_virtual_disks_ui()

    def unmount_specific_vhd(self, vhd_path):
        self.run_cmd(f'powershell -Command "Dismount-DiskImage -ImagePath \'{vhd_path}\' -ErrorAction SilentlyContinue"')
        refresh_explorer_silently()
        self.log(f"Unmounted: {os.path.basename(vhd_path)}")
        self.load_virtual_disks_ui()

    def delete_specific_vhd(self, disk_data):
        if messagebox.askyesno("تأیید حذف", f"آیا مطمئن هستید که می‌خواهید هارد مجازی '{disk_data['name']}' را کاملاً حذف کنید؟"):
            self.unmount_specific_vhd(disk_data["path"])
            try:
                os.remove(disk_data["path"])
                self.log(f"Deleted VHDX: {disk_data['filename']}")
                self.load_virtual_disks_ui()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف فایل: {e}")

    def sync_specific_vhd(self, disk_data):
        if not disk_data["attached"]:
            messagebox.showwarning("هشدار", "ابتدا درایو را متصل (Mount) کنید.")
            return
        src_raw = self.cmb_source.get().split()[0]
        src = src_raw.replace(":", "").replace("\\", "") + ":"
        target = disk_data["letter"]

        self.log(f"Syncing changes from {src} to {target}...")
        self.run_cmd(f'robocopy "{src}" "{target}" /E /CREATE /PURGE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{target}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')
        refresh_explorer_silently()
        self.log(f"SUCCESS: Drive {target} updated smoothly!")

    def start_create(self):
        threading.Thread(target=self._task_create, daemon=True).start()

    def _task_create(self):
        src_raw = self.cmb_source.get().split()[0]
        src = src_raw.replace(":", "").replace("\\", "") + ":"
        target_letter = self.cmb_target.get().replace(":", "").replace("\\", "")
        target = f"{target_letter}:"
        
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
        self.load_virtual_disks_ui()
        self.log(f"SUCCESS: Drive {drive_name} ({target}) is completely ready!")

    def start_unmount_all(self):
        save_folder = self.get_save_dir()
        self.log("Unmounting ALL virtual drives...")
        ps_cmd = f'Get-ChildItem -Path \'{save_folder}\\*.vhdx\' -ErrorAction SilentlyContinue | ForEach-Object {{ Dismount-DiskImage -ImagePath $_.FullName -ErrorAction SilentlyContinue }}'
        self.run_cmd(f'powershell -Command "{ps_cmd}"')
        refresh_explorer_silently()
        self.load_virtual_disks_ui()
        self.log("SUCCESS: All virtual drives unmounted!")

    def start_mount_all(self):
        save_folder = self.get_save_dir()
        self.log("Mounting ALL virtual drives...")
        ps_cmd = f'Get-ChildItem -Path \'{save_folder}\\*.vhdx\' -ErrorAction SilentlyContinue | ForEach-Object {{ Mount-DiskImage -ImagePath $_.FullName -ErrorAction SilentlyContinue }}'
        self.run_cmd(f'powershell -Command "{ps_cmd}"')
        refresh_explorer_silently()
        self.load_virtual_disks_ui()
        self.log("SUCCESS: All virtual drives mounted!")

if __name__ == "__main__":
    app = GhostDriveApp()
    app.mainloop()
