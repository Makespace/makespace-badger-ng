#!/usr/bin/env python3

from PIL import ImageTk, ImageOps
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from label import Label

class LabelPreview(tk.Frame):
    # TODO: Parameterise this and DPI
    __aspect_ratio = 36 / 89

    def __init__(self, master=None, width=500):
        super().__init__(master)
        self.master = master
        self.canvas = tk.Canvas(self, width=width, height=int(width * LabelPreview.__aspect_ratio), background='white')
        self.canvas.pack()
        self.update([''])

    def update(self, lines):
        self.lbl = Label(lines)

        img = self.lbl.image()
        img = img.resize((self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight()))
        self.bmp = ImageTk.BitmapImage(img, foreground='white')
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight(), fill='black')
        self.canvas.create_image(0, 0, image=self.bmp, anchor="nw")

    def image(self):
        return self.lbl.image()

class NameBadgeUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def update_preview(self, lines):
        self.preview.update(lines)

    def get_lines(self):
        # Text always adds an invisible trailing newline, so remove that
        name_text = self.namebox.get('1.0', 'end')[:-1]
        comment_text = self.cbox.get('1.0', 'end')[:-1]
        lines = []
        if len(name_text) > 0:
            lines.append(name_text)
        if len(comment_text) > 0:
            lines.append(comment_text)

        if len(lines) == 0:
            return [' ']

        return lines

    def __text_modified(self, event):
        lines = self.get_lines()
        self.update_preview(lines)
        event.widget.edit_modified(False)

    def __print(self):
        img = self.preview.image()
        img.show()

    def create_widgets(self):
        row = 0
        self.grid(padx=20, pady=20)

        # Name Box
        self.namebox_lbl = tk.Label(self, text="Name:")
        self.namebox_lbl.grid(column = 0, row = row, sticky='w')

        self.namebox = tk.Text(self, width=32, height=1, wrap="none", font=('Arial'))
        self.namebox.insert('1.0', "Your Name")
        self.namebox.grid(column = 1, row = row, sticky = 'nwes')
        row += 1

        # Contact Box
        self.cbox_lbl = tk.Label(self, text="Comment:")
        self.cbox_lbl.grid(column = 0, row = row, sticky='w')

        self.cbox = tk.Text(self, width=32, height=1, wrap="none", font=('Arial'))
        self.cbox.insert('1.0', "Your comment")
        self.cbox.grid(column = 1, row = row, sticky = 'nwes')
        row += 1

        # Separator
        self.sep = ttk.Separator(self, orient='horizontal')
        self.sep.grid(column = 0, row = row, columnspan=2, sticky='we', pady=20)
        row +=1

        # Label preview
        self.preview_lbl = tk.Label(self, text="Label preview:")
        self.preview_lbl.grid(column = 0, row = row, sticky='w')
        row +=1

        self.preview = LabelPreview(self, 500)
        self.preview.grid(column = 0, row = row, columnspan=2)
        row += 1

        # Print button
        self.print = tk.Button(self, text='Print', font=('Arial', 24), command=self.__print)
        self.print.grid(column = 0, row = row, columnspan=2, ipady=10, sticky='nsew')
        row += 1

        self.namebox.bind('<<Modified>>', self.__text_modified)
        self.cbox.bind('<<Modified>>', self.__text_modified)

class GeneralLabelUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def update_preview(self, lines):
        self.preview.update(lines)

    def get_lines(self):
        # Text always adds an invisible trailing newline, so remove that
        # Don't use strip('\n') because the user might have added deliberate
        # blank lines for formatting
        text = self.textbox.get('1.0', 'end')[:-1]
        lines = text.split('\n')

        return lines

    def __text_modified(self, event):
        lines = self.get_lines()
        self.update_preview(lines)
        self.textbox.edit_modified(False)

    def __print(self):
        img = self.preview.image()
        img.show()

    def create_widgets(self):
        row = 0
        self.grid(padx=20, pady=20)

        self.textbox_lbl = tk.Label(self, text="Enter text for label:")
        self.textbox_lbl.grid(column = 0, row = row, sticky='w')
        row +=1

        # Text entry with scrollbars
        self.textbox = tk.Text(self, width=32, height=5, wrap="none", font=('Arial', 24))
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

        self.preview = LabelPreview(self, 500)
        self.preview.grid(column = 0, row = row)
        row += 1

        # Print button
        self.print = tk.Button(self, text='Print', font=('Arial', 24), command=self.__print)
        self.print.grid(column = 0, row = row, ipady=10, sticky='nsew')
        row += 1

        self.textbox.bind('<<Modified>>', self.__text_modified)


def main():
    root = tk.Tk()
    app = NameBadgeUI(master=root)
    root.resizable(False,False)
    app.mainloop()

if __name__ == "__main__":
    main()
