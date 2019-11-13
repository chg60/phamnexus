from tkinter import *

from ui.frames.ChooseRunmode import ChooseRunmode
from ui.frames.ChooseDatabase import ChooseDatabase
from ui.frames.ChooseHost import ChooseHost
from ui.frames.ChooseCluster import ChooseCluster
from ui.frames.FinalizePhage import FinalizePhage


class MainWindow:
    def __init__(self, controller):
        self.controller = controller
        self.root = Tk()
        self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(
            file="img/icon.gif"))
        self.root.wm_title("PhamNexus")
        self.root.protocol("WM_DELETE_WINDOW", self.controller.quit)

        width, height = int(self.root.winfo_screenwidth()), \
                        int(self.root.winfo_screenheight())
        x_offset = int((self.root.winfo_screenwidth() - width) / 2)
        y_offset = int((self.root.winfo_screenheight() - height) / 2)

        self.root.wm_geometry("{}x{}+{}+{}".format(width, height, x_offset,
                                                   y_offset))

        # Create menu bar
        self.menu_bar = Menu(self.root, tearoff=0)
        self.root.config(menu=self.menu_bar)

        # Create file menu
        self.file = Menu(self.menu_bar, tearoff=0)
        # self.file.add_command(label="Preferences",
        # 					  font=controller.font,
        # 					  command=None)
        # self.controller.edit_preferences)
        # self.file.add_separator()
        self.file.add_command(label="Quit",
                              font=controller.font,
                              command=self.controller.quit)
        self.menu_bar.add_cascade(menu=self.file, label="File",
                                  font=controller.font)

        # Create help menu
        self.help = Menu(self.menu_bar, tearoff=0)
        self.help.add_command(label="Documentation",
                              font=controller.font,
                              command=self.controller.documentation)
        self.help.add_command(label="Report a Bug",
                              font=controller.font,
                              command=self.controller.report_bug)
        # self.help.add_command(label="Check for Updates",
        # 					  font=controller.font,
        # 					  command=self.controller.check_updates)
        self.menu_bar.add_cascade(menu=self.help, label="Help",
                                  font=controller.font)

        self.layout = ChooseRunmode(root=self.root, controller=self.controller)

    def redraw(self, frame):
        self.layout.destroy()
        if frame == 1:
            self.layout = ChooseRunmode(root=self.root,
                                        controller=self.controller)
        elif frame == 2:
            self.controller.get_mysql_dbs()
            self.layout = ChooseDatabase(root=self.root,
                                         controller=self.controller)
        elif frame == 3:
            self.layout = ChooseHost(root=self.root,
                                     controller=self.controller)
        elif frame == 4:
            self.layout = ChooseCluster(root=self.root,
                                        controller=self.controller)
        elif frame == 5 or frame == 6 or frame == 7:
            self.layout = FinalizePhage(root=self.root,
                                        controller=self.controller)

    def launch(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()
