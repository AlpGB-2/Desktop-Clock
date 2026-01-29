import os
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

# --- CRASH PREVENTION ---
os.environ['TK_SILENCE_DEPRECATION'] = '1'


class FontSelectionDialog(tk.Toplevel):
    def __init__(self, parent, selected_font, on_font_selected):
        super().__init__(parent)
        self.title("Select Font")
        self.geometry("300x450")
        self.on_font_selected = on_font_selected

        self.search_variable = tk.StringVar()
        self.search_variable.trace_add("write", self._filter_fonts)

        tk.Label(self, text="Search Font:").pack(pady=5)
        self.search_entry = tk.Entry(self, textvariable=self.search_variable)
        self.search_entry.pack(fill="x", padx=10)
        self.search_entry.focus_set()

        self.list_frame = tk.Frame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.font_listbox = tk.Listbox(self.list_frame)
        self.font_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.list_frame, command=self.font_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.font_listbox.config(yscrollcommand=scrollbar.set)

        from tkinter import font
        self.available_fonts = sorted(font.families())

        self.font_listbox.bind("<<ListboxSelect>>", self._handle_font_selection)
        self._populate_font_list()

    def _populate_font_list(self):
        self.font_listbox.delete(0, tk.END)
        for font_name in self.available_fonts:
            self.font_listbox.insert(tk.END, font_name)

    def _filter_fonts(self, *_):
        query = self.search_variable.get().lower()
        self.font_listbox.delete(0, tk.END)
        for font_name in self.available_fonts:
            if query in font_name.lower():
                self.font_listbox.insert(tk.END, font_name)

    def _handle_font_selection(self, _event):
        if self.font_listbox.curselection():
            selected_font = self.font_listbox.get(self.font_listbox.curselection())
            self.on_font_selected(selected_font)


class DateConfigurationWindow(tk.Toplevel):
    def __init__(self, parent, clock_app):
        super().__init__(parent)
        self.title("Date Configuration")
        self.clock_app = clock_app
        self.geometry("280x350")
        self.resizable(False, False)

        self.show_date_variable = tk.BooleanVar(value=self.clock_app.is_date_visible)
        tk.Checkbutton(
            self,
            text="Show Date",
            variable=self.show_date_variable,
            command=self._sync_date_visibility
        ).pack(pady=10)

        tk.Label(self, text="Alignment:").pack()
        self.alignment_selector = ttk.Combobox(
            self,
            values=["center", "left", "right"],
            state="readonly"
        )
        self.alignment_selector.set(self.clock_app.date_alignment)
        self.alignment_selector.pack(pady=5)
        self.alignment_selector.bind(
            "<<ComboboxSelected>>",
            lambda e: self._update_setting("date_alignment")
        )

        tk.Label(self, text="Font Ratio:").pack()
        self.font_ratio_selector = ttk.Combobox(
            self,
            values=["1/4", "1/3", "1/2"],
            state="readonly"
        )
        self.font_ratio_selector.set(self.clock_app.date_font_ratio)
        self.font_ratio_selector.pack(pady=5)
        self.font_ratio_selector.bind(
            "<<ComboboxSelected>>",
            lambda e: self._update_setting("date_font_ratio")
        )

        tk.Label(self, text="Language:").pack()
        self.language_selector = ttk.Combobox(
            self,
            values=["Turkish", "English", "Turkish (Safe)"],
            state="readonly"
        )
        self.language_selector.set(self.clock_app.language)
        self.language_selector.pack(pady=5)
        self.language_selector.bind(
            "<<ComboboxSelected>>",
            lambda e: self._update_setting("language")
        )

    def _sync_date_visibility(self):
        self.clock_app.is_date_visible = self.show_date_variable.get()
        self.clock_app.refresh_display()

    def _update_setting(self, attribute_name):
        if attribute_name == "date_alignment":
            self.clock_app.date_alignment = self.alignment_selector.get()
        elif attribute_name == "date_font_ratio":
            self.clock_app.date_font_ratio = self.font_ratio_selector.get()
        elif attribute_name == "language":
            self.clock_app.language = self.language_selector.get()

        self.clock_app.refresh_display()


class ClockApplication:
    def __init__(self):
        self.root = tk.Tk()

        # Appearance settings
        self.current_font_family = "Didot"
        self.current_time_font_size = 110
        self.is_date_visible = True
        self.date_alignment = "center"
        self.date_font_ratio = "1/3"
        self.language = "Turkish"

        self.month_names = {
            "Turkish": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
            "Turkish (Safe)": ["Ocak", "Subat", "Mart", "Nisan", "Mayis", "Haziran",
                               "Temmuz", "Agustos", "Eylul", "Ekim", "Kasim", "Aralik"],
            "English": ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"]
        }

        self.day_names = {
            "Turkish": ["Pazartesi", "Salı", "Çarşamba", "Perşembe",
                        "Cuma", "Cumartesi", "Pazar"],
            "Turkish (Safe)": ["Pazartesi", "Sali", "Carsamba", "Persembe",
                               "Cuma", "Cumartesi", "Pazar"],
            "English": ["Monday", "Tuesday", "Wednesday", "Thursday",
                        "Friday", "Saturday", "Sunday"]
        }

        self._configure_root_window()
        self._create_widgets()
        self._create_context_menu()

        self.refresh_display()
        self._center_window()
        self._apply_macos_window_behavior()
        self._update_time_loop()

        self.root.mainloop()

    # -------------------- Window Setup --------------------

    def _configure_root_window(self):
        self.root.overrideredirect(True)
        self.root.config(bg="systemTransparent")
        self.root.wm_attributes("-transparent", True)

    def _create_widgets(self):
        self.container_frame = tk.Frame(self.root, bg="systemTransparent")
        self.container_frame.pack(expand=True, fill="both")

        self.time_label = tk.Label(
            self.container_frame,
            fg="white",
            bg="systemTransparent"
        )
        self.time_label.pack(side="top")

        self.date_label = tk.Label(
            self.container_frame,
            fg="white",
            bg="systemTransparent"
        )

        for widget in (self.time_label, self.date_label):
            widget.bind("<Button-1>", self._start_window_drag)
            widget.bind("<B1-Motion>", self._drag_window)
            widget.bind("<Button-2>", self._show_context_menu)
            widget.bind("<Button-3>", self._show_context_menu)

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="Browse Fonts",
            command=lambda: FontSelectionDialog(
                self.root,
                self.current_font_family,
                self.set_font_family
            )
        )
        self.context_menu.add_command(
            label="Edit Time Size",
            command=self._prompt_time_font_size
        )
        self.context_menu.add_command(
            label="Date Settings",
            command=lambda: DateConfigurationWindow(self.root, self)
        )
        self.context_menu.add_command(
            label="Manual Position",
            command=self._prompt_window_position
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Quit",
            command=self.root.destroy
        )

    # -------------------- Display Logic --------------------

    def get_formatted_date_string(self):
        current_time = time.localtime()
        months = self.month_names.get(self.language, self.month_names["English"])
        days = self.day_names.get(self.language, self.day_names["English"])

        if "Turkish" in self.language:
            return f"{current_time.tm_mday} {months[current_time.tm_mon - 1]} " \
                   f"{current_time.tm_year}, {days[current_time.tm_wday]}"

        return f"{days[current_time.tm_wday]}, {months[current_time.tm_mon - 1]} " \
               f"{current_time.tm_mday}, {current_time.tm_year}"

    def set_font_family(self, font_family):
        self.current_font_family = font_family
        self.refresh_display()

    def refresh_display(self):
        ratio_map = {"1/4": 4, "1/3": 3, "1/2": 2}
        date_font_size = self.current_time_font_size // ratio_map.get(
            self.date_font_ratio, 3
        )

        self.time_label.config(
            font=(self.current_font_family, self.current_time_font_size, "bold"),
            text=time.strftime("%H:%M")
        )

        self.date_label.config(
            font=(self.current_font_family, date_font_size, "normal"),
            text=self.get_formatted_date_string()
        )

        anchor_map = {"center": "center", "left": "w", "right": "e"}
        anchor = anchor_map.get(self.date_alignment, "center")

        self.time_label.pack_configure(anchor=anchor)

        if self.is_date_visible:
            self.date_label.pack(side="top", fill="x")
            self.date_label.pack_configure(anchor=anchor)
        else:
            self.date_label.pack_forget()

        self._update_window_geometry()

    def _update_window_geometry(self):
        self.root.update_idletasks()
        width = max(
            self.time_label.winfo_reqwidth(),
            self.date_label.winfo_reqwidth() if self.is_date_visible else 0
        )
        height = self.time_label.winfo_reqheight() + (
            self.date_label.winfo_reqheight() if self.is_date_visible else 0
        )

        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.geometry(f"{int(width)}x{int(height)}+{x}+{y}")

    # -------------------- Window Movement --------------------

    def _center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        window_width = self.root.winfo_width()
        self.root.geometry(f"+{(screen_width - window_width) // 2}+100")

    def _start_window_drag(self, event):
        self.root.lift()
        self.drag_offset_x = event.x
        self.drag_offset_y = event.y

    def _drag_window(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_offset_x)
        y = self.root.winfo_y() + (event.y - self.drag_offset_y)
        self.root.geometry(f"+{x}+{y}")

    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    # -------------------- User Input Dialogs --------------------

    def _prompt_time_font_size(self):
        new_size = simpledialog.askinteger(
            "Time Font Size",
            "Enter new font size for time:",
            parent=self.root
        )
        if new_size:
            self.current_time_font_size = new_size
            self.refresh_display()

    def _prompt_window_position(self):
        position_input = simpledialog.askstring(
            "Window Position",
            "Enter X,Y:",
            parent=self.root
        )
        if position_input:
            try:
                x, y = position_input.split(",")
                self.root.geometry(f"+{int(x)}+{int(y)}")
            except ValueError:
                pass

    # -------------------- macOS Behavior --------------------

    def _apply_macos_window_behavior(self):
        try:
            import AppKit
            AppKit.NSApplication.sharedApplication().setActivationPolicy_(1)
            AppKit.NSApp.activateIgnoringOtherApps_(True)
        except Exception:
            pass

    # -------------------- Time Update Loop --------------------

    def _update_time_loop(self):
        self.time_label.config(text=time.strftime("%H:%M"))

        if self.is_date_visible:
            self.date_label.config(text=self.get_formatted_date_string())

        self.root.lower()
        self.root.after(5000, self._update_time_loop)


if __name__ == "__main__":
    time.sleep(0.5)
    ClockApplication()
