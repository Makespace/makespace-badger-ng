#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk

class FakeTagReader(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.nreads = 0
        self.create_widgets()

    def create_widgets(self):
        row = 0
        self.grid(padx=20, pady=20)

        self.tagvar = tk.StringVar(self, "4777701c")
        self.tagbox = ttk.Entry(self, textvariable=self.tagvar)
        self.tagbox.grid(column = 0, row = row, columnspan = 2, sticky = 'nwes')
        row += 1

        self.left_var = tk.IntVar()
        self.left_chk = tk.Checkbutton(self, var=self.left_var)
        self.left_chk.grid(column = 0, row = row, sticky='nsew')

        self.right_var = tk.IntVar()
        self.right_chk = tk.Checkbutton(self, var=self.right_var)
        self.right_chk.grid(column = 1, row = row, sticky='nsew')
        row += 1

        self.present = tk.Button(self, text='Present Tag', font=('Arial', 14), command=self.present_tag)
        self.present.grid(column = 0, row = row, columnspan = 2, sticky='nsew')
        row += 1

    def present_tag(self):
        self.nreads = 5
        self.tag = bytes.fromhex(self.tagvar.get())

    def read_tag(self):
        if self.nreads > 0:
            self.nreads -= 1
            return self.tag
        return None

    def read_buttons(self):
        buttons = 0
        if self.left_var.get():
            buttons += 1
        if self.right_var.get():
            buttons += 2
        return buttons
