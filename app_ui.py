#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from ui import NameBadgeUI, TroveLabelUI, GeneralLabelUI, DatabaseUI
from tagreader import TagReader

class BadgerApp(ttk.Frame):
    def __init__(self, master=None, args=None):
        super().__init__(master)
        self.master = master
        self.pack()

        try:
            self.tagreader = TagReader(args.port)
        except:
            self.tagreader = None
            print("Couldn't open tag reader (did you specify the correct --port?)")

        nb = ttk.Notebook(self)
        nb.pack()

        self.event_add("<<Tag_Present>>", "None")
        self.bind('<<Tag_Present>>', self.handle_tag)

        namebadge_ui = NameBadgeUI(nb)
        trovelabel_ui = TroveLabelUI(nb)
        general_ui = GeneralLabelUI(nb)
        db_ui = DatabaseUI(nb)

        nb.add(namebadge_ui, text="Name Badge")
        nb.add(trovelabel_ui, text="Storage Label")
        nb.add(general_ui, text="General Label")
        nb.add(db_ui, text="Edit Tag")

        if self.tagreader:
            self.wait_for_tag_gone = None
            self.after(300, self.__check_for_tag)

    def __check_for_tag(self):
        tag = self.tagreader.read_tag()
        if tag:
            if tag == self.wait_for_tag_gone:
                self.after(300, self.__check_for_tag)
                return

            self.wait_for_tag_gone = tag
            self.event_generate("<<Tag_Present>>")
        else:
            self.wait_for_tag_gone = None

        self.after(300, self.__check_for_tag)

    def handle_tag(self, event):
        if not self.tagreader:
            return

        tag = self.tagreader.read_tag()
        if tag and tag == self.wait_for_tag_gone:
            print("Tag:", tag.hex())
