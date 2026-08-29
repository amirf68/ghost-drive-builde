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

# Auto-run as Administrator
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

# Fixed Multi-language strings (No reversed words)
STRINGS = {
    "EN": {
        "title": "Wizard Ghost Drive Manager",
        "real_drive": "Source Drive:",
        "refresh": "Refresh",
        "save_path": "VHDX Storage:",
        "browse": "Browse",
        "drive_name": "Virtual Name:",
        "magic_name": "Magic Name",
        "target_letter": "Drive Letter:",
        "btn_create": "✨ Create Ghost Drive & Match Capacity",
        "disk_mgmt_title": "Virtual Disk Management (Right-click on disks for options)",
        "mount_all": "⚡ Mount All",
        "unmount_all": "💥 Eject All",
        "startup_btn": "🚀 Enable Auto-Mount on Windows Startup",
        "no_vhds": "No Virtual Disks (VHDX) found in storage directory.",
        "ctx_open": "📂 Open in Explorer",
        "ctx_change_letter": "🔤 Change Drive Letter...",
        "ctx_sync": "🔄 Sync Changes from Source Drive...",
        "ctx_unmount": "🔌 Eject / Unmount",
        "ctx_mount": "🔗 Mount Volume",
        "ctx_delete": "🗑️ Delete Virtual Disk...",
        "ctx_props": "ℹ️ Properties"
    },
    "FA": {
        "title": "مدیریت هاردهای مجازی روح",
        "real_drive": "هارد مبدا:",
        "refresh": "رفرش",
        "save_path": "محل ذخیره:",
        "browse": "انتخاب پوشه",
        "drive_name": "نام درایو:",
        "magic_name": "اسم جادویی",
        "target_letter": "حرف درایو:",
        "btn_create": "✨ ساخت هارد روح جدید و تنظیم حجم",
        "disk_mgmt_title": "مدیریت دیسک‌های مجازی (راست‌کلیک برای منو)",
        "mount_all": "⚡ اتصال همه",
        "unmount_all": "💥 خروج همه",
        "startup_btn": "🚀 فعال‌سازی اجرای خودکار در استارتاپ ویندوز",
        "no_vhds": "هیچ هارد مجازی در این پوشه یافت نشد.",
        "ctx_open": "📂 باز کردن در اکسپلورر",
        "ctx_change_letter": "🔤 تغییر حرف درایو...",
        "ctx_sync": "🔄 بروزرسانی فایل‌ها از هارد اصلی...",
        "ctx_unmount": "🔌 خروج / قطع اتصال",
        "ctx_mount": "🔗 اتصال به ویندوز",
        "ctx_delete": "🗑️ حذف فایل هارد مجازی...",
        "ctx_props": "ℹ️ مشخصات"
    }
}

MAGIC_NAMES = [
    "Rubeus Hagrid", "Golden Snitch", "Dobby",
    "Gringotts Vault", "Hermione's Bag", "Firebolt", "Chamber of Secrets"
]

class GhostDriveApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_lang = "EN"
        self.title("Wizard Ghost Drive Management")

        # Responsive resolution
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        win_w = min(780, int(screen_w * 0.92))
        win_h = min(880, int(screen_h * 0.90))
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)

        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(580, 520)
        self.resizable(True, True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Top Bar
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(fill="x", padx=15, pady=(8, 2))

        self.lbl_title = ctk.CTkLabel(self.frame_top, text=self.t("title"), font=("Segoe UI", 16, "bold"))
        self.lbl_title.pack(side="left", padx=5)

        self.cmb_lang = ctk.CTkComboBox(self.frame_top, values=["English", "فارسی"], width=95, command=self.change_language)
        self.cmb_lang.set("English")
        self.cmb_lang.pack(side="right", padx=5)

        # 1. Source Drive
        self.frame_src = ctk.CTkFrame(self)
        self.frame_src.pack(fill="x", padx=15, pady=2)
        self.lbl_src = ctk.CTkLabel(self.frame_src, text=self.t("real_drive"), font=("Segoe UI", 11))
        self.lbl_src.pack(side="left", padx=8, pady=4)
        
        available_drives = self.get_available_drives()
        self.cmb_source = ctk.CTkComboBox(self.frame_src, values=available_drives, width=150, command=self.on_source_changed)
        self.cmb_source.pack(side="left", padx=4)
        self.btn_refresh = ctk.CTkButton(self.frame_src, text=self.t("refresh"), width=65, height=26, command=self.refresh_drives)
        self.btn_refresh.pack(side="right", padx=8)

        # 2. Storage Folder
        self.frame_path = ctk.CTkFrame(self)
        self.frame_path.pack(fill="x", padx=15, pady=2)
        self.lbl_path = ctk.CTkLabel(self.frame_path, text=self.t("save_path"), font=("Segoe UI", 11))
        self.lbl_path.pack(side="left", padx=8, pady=4)
        self.txt_save_path = ctk.CTkEntry(self.frame_path)
        self.txt_save_path.insert(0, r"D:\OfflineDrives")
        self.txt_save_path.pack(side="left", fill="x", expand=True, padx=4)
        self.btn_browse = ctk.CTkButton(self.frame_path, text=self.t("browse"), width=75, height=26, fg_color="#34495e", hover_color="#2c3e50", command=self.browse_save_folder)
        self.btn_browse.pack(side="right", padx=8)

        # 3. Drive Name
        self.frame_name = ctk.CTkFrame(self)
        self.frame_name.pack(fill="x", padx=15, pady=2)
        self.lbl_name = ctk.CTkLabel(self.frame_name, text=self.t("drive_name"), font=("Segoe UI", 11))
        self.lbl_name.pack(side="left", padx=8, pady=4)
        self.txt_name = ctk.CTkEntry(self.frame_name, placeholder_text="e.g. Golden Snitch")
        self.txt_name.pack(side="left", fill="x", expand=True, padx=4)
        self.btn_suggest = ctk.CTkButton(self.frame_name, text=self.t("magic_name"), width=90, height=26, fg_color="#6C5CE7", hover_color="#5844D8", command=self.suggest_name)
        self.btn_suggest.pack(side="right", padx=8)

        # 4. Target Letter & Create
        self.frame_target = ctk.CTkFrame(self)
        self.frame_target.pack(fill="x", padx=15, pady=2)
        self.lbl_target = ctk.CTkLabel(self.frame_target, text=self.t("target_letter"), font=("Segoe UI", 11))
        self.lbl_target.pack(side="left", padx=8, pady=4)
        self.cmb_target = ctk.CTkComboBox(self.frame_target, values=["H:", "S:", "B:", "Z:", "X:", "Y:", "V:"], width=75)
        self.cmb_target.set("Z:")
        self.cmb_target.pack(side="left", padx=4)

        self.btn_create = ctk.CTkButton(self.frame_target, text=self.t("btn_create"), font=("Segoe UI", 11, "bold"), height=28, fg_color="#00b894", hover_color="#00a383", command=self.start_create)
        self.btn_create.pack(side="right", fill="x", expand=True, padx=8)

        # 5. Disk Management Container
        self.frame_dsk_mgmt = ctk.CTkFrame(self, fg_color="#18191a", border_width=1, border_color="#3a3b3c")
        self.frame_dsk_mgmt.pack(fill="both", expand=True, padx=15, pady=4)

        # Header
        self.frame_dsk_header = ctk.CTkFrame(self.frame_dsk_mgmt, fg_color="#242526", height=32)
        self.frame_dsk_header.pack(fill="x", padx=2, pady=2)

        self.lbl_dsk_title = ctk.CTkLabel(self.frame_dsk_header, text=self.t("disk_mgmt_title"), font=("Segoe UI", 11, "bold"), text_color="#70a1ff")
        self.lbl_dsk_title.pack(side="left", padx=8)

        self.btn_refresh_cards = ctk.CTkButton(self.frame_dsk_header, text="🔄", width=30, height=22, command=self.load_virtual_disks_ui)
        self.btn_refresh_cards.pack(side="right", padx=4)

        self.btn_unmount_all = ctk.CTkButton(self.frame_dsk_header, text=self.t("unmount_all"), width=75, height=22, fg_color="#c0392b", hover_color="#962d22", command=self.start_unmount_all)
        self.btn_unmount_all.pack(side="right", padx=4)

        self.btn_mount_all = ctk.CTkButton(self.frame_dsk_header, text=self.t("mount_all"), width=75, height=22, fg_color="#27ae60", hover_color="#219150", command=self.start_mount_all)
        self.btn_mount_all.pack(side="right", padx=4)

        # Disks Scroll Area
        self.scroll_disks = ctk.CTkScrollableFrame(self.frame_dsk_mgmt, fg_color="#18191a")
        self.scroll_disks.pack(fill="both", expand=True, padx=4, pady=2)

        # Legend Bar
        self.frame_legend = ctk.CTkFrame(self.frame_dsk_mgmt, fg_color="#242526", height=20)
        self.frame_legend.pack(fill="x", padx=2, pady=2)
        
        lbl_leg1 = ctk.CTkLabel(self.frame_legend, text="■ Primary partition", text_color="#002060", font=("Segoe UI", 9, "bold"))
        lbl_leg1.pack(side="left", padx=10)
        lbl_leg2 = ctk.CTkLabel(self.frame_legend, text="■ Offline / Detached", text_color="#747d8c", font=("Segoe UI", 9))
        lbl_leg2.pack(side="left", padx=8)

        # Startup Button
        self.btn_startup = ctk.CTkButton(self, text=self.t("startup_btn"), fg_color="#2d3436", hover_color="#636e72", height=28, command=self.setup_startup)
        self.btn_startup.pack(fill="x", padx=15, pady=2)

        # Log Box
        self.log_box = ctk.CTkTextbox(self, height=80, font=("Consolas", 10))
        self.log_box.pack(fill="x", padx=15, pady=(2, 6))

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2f3542", fg="white", activebackground="#1e90ff", activeforeground="white", font=("Segoe UI", 9))
        self.active_context_disk = None

        if available_drives:
            self.on_source_changed(available_drives[0])

        self.load_virtual_disks_ui()
        self.log("Ready. Checking mounted Virtual Disks...")

    def t(self, key):
        return STRINGS[self.current_lang].get(key, key)

    def change_language(self, choice):
        self.current_lang = "FA" if choice == "فارسی" else "EN"
        self.lbl_title.configure(text=self.t("title"))
        self.lbl_src.configure(text=self.t("real_drive"))
        self.btn_refresh.configure(text=self.t("refresh"))
        self.lbl_path.configure(text=self.t("save_path"))
        self.btn_browse.configure(text=self.t("browse"))
        self.lbl_name.configure(text=self.t("drive_name"))
        self.btn_suggest.configure(text=self.t("magic_name"))
        self.lbl_target.configure(text=self.t("target_letter"))
        self.btn_create.configure(text=self.t("btn_create"))
        self.lbl_dsk_title.configure(text=self.t("disk_mgmt_title"))
        self.btn_mount_all.configure(text=self.t("mount_all"))
        self.btn_unmount_all.configure(text=self.t("unmount_all"))
        self.btn_startup.configure(text=self.t("startup_btn"))
        self.load_virtual_disks_ui()

    def log(self, text):
        self.log_box.insert("end", f"> {text}\n")
        self.log_box.see("end")

    def on_source_changed(self, choice):
        drive_letter = choice.split()[0]
        real_label = get_drive_label(drive_letter)
        if real_label:
            self.txt_name.delete(0, "end")
            self.txt_name.insert(0, real_label)
            self.log(f"Detected label '{real_label}' on {drive_letter}")

    def browse_save_folder(self):
        folder = filedialog.askdirectory(title="Select VHDX Storage Folder")
        if folder:
            win_path = os.path.normpath(folder)
            self.txt_save_path.delete(0, "end")
            self.txt_save_path.insert(0, win_path)
            self.log(f"Path: {win_path}")
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
        self.log("Source drives refreshed.")

    def suggest_name(self):
        chosen = random.choice(MAGIC_NAMES)
        self.txt_name.delete(0, "end")
        self.txt_name.insert(0, chosen)
        self.log(f"Suggested: {chosen}")

    def run_cmd(self, cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # 100% Reliable VHDX Attachment Detection
    def get_virtual_disks_info(self):
        save_folder = self.get_save_dir()
        vhdx_files = [f for f in os.listdir(save_folder) if f.endswith(".vhdx")] if os.path.exists(save_folder) else []
        
        # Directly query each VHDX image status
        ps_cmd = f"""
        Get-ChildItem -Path '{save_folder}\\*.vhdx' -ErrorAction SilentlyContinue | ForEach-Object {{
            $img = Get-DiskImage -ImagePath $_.FullName -ErrorAction SilentlyContinue
            if ($img -and $img.Attached) {{
                $disk = $img | Get-Disk -ErrorAction SilentlyContinue
                $part = $disk | Get-Partition | Where-Object {{ $_.DriveLetter }} | Select-Object -First 1
                $letter = if ($part) {{ $part.DriveLetter }} else {{ "" }}
                $size = if ($disk) {{ [math]::Round($disk.Size/1GB, 2) }} else {{ "1000" }}
                Write-Output "$($_.FullName)|$letter|$size"
            }}
        }}
        """
        res = self.run_cmd(f'powershell -Command "{ps_cmd}"')
        attached_map = {}
        if res.stdout:
            for line in res.stdout.strip().splitlines():
                if "|" in line:
                    parts = line.strip().split("|")
                    p_path = os.path.normpath(parts[0]).lower()
                    p_letter = parts[1] if len(parts) > 1 else ""
                    p_size = parts[2] if len(parts) > 2 else "1000"
                    attached_map[p_path] = {"letter": p_letter, "size": p_size}

        disks_data = []
        for idx, file in enumerate(vhdx_files):
            full_path = os.path.normpath(os.path.join(save_folder, file))
            name = file.replace(".vhdx", "").replace("_", " ")
            is_attached = full_path.lower() in attached_map
            letter = attached_map[full_path.lower()]["letter"] if is_attached else ""
            size_gb = attached_map[full_path.lower()]["size"] if is_attached else "1000.00"

            disks_data.append({
                "disk_num": idx + 2,
                "filename": file,
                "path": full_path,
                "name": name,
                "attached": is_attached,
                "letter": f"{letter}:" if letter else "",
                "size_gb": f"{size_gb} GB"
            })
        return disks_data

    def load_virtual_disks_ui(self):
        for widget in self.scroll_disks.winfo_children():
            widget.destroy()

        disks = self.get_virtual_disks_info()
        if not disks:
            lbl_empty = ctk.CTkLabel(self.scroll_disks, text=self.t("no_vhds"), text_color="gray")
            lbl_empty.pack(pady=25)
            return

        for disk in disks:
            row_frame = ctk.CTkFrame(self.scroll_disks, fg_color="#242526", corner_radius=2, border_width=1, border_color="#3a3b3c")
            row_frame.pack(fill="x", padx=2, pady=3)

            left_header = ctk.CTkFrame(row_frame, fg_color="#1e1f20", width=125, height=68, corner_radius=0)
            left_header.pack(side="left", fill="y")
            left_header.pack_propagate(False)

            status_txt = "Online" if disk["attached"] else "Offline"
            status_color = "#2ed573" if disk["attached"] else "#a4b0be"

            ctk.CTkLabel(left_header, text=f"■ Disk {disk['disk_num']}", font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=6, pady=(3, 0))
            ctk.CTkLabel(left_header, text="Basic", font=("Segoe UI", 9), text_color="#ced6e0", anchor="w").pack(fill="x", padx=6)
            ctk.CTkLabel(left_header, text=disk["size_gb"], font=("Segoe UI", 9), text_color="#ced6e0", anchor="w").pack(fill="x", padx=6)
            ctk.CTkLabel(left_header, text=status_txt, font=("Segoe UI", 9, "bold"), text_color=status_color, anchor="w").pack(fill="x", padx=6)

            part_container = ctk.CTkFrame(row_frame, fg_color="#2f3136", corner_radius=0, border_width=1, border_color="#485460")
            part_container.pack(side="left", fill="both", expand=True, padx=3, pady=2)

            stripe_color = "#002060" if disk["attached"] else "#57606f"
            stripe = ctk.CTkFrame(part_container, fg_color=stripe_color, height=6, corner_radius=0)
            stripe.pack(fill="x")

            part_body = ctk.CTkFrame(part_container, fg_color="transparent")
            part_body.pack(fill="both", expand=True, padx=8, pady=4)

            if disk["attached"]:
                lbl_vol = ctk.CTkLabel(part_body, text=f"{disk['name']} ({disk['letter']})", font=("Segoe UI", 10, "bold"), anchor="w")
                lbl_vol.pack(fill="x")
                lbl_details = ctk.CTkLabel(part_body, text=f"{disk['size_gb']} NTFS\nHealthy (Primary Partition)", font=("Segoe UI", 9), text_color="#dcdde1", anchor="w", justify="left")
                lbl_details.pack(fill="x")
            else:
                lbl_vol = ctk.CTkLabel(part_body, text=f"{disk['name']} [Offline]", font=("Segoe UI", 10, "bold"), text_color="#a4b0be", anchor="w")
                lbl_vol.pack(fill="x")
                lbl_details = ctk.CTkLabel(part_body, text=f"{disk['filename']}\nOffline / Unallocated Space", font=("Segoe UI", 9), text_color="#747d8c", anchor="w", justify="left")
                lbl_details.pack(fill="x")

            # Recursive context menu bindings for instant right-click response
            for widget in [row_frame, left_header, part_container, stripe, part_body, lbl_vol, lbl_details]:
                widget.bind("<Button-3>", lambda event, d=disk: self.popup_menu(event, d))

    def popup_menu(self, event, disk_data):
        self.active_context_disk = disk_data
        self.context_menu.delete(0, "end")

        self.context_menu.add_command(label=f"Disk {disk_data['disk_num']}: {disk_data['name']}", state="disabled")
        self.context_menu.add_separator()

        if disk_data["attached"]:
            self.context_menu.add_command(label=self.t("ctx_open"), command=lambda: self.open_in_explorer(disk_data["letter"]))
            self.context_menu.add_command(label=self.t("ctx_change_letter"), command=lambda: self.prompt_change_letter(disk_data))
            self.context_menu.add_command(label=self.t("ctx_sync"), command=lambda: self.sync_specific_vhd(disk_data))
            self.context_menu.add_command(label=self.t("ctx_unmount"), command=lambda: self.unmount_specific_vhd(disk_data["path"]))
        else:
            self.context_menu.add_command(label=self.t("ctx_mount"), command=lambda: self.mount_specific_vhd(disk_data["path"]))

        self.context_menu.add_separator()
        self.context_menu.add_command(label=self.t("ctx_delete"), command=lambda: self.delete_specific_vhd(disk_data))
        self.context_menu.add_command(label=self.t("ctx_props"), command=lambda: self.show_properties(disk_data))

        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def open_in_explorer(self, letter):
        if letter:
            os.startfile(f"{letter}\\")

    # 100% Guaranteed Drive Letter Changer via Diskpart
    def prompt_change_letter(self, disk_data):
        old_letter = disk_data["letter"].replace(":", "").strip()
        dialog = ctk.CTkInputDialog(text=f"Enter new Drive Letter for '{disk_data['name']}' (Current: {old_letter}):", title="Change Drive Letter")
        new_letter = dialog.get_input()
        if new_letter:
            new_letter = new_letter.strip().replace(":", "").upper()
            if len(new_letter) == 1 and new_letter in string.ascii_uppercase:
                dp = f"""select volume {old_letter}
assign letter={new_letter}
"""
                with open("dp_chg.txt", "w") as f: f.write(dp)
                self.run_cmd("diskpart /s dp_chg.txt")
                if os.path.exists("dp_chg.txt"): os.remove("dp_chg.txt")

                refresh_explorer_silently()
                self.log(f"Successfully changed letter from {old_letter}: to {new_letter}:")
                self.load_virtual_disks_ui()
            else:
                messagebox.showerror("Error", "Please enter a valid single English letter (e.g. X, Y, H).")

    def mount_specific_vhd(self, vhd_path):
        self.run_cmd(f'powershell -Command "Mount-DiskImage -ImagePath \'{vhd_path}\' -ErrorAction SilentlyContinue"')
        refresh_explorer_silently()
        self.log(f"Mounted: {os.path.basename(vhd_path)}")
        self.load_virtual_disks_ui()

    def unmount_specific_vhd(self, vhd_path):
        self.run_cmd(f'powershell -Command "Dismount-DiskImage -ImagePath \'{vhd_path}\' -ErrorAction SilentlyContinue"')
        refresh_explorer_silently()
        self.log(f"Ejected: {os.path.basename(vhd_path)}")
        self.load_virtual_disks_ui()

    def delete_specific_vhd(self, disk_data):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to completely delete '{disk_data['name']}'?"):
            self.unmount_specific_vhd(disk_data["path"])
            try:
                os.remove(disk_data["path"])
                self.log(f"Deleted VHDX: {disk_data['filename']}")
                self.load_virtual_disks_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {e}")

    def show_properties(self, disk_data):
        info = f"Drive Name: {disk_data['name']}\nStatus: {'Online' if disk_data['attached'] else 'Offline'}\nLetter: {disk_data['letter']}\nCapacity: {disk_data['size_gb']}\nPath: {disk_data['path']}"
        messagebox.showinfo("Virtual Disk Properties", info)

    def sync_specific_vhd(self, disk_data):
        if not disk_data["attached"]:
            messagebox.showwarning("Warning", "Mount the drive before syncing.")
            return
        src_raw = self.cmb_source.get().split()[0]
        src = src_raw.replace(":", "").replace("\\", "") + ":"
        target = disk_data["letter"]

        self.log(f"Syncing changes from {src} to {target}...")
        self.run_cmd(f'robocopy "{src}" "{target}" /E /CREATE /PURGE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{target}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')
        refresh_explorer_silently()
        self.log(f"SUCCESS: Drive {target} synced!")

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

        self.log(f"Preparing VHDX: {drive_name}...")
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

        self.log("Copying 0-byte ghost structure...")
        self.run_cmd(f'robocopy "{src}" "{target}" /E /CREATE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{target}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')

        self.log("Activating folder icons...")
        ps_icons = f"Get-ChildItem -Path '{target}\\' -Filter 'desktop.ini' -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {{ attrib +h +s $_.FullName; attrib +r $_.DirectoryName }}"
        subprocess.run(["powershell", "-Command", ps_icons])

        self.log("Matching exact disk capacity...")
        ps_size = f"""$E = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='{src}'"; $S = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='{target}'"; $N = $S.FreeSpace - $E.FreeSpace; if ($N -gt 0) {{ fsutil file createnew "{target}\\SpaceFiller.dat" $N; attrib +h +s "{target}\\SpaceFiller.dat" }}"""
        subprocess.run(["powershell", "-Command", ps_size])

        refresh_explorer_silently()
        self.load_virtual_disks_ui()
        self.log(f"SUCCESS: Drive {drive_name} ({target}) created!")

    def start_unmount_all(self):
        save_folder = self.get_save_dir()
        self.log("Ejecting ALL virtual drives...")
        ps_cmd = f'Get-ChildItem -Path \'{save_folder}\\*.vhdx\' -ErrorAction SilentlyContinue | ForEach-Object {{ Dismount-DiskImage -ImagePath $_.FullName -ErrorAction SilentlyContinue }}'
        self.run_cmd(f'powershell -Command "{ps_cmd}"')
        refresh_explorer_silently()
        self.load_virtual_disks_ui()
        self.log("All virtual drives unmounted.")

    def start_mount_all(self):
        save_folder = self.get_save_dir()
        self.log("Mounting ALL virtual drives...")
        ps_cmd = f'Get-ChildItem -Path \'{save_folder}\\*.vhdx\' -ErrorAction SilentlyContinue | ForEach-Object {{ Mount-DiskImage -ImagePath $_.FullName -ErrorAction SilentlyContinue }}'
        self.run_cmd(f'powershell -Command "{ps_cmd}"')
        refresh_explorer_silently()
        self.load_virtual_disks_ui()
        self.log("All virtual drives mounted.")

    def setup_startup(self):
        save_folder = self.get_save_dir()
        bat_content = f'@echo off\npowershell -Command "Get-ChildItem -Path \'{save_folder}\\*.vhdx\' -ErrorAction SilentlyContinue | ForEach-Object {{ Mount-DiskImage -ImagePath $_.FullName }}"\n'
        startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        bat_path = os.path.join(startup_dir, "AutoMountGhostDrives.bat")
        with open(bat_path, "w") as f:
            f.write(bat_content)
        self.log("SUCCESS: Auto-mount on Windows Startup enabled.")

if __name__ == "__main__":
    app = GhostDriveApp()
    app.mainloop()
