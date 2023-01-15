#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from db import Database
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

        if args.database:
            try:
                self.db = Database(args.database)
            except:
                self.db = None
                print("Couldn't open database")
        else:
            self.db = None

        self.nb = ttk.Notebook(self)
        self.nb.pack()

        self.event_add("<<Tag_Present>>", "None")
        self.bind('<<Tag_Present>>', self.handle_tag)

        self.namebadge_ui = NameBadgeUI(self.nb)
        self.trovelabel_ui = TroveLabelUI(self.nb)
        self.general_ui = GeneralLabelUI(self.nb)
        self.db_ui = DatabaseUI(self.nb, self.db)

        self.nb.add(self.namebadge_ui, text="Name Badge")
        self.nb.add(self.trovelabel_ui, text="Storage Label")
        self.nb.add(self.general_ui, text="General Label")
        self.nb.add(self.db_ui, text="Edit Tag")

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
            buttons = self.tagreader.read_buttons()
            print("Tag:", tag.hex())
            print("Buttons:", buttons)

            # Special case the "General" tag
            if tag.hex() == "4777701c":
                self.general_ui.reset()
                self.namebadge_ui.reset()
                self.trovelabel_ui.reset()
                self.db_ui.reset()
                self.nb.select(self.general_ui)
                return

            # All other tags can only be handled if we have a database
            if not self.db:
                return

            try:
                name, comment = self.db.lookup(tag)
                print(name, comment)
            except Exception as e:
                print("Tag not in database, enrol it", e)
                self.db_ui.populate(tag, "Your Name", "Your Comment")
                self.nb.select(self.db_ui)
                return

            self.namebadge_ui.populate(name, comment)
            self.trovelabel_ui.populate(name, comment)
            # Clear out the db_ui always, so someone else's tag isn't loaded
            self.db_ui.reset()

            if buttons == 0:
                self.nb.select(self.namebadge_ui)
            elif buttons == 1:
                self.db_ui.populate(tag, name, comment)
                self.nb.select(self.db_ui)
            elif buttons == 2:
                self.nb.select(self.trovelabel_ui)
