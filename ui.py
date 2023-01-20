#!/usr/bin/env python3

import copy
import datetime
from PIL import ImageTk, ImageOps
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from label import Label
from printer import DisplayPrinter

import time

UPDATE_DELAY=300

class LabelPreview(tk.Frame):
    # XXX: There seems to be an unavoidable 5mm margin on the right edge,
    # So just scale down the label by 10mm.
    __label_width_mm = 89 - 10
    __label_height_mm = 36
    __aspect_ratio = __label_height_mm / __label_width_mm

    def __init__(self, master=None, width=400):
        super().__init__(master)
        self.master = master
        self.canvas = tk.Canvas(self, width=width, height=int(width * LabelPreview.__aspect_ratio), background='white')
        self.canvas.pack()
        self.lines = ['']
        self.update(self.lines)

    def update(self, lines):
        if lines == self.lines:
            return
        self.lines = copy.deepcopy(lines)

        self.lbl = Label(lines, dpi=300,
                         size_mm=(LabelPreview.__label_width_mm, LabelPreview.__label_height_mm))

        img = self.lbl.image()
        img = img.resize((self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight()))
        self.bmp = ImageTk.BitmapImage(img, foreground='white')
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight(), fill='black')
        self.canvas.create_image(0, 0, image=self.bmp, anchor="nw")

    def image(self):
        return self.lbl.image()

class NameBadgeUI(tk.Frame):
    def __init__(self, master=None, printer=DisplayPrinter()):
        super().__init__(master)
        self.master = master
        self.printer = printer
        self.create_widgets()
        self.generation = 0
        self.timer_id = None
        self.__text_modified()

        self.event_add("<<Print_Label>>", "None")
        self.bind('<<Print_Label>>', self.handle_print_event)

    def handle_print_event(self, event):
        self.__print()

    def update_preview(self, lines):
        self.preview.update(lines)

    def get_lines(self):
        name_text = self.namevar.get()
        comment_text = self.commentvar.get()
        lines = []
        if len(name_text) > 0:
            lines.append(name_text)
        if len(comment_text) > 0:
            lines.append(comment_text)

        if len(lines) == 0:
            return [' ']

        return lines

    def __update_timer_cb(self, generation):
        lines = self.get_lines()
        self.update_preview(lines)

        if generation < self.generation:
            self.timer_id = self.after(UPDATE_DELAY, self.__update_timer_cb, self.generation)
        else:
            self.timer_id = None

    def __text_modified(self, *args):
        self.generation += 1

        if self.timer_id is None:
            self.timer_id = self.after(UPDATE_DELAY, self.__update_timer_cb, self.generation)

    def __print(self):
        print("Printing...")
        img = self.preview.image()
        self.printer.print_image(img)

    def create_widgets(self):
        row = 0
        self.grid(padx=20, pady=20)

        # Name Box
        self.namebox_lbl = tk.Label(self, text="Name:")
        self.namebox_lbl.grid(column = 0, row = row, sticky='w')

        self.namevar = tk.StringVar(self, "Your Name")
        self.namebox = ttk.Entry(self, textvariable=self.namevar)
        self.namebox.grid(column = 1, row = row, sticky = 'nwes')
        row += 1

        # Comment Box
        self.cbox_lbl = tk.Label(self, text="Comment:")
        self.cbox_lbl.grid(column = 0, row = row, sticky='w')

        self.commentvar = tk.StringVar(self, "Your Comment")
        self.commentbox = ttk.Entry(self, textvariable=self.commentvar)
        self.commentbox.grid(column = 1, row = row, sticky = 'nwes')
        row += 1

        # Separator
        self.sep = ttk.Separator(self, orient='horizontal')
        self.sep.grid(column = 0, row = row, columnspan=2, sticky='we', pady=20)
        row +=1

        # Label preview
        self.preview_lbl = tk.Label(self, text="Label preview:")
        self.preview_lbl.grid(column = 0, row = row, sticky='w')
        row +=1

        self.preview = LabelPreview(self, 400)
        self.preview.grid(column = 0, row = row, columnspan=2)
        row += 1

        # Print button
        self.print = tk.Button(self, text='Print', font=('Arial', 24), command=self.__print)
        self.print.grid(column = 0, row = row, columnspan=2, ipady=10, sticky='nsew')
        row += 1

        self.namevar.trace_add("write", self.__text_modified)
        self.commentvar.trace_add("write", self.__text_modified)

    def populate(self, name, comment):
        self.namevar.set(name)
        self.commentvar.set(comment)

    def reset(self):
        self.populate("Your Name", "Your Comment")

class DatabaseUI(tk.Frame):
    def __init__(self, master=None, db=None, printer=DisplayPrinter()):
        super().__init__(master)
        self.master = master
        self.printer = printer
        self.db = db
        self.create_widgets()
        self.generation = 0
        self.timer_id = None
        self.__text_modified()

    def update_preview(self, lines):
        self.preview.update(lines)

    def get_lines(self):
        name_text = self.namevar.get()
        comment_text = self.commentvar.get()
        lines = []
        if len(name_text) > 0:
            lines.append(name_text)
        if len(comment_text) > 0:
            lines.append(comment_text)

        if len(lines) == 0:
            return [' ']

        return lines

    def __update_timer_cb(self, generation):
        lines = self.get_lines()
        self.update_preview(lines)

        if generation < self.generation:
            self.timer_id = self.after(UPDATE_DELAY, self.__update_timer_cb, self.generation)
        else:
            self.timer_id = None

    def __text_modified(self):
        self.generation += 1

        if self.timer_id is None:
            self.timer_id = self.after(UPDATE_DELAY, self.__update_timer_cb, self.generation)

    def __print(self):
        img = self.preview.image()
        self.printer.print_image(img)

    def create_widgets(self):
        row = 0
        self.grid(padx=20, pady=20)

        # Tag labels
        self.tagbox_lbl = tk.Label(self, text="Editing tag:")
        self.tagbox_lbl.grid(column = 0, row = row, sticky='w')

        self.tagvar = tk.StringVar(self, "Scan a tag while holding left button")
        self.tagbox = ttk.Entry(self, textvariable=self.tagvar, state='disabled')
        self.tagbox.grid(column = 1, row = row, sticky = 'nwes')
        row += 1

        # Name Box
        self.namebox_lbl = tk.Label(self, text="Name:")
        self.namebox_lbl.grid(column = 0, row = row, sticky='w')

        self.namevar = tk.StringVar(self, "Hold left button")
        self.namebox = ttk.Entry(self, textvariable=self.namevar, state='disabled')
        self.namebox.grid(column = 1, row = row, sticky = 'nwes')
        row += 1

        # Comment Box
        self.cbox_lbl = tk.Label(self, text="Comment:")
        self.cbox_lbl.grid(column = 0, row = row, sticky='w')

        self.commentvar = tk.StringVar(self, "And scan a tag to update it")
        self.commentbox = ttk.Entry(self, textvariable=self.commentvar, state='disabled')
        self.commentbox.grid(column = 1, row = row, sticky = 'nwes')
        row += 1

        # Separator
        self.sep = ttk.Separator(self, orient='horizontal')
        self.sep.grid(column = 0, row = row, columnspan=2, sticky='we', pady=20)
        row +=1

        # Label preview
        self.preview_lbl = tk.Label(self, text="Label preview:")
        self.preview_lbl.grid(column = 0, row = row, sticky='w')
        row +=1

        self.preview = LabelPreview(self, 400)
        self.preview.grid(column = 0, row = row, columnspan=2)
        row += 1

        # Save / Print button
        self.print = tk.Button(self, text='Print', font=('Arial', 24), state='disabled',
                               command=self.__print)
        self.print.grid(column = 0, row = row, columnspan=1, ipady=10, sticky='nsew')

        self.save = tk.Button(self, text='Save', font=('Arial', 24), state='disabled',
                              command=self.do_save)
        self.save.grid(column = 1, row = row, columnspan=1, ipady=10, sticky='nsew')
        row += 1

        self.namevar.trace_add("write", self.__text_modified)
        self.commentvar.trace_add("write", self.__text_modified)

    def do_save(self):
        if not self.db:
            # Can't do anything without a database
            self.reset()
            return

        tag = bytes.fromhex(self.tagvar.get())
        name = self.namevar.get()
        comment = self.commentvar.get()

        try:
            self.db.update(tag, name, comment)
        except:
            self.db.insert(tag, name, comment)

        self.tagvar.set("Scan a tag while holding left button")
        self.namebox['state'] = 'disabled'
        self.commentbox['state'] = 'disabled'
        self.save['state'] = 'disabled'

    def populate(self, tag, name="Your Name", comment="Your Comment"):
        if not self.db:
            # Can't do anything without a database
            self.reset()
            return

        self.tagvar.set(tag.hex())
        self.namevar.set(name)
        self.commentvar.set(comment)
        self.namebox['state'] = 'enabled'
        self.commentbox['state'] = 'enabled'
        self.print['state'] = 'normal'
        self.save['state'] = 'normal'

    def reset(self):
        self.tagvar.set("Scan a tag while holding left button")
        self.namevar.set("-")
        self.commentvar.set("-")
        self.namebox['state'] = 'disabled'
        self.commentbox['state'] = 'disabled'
        self.print['state'] = 'disabled'
        self.save['state'] = 'disabled'

class TroveLabelUI(tk.Frame):
    def __init__(self, master=None, printer=DisplayPrinter()):
        super().__init__(master)
        self.master = master
        self.printer = printer
        self.create_widgets()
        self.generation = 0
        self.timer_id = None
        self.__set_out_to_days(30)
        self.__text_modified()

    def update_preview(self, lines):
        self.preview.update(lines)

    def get_lines(self):
        name_text = self.namevar.get()
        contact_text = self.contactvar.get()
        out_text = self.outvar.get()

        today = datetime.date.today()
        in_text = f"Date in: {today.isoformat()}"
        out_text = "Use by: " + out_text

        return [
                [name_text],
                [contact_text],
                [in_text, out_text],
        ]

    def __update_timer_cb(self, generation):
        lines = self.get_lines()
        self.update_preview(lines)

        if generation < self.generation:
            self.timer_id = self.after(UPDATE_DELAY, self.__update_timer_cb, self.generation)
        else:
            self.timer_id = None

    def __set_out_to_days(self, days):
        today = datetime.date.today()
        delta = datetime.timedelta(days=days)
        out = today + delta
        self.outvar.set(out.isoformat())

    def __text_modified(self, *args):
        name_text = self.namevar.get()
        contact_text = self.contactvar.get()
        out_text = self.outvar.get()

        if len(name_text) == 0 or len(contact_text) == 0 or len(out_text) == 0:
                self.print['state'] = 'disabled'
        else:
                self.print['state'] = 'normal'

        self.generation += 1

        if self.timer_id is None:
            self.timer_id = self.after(UPDATE_DELAY, self.__update_timer_cb, self.generation)

    def __print(self):
        img = self.preview.image()
        self.printer.print_image(img)

    def create_widgets(self):
        row = 0
        self.grid(padx=20, pady=20)

        # Name Box
        self.namebox_lbl = tk.Label(self, text="Name:")
        self.namebox_lbl.grid(column = 0, row = row, sticky='w')

        self.namevar = tk.StringVar(self, "Your Name")
        self.namebox = ttk.Entry(self, textvariable=self.namevar)
        self.namebox.grid(column = 1, row = row, columnspan=2, sticky = 'nwes')
        row += 1

        # Contact Box
        self.cbox_lbl = tk.Label(self, text="Contact:")
        self.cbox_lbl.grid(column = 0, row = row, sticky='w')

        self.contactvar = tk.StringVar(self, "Your Contact Info")
        self.contactbox = ttk.Entry(self, textvariable=self.contactvar)
        self.contactbox.grid(column = 1, row = row, columnspan=2, sticky = 'nwes')
        row += 1

        # Date out
        self.outbox_lbl = tk.Label(self, text="Use by:")
        self.outbox_lbl.grid(column = 0, row = row, sticky='w')

        self.outvar = tk.StringVar(self, "1970-01-01")
        self.outbox = ttk.Entry(self, textvariable=self.outvar)
        self.outbox.grid(column = 1, row = row, columnspan=2, sticky = 'nwes')
        row += 1

        # Date buttons
        self.monthbutton1 = ttk.Button(self, text="1 month",
                                       command=lambda: self.__set_out_to_days(30))
        self.monthbutton1.grid(column = 1, row = row, sticky = 'nwes')

        self.monthbutton3 = ttk.Button(self, text="3 months",
                                       command=lambda: self.__set_out_to_days(90))
        self.monthbutton3.grid(column = 2, row = row, sticky = 'nwes')
        row += 1

        # Separator
        self.sep = ttk.Separator(self, orient='horizontal')
        self.sep.grid(column = 0, row = row, columnspan=3, sticky='we', pady=20)
        row += 1

        # Label preview
        self.preview_lbl = tk.Label(self, text="Label preview:")
        self.preview_lbl.grid(column = 0, row = row, sticky='w')
        row += 1

        self.preview = LabelPreview(self, 400)
        self.preview.grid(column = 0, row = row, columnspan=3)
        row += 1

        # Print button
        self.print = tk.Button(self, text='Print', font=('Arial', 24), command=self.__print)
        self.print.grid(column = 0, row = row, columnspan=3, ipady=10, sticky='nsew')
        row += 1

        self.namevar.trace_add("write", self.__text_modified)
        self.contactvar.trace_add("write", self.__text_modified)
        self.outvar.trace_add("write", self.__text_modified)

    def populate(self, name, comment):
        self.namevar.set(name)
        self.contactvar.set(comment)
        self.__set_out_to_days(30)
        self.__text_modified()

    def reset(self):
        self.populate("Your Name", "Your Contact Info")

class GeneralLabelUI(tk.Frame):
    def __init__(self, master=None, printer=DisplayPrinter()):
        super().__init__(master)
        self.master = master
        self.printer = printer
        self.create_widgets()
        self.last_mod_time = 0
        self.timer_id = None

    def invalidate(self):
        self.print['state'] = 'disabled'

    def update_preview(self):
        lines = self.get_lines()
        self.preview.update(lines)
        self.print['state'] = 'normal'

    def get_lines(self):
        # Text always adds an invisible trailing newline, so remove that
        # Don't use strip('\n') because the user might have added deliberate
        # blank lines for formatting
        text = self.textbox.get('1.0', 'end')[:-1]
        lines = text.split('\n')
        return lines

    def __update_timer_cb(self):
        now = time.monotonic_ns()
        diff = now - self.last_mod_time
        if diff >= UPDATE_DELAY * 1000000:
            self.update_preview()
            self.timer_id = None
        else:
            self.timer_id = self.after(UPDATE_DELAY - (diff * 1000000) + 10,
                                       self.__update_timer_cb)

    def __text_modified(self, event):
        self.invalidate()
        self.last_mod_time = time.monotonic_ns()
        self.textbox.edit_modified(False)

        if self.timer_id is None:
            self.timer_id = self.after(UPDATE_DELAY, self.__update_timer_cb)

    def __print(self):
        self.update_preview()
        img = self.preview.image()
        self.printer.print_image(img)

    def create_widgets(self):
        row = 0
        self.grid(padx=20, pady=20)

        self.textbox_lbl = tk.Label(self, text="Enter text for label:")
        self.textbox_lbl.grid(column = 0, row = row, sticky='w')
        row +=1

        # Text entry with scrollbars
        self.textbox = tk.Text(self, width=32, height=5, wrap="none", font=('Arial', 14))
        ys = ttk.Scrollbar(self, orient = 'vertical', command = self.textbox.yview)
        xs = ttk.Scrollbar(self, orient = 'horizontal', command = self.textbox.xview)
        self.textbox['yscrollcommand'] = ys.set
        self.textbox['xscrollcommand'] = xs.set
        self.textbox.insert('1.0', "Create a Label\nWith all the content you want\nMaybe a Haiku")

        self.textbox.grid(column = 0, row = row, sticky = 'nwes')
        ys.grid(column = 1, row = row, sticky = 'ns')
        row += 1

        xs.grid(column = 0, row = row, sticky = 'we')
        row += 1

        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        # Separator
        self.sep = ttk.Separator(self, orient='horizontal')
        self.sep.grid(column = 0, row = row, sticky='we', pady=20)
        row +=1

        # Label preview
        self.preview_lbl = tk.Label(self, text="Label preview:")
        self.preview_lbl.grid(column = 0, row = row, sticky='w')
        row +=1

        self.preview = LabelPreview(self, 400)
        self.preview.grid(column = 0, row = row)
        row += 1

        # Print button
        self.print = tk.Button(self, text='Print', font=('Arial', 24), command=self.__print)
        self.print.grid(column = 0, row = row, ipady=10, sticky='nsew')
        row += 1

        self.textbox.bind('<<Modified>>', self.__text_modified)

    def reset(self):
        self.textbox.delete("1.0", "end")
        self.textbox.insert('1.0', "Create a Label\nWith all the content you want\nMaybe a Haiku")

def main():
    root = tk.Tk()
    nb = ttk.Notebook(root)
    nb.pack()

    namebadge_ui = NameBadgeUI(nb)
    trovelabel_ui = TroveLabelUI(nb)
    general_ui = GeneralLabelUI(nb)
    db_ui = DatabaseUI(nb)

    nb.add(namebadge_ui, text="Name Badge")
    nb.add(trovelabel_ui, text="Storage Label")
    nb.add(general_ui, text="General Label")
    nb.add(db_ui, text="Edit Tag")

    app = root
    root.resizable(False,False)
    app.mainloop()

if __name__ == "__main__":
    main()
