import os
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import time
import platform

# --- CRASH PREVENTION ---
os.environ['TK_SILENCE_DEPRECATION'] = '1'

class FontPicker(tk.Toplevel):
    def __init__(self, parent, current_font, callback):
        super().__init__(parent)
        self.title("Select Font")
        self.geometry("300x450")
        self.callback = callback
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        tk.Label(self, text="Search Fonts:").pack(pady=5)
        self.entry = tk.Entry(self, textvariable=self.search_var)
        self.entry.pack(fill='x', padx=10)
        self.entry.focus_set()

        self.frame = tk.Frame(self)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.listbox = tk.Listbox(self.frame)
        self.listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(self.frame, command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        from tkinter import font
        self.all_fonts = sorted(font.families())
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.update_list()

    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for f in self.all_fonts:
            if search_term in f.lower():
                self.listbox.insert(tk.END, f)

    def on_select(self, event):
        if self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            self.callback(selected)

class DateSettingsWindow(tk.Toplevel):
    def __init__(self, parent, clock_app):
        super().__init__(parent)
        self.title("Date Settings")
        self.clock = clock_app
        self.geometry("280x350")
        self.resizable(False, False)

        self.show_var = tk.BooleanVar(value=self.clock.show_date)
        tk.Checkbutton(self, text="Show Date", variable=self.show_var, 
                       command=self.sync_show).pack(pady=10)

        tk.Label(self, text="Alignment:").pack()
        self.align_combo = ttk.Combobox(self, values=["center", "left", "right"], state="readonly")
        self.align_combo.set(self.clock.date_align)
        self.align_combo.pack(pady=5)
        self.align_combo.bind("<<ComboboxSelected>>", lambda e: self.set_val('date_align'))

        tk.Label(self, text="Font Ratio:").pack()
        self.ratio_combo = ttk.Combobox(self, values=["1/4", "1/3", "1/2"], state="readonly")
        self.ratio_combo.set(self.clock.date_ratio_str)
        self.ratio_combo.pack(pady=5)
        self.ratio_combo.bind("<<ComboboxSelected>>", lambda e: self.set_val('date_ratio_str'))

        tk.Label(self, text="Language:").pack()
        self.lang_combo = ttk.Combobox(self, values=["Turkish", "English", "Turkish (Safe)"], state="readonly")
        self.lang_combo.set(self.clock.lang)
        self.lang_combo.pack(pady=5)
        self.lang_combo.bind("<<ComboboxSelected>>", lambda e: self.set_val('lang'))

    def sync_show(self):
        self.clock.show_date = self.show_var.get()
        self.clock.refresh_ui()

    def set_val(self, attr):
        if attr == 'date_align': self.clock.date_align = self.align_combo.get()
        if attr == 'date_ratio_str': self.clock.date_ratio_str = self.ratio_combo.get()
        if attr == 'lang': self.clock.lang = self.lang_combo.get()
        self.clock.refresh_ui()

class DesktopClock:
    def __init__(self):
        self.root = tk.Tk()
        self.os_name = platform.system()
        
        # Defaults
        self.current_font = 'Arial' if self.os_name == 'Windows' else 'Didot'
        self.current_size = 110
        self.show_date = True
        self.date_align = "center"
        self.date_ratio_str = "1/3"
        self.lang = "Turkish"
        
        self.months = {
            "Turkish": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
            "Turkish (Safe)": ["Ocak", "Subat", "Mart", "Nisan", "Mayis", "Haziran", "Temmuz", "Agustos", "Eylul", "Ekim", "Kasim", "Aralik"],
            "English": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        }
        self.days = {
            "Turkish": ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"],
            "Turkish (Safe)": ["Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar"],
            "English": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        }
        
        # --- OS SPECIFIC TRANSPARENCY ---
        self.root.overrideredirect(True)
        if self.os_name == 'Darwin': 
            self.root.config(bg='systemTransparent')
            self.root.wm_attributes("-transparent", True)
        elif self.os_name == 'Windows':
            self.root.config(bg='black')
            self.root.wm_attributes("-transparentcolor", "black")
        else:
            try: self.root.wait_visibility(self.root)
            except: pass
            self.root.wm_attributes("-alpha", 0.9)
            self.root.config(bg='black')

        self.container = tk.Frame(self.root, bg='systemTransparent' if self.os_name == 'Darwin' else 'black')
        self.container.pack(expand=True, fill='both')

        self.time_label = tk.Label(self.container, fg='white', bg='systemTransparent' if self.os_name == 'Darwin' else 'black')
        self.time_label.pack(side='top')

        self.date_label = tk.Label(self.container, fg='white', bg='systemTransparent' if self.os_name == 'Darwin' else 'black')

        for w in [self.time_label, self.date_label]:
            w.bind("<Button-1>", self.start_move)
            w.bind("<B1-Motion>", self.do_move)
            w.bind("<Button-2>", self.show_menu)
            w.bind("<Button-3>", self.show_menu)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Browse Fonts", command=lambda: FontPicker(self.root, self.current_font, self.set_font))
        self.menu.add_command(label="Edit Time Size", command=self.edit_size)
        self.menu.add_command(label="Date Settings", command=lambda: DateSettingsWindow(self.root, self))
        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=self.root.destroy)

        self.refresh_ui()
        self.center_window()
        self.apply_os_tweaks()
        self.update_clock()
        self.root.mainloop()

    def apply_os_tweaks(self):
        if self.os_name == 'Darwin':
            try:
                import AppKit
                ns_app = AppKit.NSApplication.sharedApplication()
                ns_app.setActivationPolicy_(1)
                AppKit.NSApp.activateIgnoringOtherApps_(True)
            except: pass
        elif self.os_name == 'Windows':
            self.root.attributes("-topmost", False)

    def get_formatted_date(self):
        t = time.localtime()
        m_list = self.months.get(self.lang, self.months["English"])
        d_list = self.days.get(self.lang, self.days["English"])
        if "Turkish" in self.lang:
            return f"{t.tm_mday} {m_list[t.tm_mon-1]} {t.tm_year}, {d_list[t.tm_wday]}"
        return f"{d_list[t.tm_wday]}, {m_list[t.tm_mon-1]} {t.tm_mday}, {t.tm_year}"

    def set_font(self, font_name):
        self.current_font = font_name
        self.refresh_ui()

    def refresh_ui(self):
        ratio_map = {"1/4": 4, "1/3": 3, "1/2": 2}
        date_size = self.current_size // ratio_map.get(self.date_ratio_str, 3)
        self.time_label.config(font=(self.current_font, self.current_size, 'bold'), text=time.strftime('%H:%M'))
        self.date_label.config(font=(self.current_font, date_size, 'normal'), text=self.get_formatted_date())
        
        anchor_map = {"center": "center", "left": "w", "right": "e"}
        active_anchor = anchor_map.get(self.date_align, "center")
        self.time_label.pack_configure(anchor=active_anchor)
        
        if self.show_date:
            self.date_label.pack(side='top', fill='x')
            self.date_label.pack_configure(anchor=active_anchor)
        else:
            self.date_label.pack_forget()

        self.root.update_idletasks()
        ww = max(self.time_label.winfo_reqwidth(), self.date_label.winfo_reqwidth() if self.show_date else 0)
        wh = self.time_label.winfo_reqheight() + (self.date_label.winfo_reqheight() if self.show_date else 0)
        curr_x, curr_y = self.root.winfo_x(), self.root.winfo_y()
        self.root.geometry(f'{int(ww)}x{int(wh)}+{curr_x}+{curr_y}')

    def center_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        ww = self.root.winfo_width()
        self.root.geometry(f'+{(sw-ww)//2}+100')

    def start_move(self, event):
        self.root.lift(); self.x, self.y = event.x, event.y

    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def edit_size(self):
        new_size = simpledialog.askinteger("Size", "Enter Time Font Size:", parent=self.root)
        if new_size: self.current_size = new_size; self.refresh_ui()

    def update_clock(self):
        self.time_label.config(text=time.strftime('%H:%M'))
        if self.show_date: self.date_label.config(text=self.get_formatted_date())
        self.root.lower(); self.root.after(5000, self.update_clock)

if __name__ == "__main__":
    time.sleep(0.5)
    DesktopClock()
