import socket
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import os
import subprocess
import re

# پورت‌های مهم و پرکاربرد
DEFAULT_PORTS = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 123, 135, 139,
    143, 161, 162, 179, 389, 443, 445, 465, 514, 515, 587, 636, 993,
    995, 1080, 1194, 1433, 1521, 1723, 2049, 2082, 2083, 2095, 2096,
    3306, 3389, 5060, 5061, 5432, 5900, 6000, 8080, 8443, 8888, 10000
]

# متغیر برای کنترل متوقف کردن اسکن
stop_scan = False

def detect_os(target_ip):
    """OS Detection based on TTL (Time To Live) analysis"""
    try:
        # دستور ping برای بدست آوردن TTL
        if os.name == "nt":  # Windows
            ping_cmd = ["ping", "-n", "1", target_ip]
            pattern = r"TTL=(\d+)"
        else:  # Linux/Mac
            ping_cmd = ["ping", "-c", "1", target_ip]
            pattern = r"ttl=(\d+)"
        
        result = subprocess.run(
            ping_cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        match = re.search(pattern, result.stdout, re.IGNORECASE)
        
        if match:
            ttl = int(match.group(1))
            
            # تشخیص سیستم عامل بر اساس TTL
            # Windows: 128, Linux: 64, Cisco: 255
            # ranges برای در نظر گرفتن hop‌های میانی
            if ttl >= 220 or ttl == 255:
                return "OS Detection: Cisco/Network Device (TTL: 255)"
            elif ttl >= 95:
                return "OS Detection: Windows (TTL: ~128)"
            elif ttl >= 40:
                return "OS Detection: Linux/Unix (TTL: ~64)"
            else:
                return f"OS Detection: Unknown (TTL: {ttl})"
        else:
            return "OS Detection: Could not determine TTL"
            
    except Exception as e:
        return f"OS Detection: Failed - {str(e)}"

def banner_grabbing(target_ip, port):
    """Banner Grabbing - دریافت اطلاعات سرویس از پورت‌های باز"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((target_ip, port))
        
        # سعی برای دریافت banner
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        s.close()
        
        # تشخیص سرویس و OS بر اساس banner
        banner_lower = banner.lower()
        
        if not banner:
            return None
        
        # شناسایی سرویس و ورژن
        if 'ssh' in banner_lower:
            return f"SSH: {banner}"
        elif 'http' in banner_lower or 'server:' in banner_lower:
            return f"HTTP: {banner}"
        elif 'ftp' in banner_lower:
            return f"FTP: {banner}"
        elif 'smtp' in banner_lower:
            return f"SMTP: {banner}"
        elif 'pop' in banner_lower:
            return f"POP3: {banner}"
        elif 'imap' in banner_lower:
            return f"IMAP: {banner}"
        else:
            return f"Service: {banner}"
    
    except socket.timeout:
        return None
    except:
        return None

def scan_ports_gui():
    target = entry_target.get()
    # اگر حالت Default انتخاب شده، از DEFAULT_PORTS استفاده می‌کنیم
    if combo_choice.get() == "Default Ports":
        ports = DEFAULT_PORTS
    else:
        start_text = entry_start.get()
        end_text = entry_end.get()
        if start_text.strip() == "" or end_text.strip() == "":
            output.insert(tk.END, "Please enter Start and End ports\n")
            return
        start = int(start_text)
        end = int(end_text)
        ports = list(range(start, end + 1))

    progress_bar['maximum'] = len(ports)
    progress_bar['value'] = 0

    try:
        target_ip = socket.gethostbyname(target)
    except:
        output.insert(tk.END, "Invalid IP/Domain\n")
        return

    output.insert(tk.END, f"Scanning {target} ({target_ip})...\n")
    
    # اگر OS Detection فعال باشد
    if os_detect_var.get():
        output.insert(tk.END, "Detecting OS...\n")
        os_info = detect_os(target_ip)
        output.insert(tk.END, f"{os_info}\n")
    
    global stop_scan
    stop_scan = False

    for count, port in enumerate(ports, start=1):
        if stop_scan:
            output.insert(tk.END, "Scan cancelled.\n\n")
            progress_bar['value'] = 0
            return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((target_ip, port))
        if result == 0:
            output.insert(tk.END, f"Port {port} is open\n")
            
            # سعی برای دریافت banner
            banner_info = banner_grabbing(target_ip, port)
            if banner_info:
                output.insert(tk.END, f"  └─ {banner_info}\n")
        
        s.close()
        progress_bar['value'] = count
        root.update_idletasks()

    output.insert(tk.END, "Scan complete.\n\n")
    progress_bar['value'] = 0

def start_scan_thread():
    thread = threading.Thread(target=scan_ports_gui)
    thread.start()

def cancel_scan():
    global stop_scan
    stop_scan = True

def on_combo_change(event):
    # اگر Default انتخاب شد، Entryها غیر فعال شوند
    if combo_choice.get() == "Default Ports":
        entry_start.config(state="disabled")
        entry_end.config(state="disabled")
    else:
        entry_start.config(state="normal")
        entry_end.config(state="normal")

# ساخت GUI
root = tk.Tk()
root.title("Simple Port Scanner")
root.geometry("600x500")

if os.name == "nt":
    root.wm_iconbitmap("icon.ico")
else:
    root.iconphoto(False, tk.PhotoImage(file="icon.png"))

font_label = ("Helvetica", 12)
font_entry = ("Helvetica", 12)
font_button = ("Helvetica", 12)
font_output = ("Courier", 11)

tk.Label(root, text="Target IP/Domain:", font=font_label).grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_target = tk.Entry(root, font=font_entry, width=30)
entry_target.grid(row=0, column=1, padx=10, pady=5)

# ComboBox برای انتخاب حالت
tk.Label(root, text="Scan Mode:", font=font_label).grid(row=1, column=0, padx=10, pady=5, sticky="e")
combo_choice = ttk.Combobox(root, values=["Default Ports", "Custom Range"], state="readonly", font=font_entry)
combo_choice.current(0)
combo_choice.grid(row=1, column=1, padx=10, pady=5, sticky="w")
combo_choice.bind("<<ComboboxSelected>>", on_combo_change)

tk.Label(root, text="Start Port:", font=font_label).grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_start = tk.Entry(root, font=font_entry, width=10)
entry_start.grid(row=2, column=1, padx=10, pady=5, sticky="w")
entry_start.insert(0, str(DEFAULT_PORTS[0]))
entry_start.config(state="disabled")

tk.Label(root, text="End Port:", font=font_label).grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_end = tk.Entry(root, font=font_entry, width=10)
entry_end.grid(row=3, column=1, padx=10, pady=5, sticky="w")
entry_end.insert(0, str(DEFAULT_PORTS[-1]))
entry_end.config(state="disabled")

# Checkbox برای OS Detection
os_detect_var = tk.BooleanVar(value=False)
os_detect_check = tk.Checkbutton(root, text="Enable OS Detection", variable=os_detect_var, font=font_label)
os_detect_check.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

button_frame = tk.Frame(root)
button_frame.grid(row=5, column=0, columnspan=2, pady=10)

scan_btn = tk.Button(button_frame, text="Scan", font=font_button, command=start_scan_thread, width=10)
scan_btn.pack(side="left", padx=5)

cancel_btn = tk.Button(button_frame, text="Cancel", font=font_button, command=cancel_scan, width=10)
cancel_btn.pack(side="left", padx=5)

root.bind("<Return>", lambda e: start_scan_thread())

progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

output = scrolledtext.ScrolledText(root, width=70, height=15, font=font_output)
output.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()