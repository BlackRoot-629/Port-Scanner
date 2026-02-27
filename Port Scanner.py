import socket
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import os

# پورت‌های مهم و پرکاربرد
DEFAULT_PORTS = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 123, 135, 139,
    143, 161, 162, 179, 389, 443, 445, 465, 514, 515, 587, 636, 993,
    995, 1080, 1194, 1433, 1521, 1723, 2049, 2082, 2083, 2095, 2096,
    3306, 3389, 5060, 5061, 5432, 5900, 6000, 8080, 8443, 8888, 10000
]

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

    for count, port in enumerate(ports, start=1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((target_ip, port))
        if result == 0:
            output.insert(tk.END, f"Port {port} is open\n")
        s.close()
        progress_bar['value'] = count
        root.update_idletasks()

    output.insert(tk.END, "Scan complete.\n\n")
    progress_bar['value'] = 0

def start_scan_thread():
    thread = threading.Thread(target=scan_ports_gui)
    thread.start()

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

scan_btn = tk.Button(root, text="Scan", font=font_button, command=start_scan_thread, width=20)
scan_btn.grid(row=4, column=0, columnspan=2, pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

output = scrolledtext.ScrolledText(root, width=70, height=15, font=font_output)
output.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()