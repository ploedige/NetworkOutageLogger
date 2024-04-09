import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import time
import threading

class NetworkOutageLogger:
    def __init__(self, master):
        self.master = master
        master.title("Network Outage Logger")

        self.target = tk.StringVar()
        self.logfile = tk.StringVar()
        self.logging_thread = None
        self.stop_logging_flag = threading.Event()

        self.init_gui()

    def init_gui(self):
        self.target_label = tk.Label(self.master, text="Connection Destination:")
        self.target_label.grid(row=0, column=0, sticky="w")

        self.target_entry = tk.Entry(self.master, textvariable=self.target)
        self.target_entry.grid(row=0, column=1)

        self.log_file_label = tk.Label(self.master, text="Logging File:")
        self.log_file_label.grid(row=1, column=0, sticky="w")

        self.log_file_entry = tk.Entry(self.master, textvariable=self.logfile)
        self.log_file_entry.grid(row=1, column=1)
        self.log_file_entry.config(state="readonly")

        self.browse_button = tk.Button(self.master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=1, column=2)

        self.start_button = tk.Button(self.master, text="Start Logging", command=self.start_logging)
        self.start_button.grid(row=2, column=0, columnspan=2)

        self.stop_button = tk.Button(self.master, text="Stop Logging", command=self.stop_logging)
        self.stop_button.grid(row=2, column=2)

        self.connection_status_label = tk.Label(self.master, text="Connection Status: ")
        self.connection_status_label.grid(row=3, column=0, sticky="w")

        self.connection_status = tk.Label(self.master, text="Unknown")
        self.connection_status.grid(row=3, column=1, sticky="w")

        self.logging_status_label = tk.Label(self.master, text="Logging Status: ")
        self.logging_status_label.grid(row=4, column=0, sticky="w")

        self.logging_status = tk.Label(self.master, text="Not Logging")
        self.logging_status.grid(row=4, column=1, sticky="w")

    def browse_file(self):
        self.logfile.set(filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]))

    def ping_host(self):
        return subprocess.call(["ping", "-n", "1", self.target.get()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    def log_outage(self, start_time, end_time):
        with open(self.logfile.get(), "a") as f:
            f.write(f"Connection lost from {start_time} to {end_time}\n")

    def logging_process(self):
        while not self.stop_logging_flag.is_set():
            if self.ping_host():
                self.connection_status.config(text="Connected")
                time.sleep(5)
            else:
                start_time = time.strftime('%Y-%m-%d %H:%M:%S')
                self.connection_status.config(text="Disconnected")
                while not self.ping_host():
                    if self.stop_logging_flag.is_set():
                        return
                    time.sleep(1)
                end_time = time.strftime('%Y-%m-%d %H:%M:%S')
                self.log_outage(start_time, end_time)

    def start_logging(self):
        target = self.target.get()
        logfile = self.logfile.get()
        if not target or not logfile:
            messagebox.showerror("Error", "Please provide both connection destination and logging file!")
            return

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.logging_status.config(text="Logging")
        self.stop_logging_flag.clear()
        self.logging_thread = threading.Thread(target=self.logging_process)
        self.logging_thread.start()

    def stop_logging(self):
        if self.logging_thread:
            self.stop_logging_flag.set()
            self.logging_thread.join()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.logging_status.config(text="Not Logging")
        self.connection_status.config(text="Unknown")

def main():
    root = tk.Tk()
    app = NetworkOutageLogger(root)
    root.mainloop()

if __name__ == "__main__":
    main()
