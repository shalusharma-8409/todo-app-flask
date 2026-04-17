import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import DateEntry
from datetime import datetime
import json, os

DATA_FILE = "tasks.json"

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do App 🚀")
        self.root.geometry("900x700")
        self.root.configure(bg="#121212")

        self.tasks = []
        self.filtered_tasks = []
        self.daily_note = ""

        self.load_data()

        # ===== QUOTE BOX =====
        box = tk.Frame(root, bg="#1f1f1f")
        box.pack(fill="x", padx=10, pady=10)

        tk.Label(box, text=datetime.now().strftime("%A, %d %B %Y"),
                 fg="#aaa", bg="#1f1f1f").pack(anchor="e", padx=10)

        self.note_label = tk.Label(
            box,
            text=self.daily_note or "No quote set ✨",
            fg="white",
            bg="#1f1f1f",
            font=("Arial", 12, "bold")
        )
        self.note_label.pack(pady=5)

        tk.Button(
            box,
            text="✏️ Edit Quote",
            command=self.set_note,
            bg="#333",
            fg="white"
        ).pack(pady=5)

        # ===== PROGRESS =====
        tk.Label(root, text="Daily Progress",
                 fg="white", bg="#121212").pack()

        self.progress = ttk.Progressbar(root, length=500)
        self.progress.pack(pady=5)

        self.progress_text = tk.Label(root, text="0%",
                                     fg="#aaa", bg="#121212")
        self.progress_text.pack()

        # ===== INPUT =====
        frame = tk.Frame(root, bg="#121212")
        frame.pack(pady=10)

        self.task_entry = tk.Entry(frame, width=30, bg="#2a2a2a", fg="white")
        self.task_entry.grid(row=0, column=0, padx=5)

        self.date_entry = DateEntry(frame, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1, padx=5)

        self.priority = ttk.Combobox(
            frame,
            values=["High", "Medium", "Low"],
            width=10
        )
        self.priority.set("Medium")
        self.priority.grid(row=0, column=2, padx=5)

        tk.Button(
            frame,
            text="Add Task",
            command=self.add_task,
            bg="#444",
            fg="white"
        ).grid(row=0, column=3, padx=5)

        # ===== SEARCH =====
        self.search = tk.Entry(root, width=40, fg="gray")
        self.search.pack(pady=5)

        self.search.insert(0, "🔍 Search tasks...")

        self.search.bind("<FocusIn>", self.on_focus_in)
        self.search.bind("<FocusOut>", self.on_focus_out)
        self.search.bind("<KeyRelease>", lambda e: self.refresh_list())

        # ===== LIST =====
        self.listbox = tk.Listbox(
            root,
            width=100,
            height=18,
            bg="#1e1e1e",
            fg="white"
        )
        self.listbox.pack(pady=10)

        # ===== BUTTONS =====
        btn = tk.Frame(root, bg="#121212")
        btn.pack()

        tk.Button(btn, text="✔ Complete", command=self.complete).grid(row=0, column=0, padx=5)
        tk.Button(btn, text="✖ Incomplete", command=self.incomplete).grid(row=0, column=1, padx=5)
        tk.Button(btn, text="🗑 Delete", command=self.delete).grid(row=0, column=2, padx=5)

        self.refresh_list()
        self.reminder_loop()

    # ===== SEARCH =====
    def on_focus_in(self, event):
        if self.search.get() == "🔍 Search tasks...":
            self.search.delete(0, tk.END)
            self.search.config(fg="white")

    def on_focus_out(self, event):
        if self.search.get() == "":
            self.search.insert(0, "🔍 Search tasks...")
            self.search.config(fg="gray")

    # ===== CORE =====
    def set_note(self):
        note = simpledialog.askstring("Quote", "Write something 💡")
        if note:
            self.daily_note = note
            self.note_label.config(text=note)
            self.save()

    def add_task(self):
        task = self.task_entry.get().strip()
        if not task:
            messagebox.showwarning("Warning", "Task cannot be empty")
            return

        self.tasks.append({
            "task": task,
            "date": self.date_entry.get(),
            "priority": self.priority.get(),
            "completed": False
        })

        self.task_entry.delete(0, tk.END)
        self.save()
        self.refresh_list()

    def delete(self):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            task = self.filtered_tasks[index]
            self.tasks.remove(task)
            self.save()
            self.refresh_list()

    def complete(self):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            self.filtered_tasks[index]["completed"] = True
            self.save()
            self.refresh_list()

    def incomplete(self):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            self.filtered_tasks[index]["completed"] = False
            self.save()
            self.refresh_list()

    # ===== UI =====
    def refresh_list(self):
        self.listbox.delete(0, tk.END)

        keyword = self.search.get().lower()
        if keyword == "🔍 search tasks...":
            keyword = ""

        self.filtered_tasks = []

        for task in self.tasks:
            name = task.get("task", "")
            if keyword and keyword not in name.lower():
                continue
            self.filtered_tasks.append(task)

        for i, task in enumerate(self.filtered_tasks):
            completed = task.get("completed", False)

            if completed:
                text = f"✔ {task.get('task')} | {task.get('date')} | {task.get('priority')}"
                self.listbox.insert(tk.END, text)
                self.listbox.itemconfig(i, fg="lightgreen")
            else:
                text = f"✖ {task.get('task')} | {task.get('date')} | {task.get('priority')}"
                self.listbox.insert(tk.END, text)
                self.listbox.itemconfig(i, fg="red")

        self.update_progress()

    def update_progress(self):
        today = datetime.now().strftime("%Y-%m-%d")
        today_tasks = [t for t in self.tasks if t.get("date") == today]

        if not today_tasks:
            self.progress['value'] = 0
            self.progress_text.config(text="0%")
            return

        done = len([t for t in today_tasks if t.get("completed")])
        percent = int((done / len(today_tasks)) * 100)

        self.progress['value'] = percent
        self.progress_text.config(text=f"{percent}% completed")

    # ===== STORAGE =====
    def save(self):
        with open(DATA_FILE, "w") as f:
            json.dump({
                "tasks": self.tasks,
                "note": self.daily_note
            }, f)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE) as f:
                    data = json.load(f)

                    if isinstance(data, dict):
                        self.tasks = data.get("tasks", [])
                        self.daily_note = data.get("note", "")
                    else:
                        self.tasks = data
            except:
                self.tasks = []
                self.daily_note = ""

    # ===== REMINDER =====
    def reminder_loop(self):
        today = datetime.now().strftime("%Y-%m-%d")
        pending = [t for t in self.tasks if t.get("date") == today and not t.get("completed")]

        if pending:
            messagebox.showinfo("Reminder 🔔", f"{len(pending)} pending tasks!")

        self.root.after(60000, self.reminder_loop)


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()