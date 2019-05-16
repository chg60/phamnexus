from tkinter import *


class GetMySQLUserPassDialog(Toplevel):
	def __init__(self, controller):
		super(GetMySQLUserPassDialog, self).__init__(master=None)
		self.title("Enter MySQL Credentials")
		x_offset = int(self.winfo_screenwidth() / 3)
		y_offset = int(self.winfo_screenheight() / 3)
		self.geometry("+{}+{}".format(x_offset, y_offset))
		self.focus_set()

		self.controller = controller

		self.user_frame = Frame(master=self)
		self.user_label = Label(master=self.user_frame, text="Admin "
															 "Username: ",
								font=("TkDefaultFont", 12))
		self.user_label.pack(side=LEFT, anchor=W, expand=True, fill=None)
		self.user_entry = Entry(master=self.user_frame,
								font=("TkDefaultFont", 12))
		self.user_entry.pack(side=LEFT, anchor=E, expand=True, fill=X)
		self.user_frame.pack(side=TOP, fill=X)

		self.pass_frame = Frame(master=self)
		self.pass_label = Label(master=self.pass_frame, text="Admin "
															 "Password: ",
								font=("TkDefaultFont", 12))
		self.pass_label.pack(side=LEFT, anchor=W, expand=True, fill=None)
		self.pass_entry = Entry(master=self.pass_frame, show="*",
								font=("TkDefaultFont", 12))
		self.pass_entry.pack(side=LEFT, anchor=E, expand=True, fill=X)
		self.pass_frame.pack(side=TOP, fill=X)

		self.button_frame = Frame(master=self)
		self.ok_button = Button(master=self.button_frame, text="Ok",
								command=self.on_ok_click,
								font=("TkDefaultFont", 12))
		self.ok_button.pack(side=LEFT, anchor=E, expand=True, fill=None)
		self.button_frame.pack(side=TOP, fill=X)

	def on_ok_click(self):
		username = self.user_entry.get()
		password = self.pass_entry.get()
		if username == "":
			username = None
		if password == "":
			password = None
		self.destroy()
		# print(username, password)
		self.controller.username = username
		self.controller.password = password
		return
