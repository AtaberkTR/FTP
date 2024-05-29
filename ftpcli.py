import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ftplib
import os

class FTPClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FTP Client")
        self.root.configure(bg='#2e2e2e')
        self.create_widgets()
        self.ftp = None
        self.current_path = '/'

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#2e2e2e", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#4d4d4d", foreground="#ffffff")
        style.configure("TButton", background="#4d4d4d", foreground="#ffffff")
        style.configure("TFrame", background="#2e2e2e")
        style.configure("Treeview", background="#4d4d4d", foreground="#ffffff", fieldbackground="#4d4d4d")
        style.configure("Treeview.Heading", background="#4d4d4d", foreground="#ffffff")

        # FTP Connection Frame
        frame_conn = ttk.LabelFrame(self.root, text="FTP Connection")
        frame_conn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(frame_conn, text="Host:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_host = ttk.Entry(frame_conn)
        self.entry_host.grid(row=0, column=1, padx=5, pady=5)
        self.entry_host.insert(0, "neptune.ca.freemcserver.net")

        ttk.Label(frame_conn, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_username = ttk.Entry(frame_conn)
        self.entry_username.grid(row=1, column=1, padx=5, pady=5)
        self.entry_username.insert(0, "200atarke@gmail.com.1255809")

        ttk.Label(frame_conn, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_password = ttk.Entry(frame_conn, show="*")
        self.entry_password.grid(row=2, column=1, padx=5, pady=5)
        self.entry_password.insert(0, "TTBfBNDI9HLkJ2LsmaNVAZhFhlipBX8Y")

        ttk.Button(frame_conn, text="Connect", command=self.connect).grid(row=3, column=0, columnspan=2, pady=10)

        # FTP File Operations Frame
        frame_files = ttk.LabelFrame(self.root, text="Files")
        frame_files.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.tree_files = ttk.Treeview(frame_files, columns=("size", "modified"), show="headings")
        self.tree_files.heading("size", text="Size")
        self.tree_files.heading("modified", text="Modified")
        self.tree_files.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.tree_files.bind("<Double-1>", self.open_file_or_dir)

        ttk.Button(frame_files, text="Upload", command=self.upload_file).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(frame_files, text="Download", command=self.download_file).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(frame_files, text="Delete", command=self.delete_file).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(frame_files, text="Back", command=self.go_back).grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")

        # Configure column and row weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        frame_files.columnconfigure(0, weight=1)
        frame_files.rowconfigure(0, weight=1)

    def connect(self):
        host = self.entry_host.get()
        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            self.ftp = ftplib.FTP(host)
            self.ftp.login(username, password)
            messagebox.showinfo("Success", f"Connected to {host}")
            self.list_files()
        except ftplib.all_errors as e:
            messagebox.showerror("Error", str(e))

    def list_files(self):
        for item in self.tree_files.get_children():
            self.tree_files.delete(item)

        files = self.ftp.nlst()
        for file in files:
            try:
                size = self.ftp.size(file)
                modified = self.ftp.sendcmd(f"MDTM {file}")[4:].strip()
                self.tree_files.insert("", "end", file, values=(size, modified))
            except ftplib.error_perm:
                self.tree_files.insert("", "end", file, values=("", ""))

    def open_file_or_dir(self, event):
        item = self.tree_files.selection()[0]
        try:
            self.ftp.cwd(item)
            self.current_path = self.ftp.pwd()
            self.list_files()
        except ftplib.error_perm:
            messagebox.showinfo("Info", f"{item} is a file")

    def upload_file(self):
        local_file = filedialog.askopenfilename()
        if local_file:
            filename = os.path.basename(local_file)
            with open(local_file, 'rb') as f:
                self.ftp.storbinary(f"STOR {filename}", f)
            self.list_files()
            messagebox.showinfo("Success", f"Uploaded {filename}")

    def download_file(self):
        item = self.tree_files.selection()[0]
        local_file = filedialog.asksaveasfilename(initialfile=item)
        if local_file:
            with open(local_file, 'wb') as f:
                self.ftp.retrbinary(f"RETR {item}", f.write)
            messagebox.showinfo("Success", f"Downloaded {item}")

    def delete_file(self):
        item = self.tree_files.selection()[0]
        self.ftp.delete(item)
        self.list_files()
        messagebox.showinfo("Success", f"Deleted {item}")

    def go_back(self):
        self.ftp.cwd('..')
        self.current_path = self.ftp.pwd()
        self.list_files()

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPClientApp(root)
    root.mainloop()
