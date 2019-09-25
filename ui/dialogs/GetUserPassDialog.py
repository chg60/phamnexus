from tkinter import *


class GetMySQLUserPassDialog(Toplevel):
    def __init__(self, controller, parent, title):
        # Initialize Toplevel window and mark it as belonging to controller
        Toplevel.__init__(self, parent)
        self.transient(parent)

        # Give the window a title if we were given one
        if title:
            self.title(title)

        # Persist a reference to the controller so we can give things back
        self.controller = controller
        self.parent = parent

        # Frame to hold username label and username entry widgets
        self.user_frame = Frame(master=self)
        self.user_label = Label(master=self.user_frame,
                                text="MySQL Username: ",
                                font=self.controller.font)
        self.user_label.pack(side=LEFT, anchor=W, expand=True, fill=None)
        self.user_entry = Entry(master=self.user_frame,
                                font=self.controller.font)
        self.user_entry.pack(side=LEFT, anchor=E, expand=True, fill=X)
        self.user_frame.pack(side=TOP, fill=X)

        # Frame to hold password label and password entry widgets
        self.pass_frame = Frame(master=self)
        self.pass_label = Label(master=self.pass_frame,
                                text="MySQL Password: ",
                                font=self.controller.font)
        self.pass_label.pack(side=LEFT, anchor=W, expand=True, fill=None)
        self.pass_entry = Entry(master=self.pass_frame,
                                show="*",
                                font=self.controller.font)
        self.pass_entry.pack(side=LEFT, anchor=E, expand=True, fill=X)
        self.pass_frame.pack(side=TOP, fill=X)

        # Frame to hold button widgets
        self.button_frame = Frame(master=self)
        self.ok_button = Button(master=self.button_frame,
                                text="Ok",
                                command=self.ok,
                                font=self.controller.font)
        self.ok_button.pack(side=LEFT, anchor=E, expand=True, fill=None)
        self.button_frame.pack(side=TOP, fill=X)

        # Make this window the focus
        self.grab_set()

        # Make user entry box the cursor focus
        self.user_entry.focus_set()

        # Hijack close button protocol
        self.protocol("WM_DELETE_WINDOW", self.ok)

        # Make application wait for this window
        self.wait_window(self)

    def ok(self):
        self.controller.admin_mysql.username = self.user_entry.get()
        self.controller.admin_mysql.password = self.pass_entry.get()
        self.destroy()
