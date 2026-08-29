import os
import subprocess
import threading
import random
import string
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MAGIC_NAMES = [
    "Rubeus Hagrid (هارد بزرگ و پرحجم)",
    "Golden Snitch (SSD پرسرعت و تیز)",
    "Dobby The Elf (هارد کوچیک و زحمت‌کش)",
    "Gringotts Vault (خزانه فایل‌های باارزش)",
    "Hermione's Bag (کیف بی‌انتهای هرماینی)",
    "Firebolt (جاروی آذرخش فوق‌سریع)",
    "Chamber of Secrets (تالار اسرار و فایل‌های مخفی)"
]

class GhostDriveApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚡ Wizard Ghost Drive - جادوگر هاردهای روح")
        self.geometry("620x660")
        self.resizable(False, False)

        self.lbl_title = ctk.CTkLabel(self, text="🪄 ساخت و مدیریت هاردهای مجازی روح", font=("Segoe UI", 20, "bold"))
        self.lbl_title.pack(pady=15)

        self.frame_source = ctk.CTkFrame(self)
        self.frame_source.pack(fill="x", padx=25, pady=8)
        self.lbl_src = ctk.CTkLabel(self.frame_source, text=":هارد واقعی (مبدأ)", font=("Segoe UI", 13))
        self.lbl_src.pack(side="right", padx=10, pady=10)
        self.cmb_source = ctk.CTkComboBox(self.frame_source, values=self.get_available_drives(), width=120)
        self.cmb_source.pack(side="right", padx=10)
        self.btn_refresh = ctk.CTkButton(self.frame_source, text="🔄 رفرش درایوها", width=100, command=self.refresh_drives)
        self.btn_refresh.pack(side="left", padx=10)

        self.frame_name = ctk.CTkFrame(self)
        self.frame_name.pack(fill="x", padx=25, pady=8)
        self.lbl_name = ctk.CTkLabel(self.frame_name, text=":نام درایو", font=("Segoe UI", 13))
        self.lbl_name.pack(side="right", padx=10, pady=10)
        self.txt_name = ctk.CTkEntry(self.frame_name, width=230, placeholder_text="Rubeus Hagrid")
        self.txt_name.pack(side="right", padx=10)
        self.btn_suggest = ctk.CTkButton(self.frame_name, text="🎲 اسم جادویی", width=110, fg_color="#6C5CE7", hover_color="#5844D8", command=self.suggest_name)
        self.btn_suggest.pack(side="left", padx=10)

        self.frame_target = ctk.CTkFrame(self)
        self.frame_target.pack(fill="x", padx=25, pady=8)
        self.lbl_target = ctk.CTkLabel(self.frame_target, text=":حرف درایو مجازی", font=("Segoe UI", 13))
        self.lbl_target.pack(side="right", padx=10, pady=10)
        self.cmb_target = ctk.CTkComboBox(self.frame_target, values=["H:", "S:", "B:", "X:", "Y:", "Z:"], width=100)
        self.cmb_target.set("S:")
        self.cmb_target.pack(side="right", padx=10)

        self.btn_create = ctk.CTkButton(self, text="✨ ساخت هارد روح و شبیه‌سازی دقیق حجم", font=("Segoe UI", 14, "bold"), height=42, fg_color="#00b894", hover_color="#00a383", command=self.start_create)
        self.btn_create.pack(fill="x", padx=25, pady=8)

        self.btn_sync = ctk.CTkButton(self, text="🔄 همگام‌سازی و آپدیت تغییرات", font=("Segoe UI", 14, "bold"), height=42, fg_color="#0984e3", hover_color="#0773c5", command=self.start_sync)
        self.btn_sync.pack(fill="x", padx=25, pady=8)

        self.log_box = ctk.CTkTextbox(self, height=180, font=("Consolas", 11))
        self.log_box.pack(fill="both", padx=25, pady=15)
        self.log("برنامه آماده است...")

    def log(self, text):
        self.log_box.insert("end", f">> {text}\n")
        self.log_box.see("end")

    def get_available_drives(self):
        drives = []
        for letter in string.ascii_uppercase:
            if os.path.exists(f"{letter}:\\") and letter != "C":
                drives.append(f"{letter}:")
        return drives if drives else ["E:"]

    def refresh_drives(self):
        self.cmb_source.configure(values=self.get_available_drives())
        self.log("لیست درایوها بروز شد.")

    def suggest_name(self):
        chosen = random.choice(MAGIC_NAMES)
        name_only = chosen.split(" (")[0]
        self.txt_name.delete(0, "end")
        self.txt_name.insert(0, name_only)
        self.log(f"پیشنهاد جادویی: {chosen}")

    def run_cmd(self, cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)

    def start_create(self):
        threading.Thread(target=self._task_create, daemon=True).start()

    def _task_create(self):
        src = self.cmb_source.get().replace("\\", "") + "\\"
        drive_name = self.txt_name.get().strip() or "MagicDrive"
        target = self.cmb_target.get().replace(":", "")
        dest = f"{target}:\\"

        self.log(f"شروع ساخت دیسک مجازی برای {drive_name}...")
        os.makedirs("D:\\OfflineDrives", exist_ok=True)
        vhdx_path = f"D:\\OfflineDrives\\{drive_name.replace(' ', '_')}.vhdx"

        dp = f"""create vdisk file="{vhdx_path}" maximum=1000000 type=expandable
select vdisk file="{vhdx_path}"
attach vdisk
create partition primary
format fs=ntfs quick label="{drive_name}"
assign letter={target}
"""
        with open("dp.txt", "w") as f:
            f.write(dp)
        self.run_cmd("diskpart /s dp.txt")
        if os.path.exists("dp.txt"): os.remove("dp.txt")

        self.log("در حال قالب‌گیری صفر بایتی از فایل‌ها...")
        self.run_cmd(f'robocopy "{src}" "{dest}" /E /CREATE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{dest}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')

        self.log("فعال‌سازی آیکون‌ها...")
        ps_icons = f"Get-ChildItem -Path '{dest}' -Filter 'desktop.ini' -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {{ attrib +h +s $_.FullName; attrib +r $_.DirectoryName }}"
        subprocess.run(["powershell", "-Command", ps_icons])

        self.log("محاسبه و شبیه‌سازی دقیق حجم هارد...")
        ps_size = f"""$E = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='{src[:2]}'"; $S = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='{dest[:2]}'"; $N = $S.FreeSpace - $E.FreeSpace; if ($N -gt 0) {{ fsutil file createnew "{dest}SpaceFiller.dat" $N; attrib +h +s "{dest}SpaceFiller.dat" }}"""
        subprocess.run(["powershell", "-Command", ps_size])

        self.run_cmd("taskkill /f /im explorer.exe && start explorer.exe")
        self.log(f"🎉 درایو {drive_name} ({target}:) با حجم و آیکون دقیق ساخته شد!")

    def start_sync(self):
        threading.Thread(target=self._task_sync, daemon=True).start()

    def _task_sync(self):
        src = self.cmb_source.get().replace("\\", "") + "\\"
        target = self.cmb_target.get().replace(":", "")
        dest = f"{target}:\\"

        if not os.path.exists(dest):
            self.log(f"خطا: درایو {target}: متصل نیست!")
            return

        self.log("همگام‌سازی فایل‌ها...")
        self.run_cmd(f'robocopy "{src}" "{dest}" /E /CREATE /PURGE /XD "$RECYCLE.BIN" "System Volume Information" /R:1 /W:1 /A-:SH')
        self.run_cmd(f'robocopy "{src}" "{dest}" desktop.ini *.ico *.dll /S /LEV:3 /R:1 /W:1 /COPY:DAT')
        self.log(f"✅ درایو {target}: با موفقیت بروزرسانی شد.")

if __name__ == "__main__":
    app = GhostDriveApp()
    app.mainloop()
