#!/usr/bin/env python3

from PIL import ImageTk, ImageOps
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from label import Label

# TODO: Parameterise this and DPI
aspect_ratio = 36 / 89

class GeneralLabelUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def update_preview(self, lines):
        lbl = Label(lines)
        img = lbl.image()
        img = img.resize((self.preview.winfo_reqwidth(), self.preview.winfo_reqheight()))

        self.bmp = ImageTk.BitmapImage(img, foreground='white')
        self.preview.create_rectangle(0, 0, self.preview.winfo_reqwidth(), self.preview.winfo_reqheight(), fill='black')
        self.preview.create_image(0, 0, image=self.bmp, anchor="nw")

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
        lines = self.get_lines()
        lbl = Label(lines)
        img = lbl.image()
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

        # Label preview
        self.preview_lbl = tk.Label(self, text="Label preview:")
        self.preview_lbl.grid(column = 0, row = row, sticky='w', pady=[20, 0])
        row +=1

        self.preview = tk.Canvas(self, width=500, height=int(500 * aspect_ratio), background='white')
        self.preview.grid(column = 0, row = row, pady=[0, 20])
        row += 1

        # Print button
        self.print = tk.Button(self, text='Print', font=('Arial', 24), command=self.__print)
        self.print.grid(column = 0, row = row, ipady=10, sticky='nsew')
        row += 1

        self.textbox.bind('<<Modified>>', self.__text_modified)  


def main():
    root = tk.Tk()
    app = GeneralLabelUI(master=root)
    root.resizable(False,False)
    app.mainloop()

if __name__ == "__main__":
    main()
