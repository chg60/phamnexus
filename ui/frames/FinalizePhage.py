from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo

import numpy as np

from data.constants import LABELS


class FinalizePhage(Frame):
    def __init__(self, root, controller):
        super(FinalizePhage, self).__init__(master=root)
        self.pack(expand=True, fill=BOTH)

        self.controller = controller
        self.root = root

        # Get selection data from
        self.runmode = self.controller.runmode
        self.status = self.controller.exclude_draft

        self.metadata = controller.metadata
        self.phages = controller.available_phages
        self.hosts = controller.available_hosts
        self.clusters = controller.available_clusters

        # List of ways that the PhageIDs can be sorted
        self.sort_mode = IntVar()
        self.sort_mode.set(value=0)
        self.append_cluster = IntVar()
        self.append_cluster.set(value=0)
        self.labels = LABELS["PhageFrame"]

        # Viewer frame to hold all runmode-specific widgets - layout is
        # pretty much the same regardless of runmode, but what changes
        # are the pre-selected phages and how those are selected.
        self.viewer = Frame(self)

        # Instruction frame to hold the runmode-specific instructions
        self.instruct_frame = Frame(master=self.viewer)
        self.instruct_label = Label(self.instruct_frame,
                                    text=self.labels["Instruct"][self.runmode],
                                    font=controller.font)

        self.instruct_label.pack(side=LEFT, anchor=NW, fill=None, expand=True)
        self.instruct_frame.pack(side=TOP, anchor=NW, fill=X, expand=True)

        # Sort frame to hold the sorting options
        self.sort_frame = Frame(master=self.viewer)

        for i in range(len(self.labels["Sort"])):
            radio = Radiobutton(master=self.sort_frame,
                                variable=self.sort_mode,
                                value=i,
                                font=controller.font,
                                text=self.labels["Sort"][i])
            radio.pack(side=TOP, anchor=W, fill=None, expand=True)

        sort_button = Button(master=self.sort_frame,
                             font=controller.font,
                             text="Sort",
                             command=lambda: self.sort(
                                 mode=self.sort_mode.get()))
        sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
        self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

        # Selection frame to hold all widgets for selecting and de-selecting
        # phages for phamnexus-ing
        self.select_frame = Frame(master=self.viewer)

        # Left listbox to display phages available for selection
        self.avail_frame = Frame(master=self.select_frame)
        self.avail_label = Label(master=self.avail_frame,
                                 font=controller.font,
                                 text="Available Phages")
        self.avail_label.pack(side=TOP, anchor=N, fill=None, expand=True)
        self.avail_list = Listbox(master=self.avail_frame,
                                  width=50, height=25,
                                  font=controller.font,
                                  selectmode=EXTENDED)

        self.avail_list.pack(side=LEFT, anchor=N, fill=None, expand=True)
        self.avail_frame.pack(side=LEFT, anchor=N, fill=None, expand=True)

        # Middle button frame to add/remove phages to/from selection listbox
        self.sel_button_frame = Frame(master=self.select_frame)
        self.add_button = Button(master=self.sel_button_frame,
                                 font=controller.font,
                                 text="Add to Selection >>",
                                 command=self.add)
        self.add_button.pack(side=TOP, anchor=CENTER, fill=None, expand=True)
        self.rem_button = Button(master=self.sel_button_frame,
                                 font=controller.font,
                                 text="<< Remove from Selection",
                                 command=self.remove)
        self.rem_button.pack(side=TOP, anchor=CENTER, fill=None, expand=True)
        self.sel_button_frame.pack(side=LEFT, anchor=CENTER,
                                   fill=None, expand=True)

        # Right listbox to display phages that have been selected
        self.chose_frame = Frame(master=self.select_frame)
        self.chose_label = Label(master=self.chose_frame,
                                 font=controller.font,
                                 text="Selected Phages")
        self.chose_label.pack(side=TOP, anchor=N, fill=None, expand=True)

        self.chose_list = Listbox(master=self.chose_frame,
                                  width=50, height=25,
                                  font=controller.font,
                                  selectmode=EXTENDED)
        self.chose_list.pack(side=LEFT, anchor=N, fill=None, expand=True)
        self.chose_frame.pack(side=LEFT, anchor=N, fill=None, expand=True)
        self.select_frame.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=True)

        # Frame to hold checkbox to append subcluster to phage name in nexus
        # file
        self.checkbutton_frame = Frame(master=self.viewer)
        self.checkbutton = Checkbutton(self.checkbutton_frame,
                                       font=controller.font,
                                       text="Append cluster to phage name?",
                                       variable=self.append_cluster)
        self.checkbutton.pack(side=TOP, anchor=NW, fill=None, expand=True)
        self.checkbutton_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

        # Bottom button frame to store back/make nexus buttons
        self.main_button_frame = Frame(master=self.viewer)
        self.back_button = Button(self.main_button_frame,
                                  font=controller.font,
                                  text="Back",
                                  command=self.back)
        self.back_button.pack(side=LEFT, anchor=SW, fill=None, expand=True)

        self.next_button = Button(self.main_button_frame,
                                  font=controller.font,
                                  text="Make Nexus File",
                                  command=self.make_nexus)
        self.next_button.pack(side=LEFT, anchor=SE, fill=None, expand=True)

        # Pack main button frame
        self.main_button_frame.pack(side=BOTTOM, anchor=S, fill=X, expand=True)

        # Pack main viewer frame
        self.viewer.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=True)

        # Populate available and pre-selected lists
        self.populate_available()
        self.populate_chosen()

    def populate_available(self):
        """

        :return:
        """
        for phage in self.metadata:
            phageid = phage["PhageID"].decode("utf-8")
            host = phage["HostGenus"].decode("utf-8")
            cluster = phage["Cluster"].decode("utf-8")
            status = phage["Status"].decode("utf-8")
            add = "\t({}, {}, {})".format(host, cluster, status)
            display = "".join(["{:<20}".format(phageid), add])
            self.avail_list.insert(END, display)

    def populate_chosen(self):
        """
        Decides which phages to pre-insert into the selected frame on
        the basis of prior user-selections and the current runmode.
        :return:
        """
        # List to store the phage selection
        pre_selected_phages = list()

        # Filter phages available for pre-selection to those that meet status
        # specifications
        if self.status == 1:
            status = "draft".encode('utf-8')
            filtered_phages = self.metadata[self.metadata["Status"] != status]
        else:
            filtered_phages = self.metadata

        # Runmode 0 bases pre-selection on Host
        if self.runmode == 0:
            print("Choosing phages based on hosts")
            # Get host selection from the controller
            chosen_hosts = self.controller.selected_hosts
            # Convert chosen_hosts to bytes strings
            chosen_hosts = [host.encode('utf-8') for host in chosen_hosts]

            # Iterate through selected hosts
            for host in chosen_hosts:
                # Subset the array based on current host selection
                phages = filtered_phages[filtered_phages["HostGenus"] == host]
                # Add those phages to the pre-selection
                for phage in phages:
                    phageid = phage["PhageID"].decode('utf-8')
                    pre_selected_phages.append(phageid)

        # Runmode 1 bases pre-selection on Cluster
        elif self.runmode == 1:
            # Get cluster selection from the controller
            chosen_clusters = self.controller.selected_clusters
            # Convert chosen_clusters to bytes strings
            chosen_clusters = [cluster.encode('utf-8') for cluster in
                               chosen_clusters]

            # Iterate through selected clusters
            for cluster in chosen_clusters:
                # Subset the array based on current cluster selection
                phages = filtered_phages[filtered_phages["Cluster"] == cluster]
                # Add those phages to the pre-selection
                for phage in phages:
                    phageid = phage["PhageID"].decode('utf-8')
                    pre_selected_phages.append(phageid)

        # Runmode 2 has no pre-selection
        elif self.runmode == 2:
            print("Choosing no phages")
            pass
        
        # Runmode 3 chooses all phages
        elif self.runmode == 3:
            print("Choosing all phages")
            # "Subset" to all phages
            phages = filtered_phages
            # Add those phages to the pre-selection
            for phage in phages:
                phageid = phage["PhageID"].decode('utf-8')
                pre_selected_phages.append(phageid)

        # Runmode 4 randomly selects phages, respecting Status selection
        else:
            print("Choosing random phages")
            # All available sub-clusters
            subclusters = list(set([subcluster.decode("utf-8") for subcluster
                               in filtered_phages['Cluster']]))
            for subcluster in sorted(subclusters):
                all_members = filtered_phages[filtered_phages["Cluster"] ==
                                              subcluster.encode("utf-8")]
                if subcluster[-1].isdigit():
                    # Found a subcluster - grab first member
                    phageid = all_members[0]["PhageID"].decode("utf-8")
                    pre_selected_phages.append(phageid)
                    print("Grabbed {} from {}".format(phageid, subcluster))
                else:
                    # Found a candidate for non-subclustered genomes
                    if (subcluster + "1" in subclusters) or \
                            (subcluster == "Singleton") or \
                            (subcluster == "UNK"):
                        # If other subclusters exist, definitely found
                        # non-subclustered genomes - take all
                        for phage in all_members:
                            phageid = phage["PhageID"].decode("utf-8")
                            pre_selected_phages.append(phageid)
                        print("Grabbed all members from {}".format(subcluster))
                    else:
                        # Just another subcluster
                        phageid = all_members[0]["PhageID"].decode("utf-8")
                        pre_selected_phages.append(phageid)
                        print("Grabbed {} from {}".format(phageid, subcluster))

        # Populate pre-selected phages into chose_list
        print("Chose {} phages".format(len(pre_selected_phages)))
        for phage in pre_selected_phages:
            data = self.metadata[self.metadata["PhageID"] ==
                                 phage.encode('utf-8')]
            host = data['HostGenus'][0].decode('utf-8')
            cluster = data['Cluster'][0].decode('utf-8')
            status = data['Status'][0].decode('utf-8')
            add = "\t({}, {}, {})".format(host, cluster, status)
            display = "".join(["{:<20}".format(phage), "{:<40}".format(
                add)])
            self.chose_list.insert(END, display)

    def sort(self, mode):
        # Empty the available list
        self.avail_list.delete(0, END)

        # Get selected list and then empty it
        selected_phages = list()
        selection = self.chose_list.get(0, END)
        for select in selection:
            selected_phages.append(select.split()[0])
        self.chose_list.delete(0, END)

        # Sort by PhageID
        if mode == 0:
            self.metadata = np.sort(self.metadata,
                                    order=["PhageID"],
                                    kind="mergesort")

        # Sort by HostStrain, then PhageID
        elif mode == 1:
            self.metadata = np.sort(self.metadata,
                                    order=["HostGenus", "PhageID"],
                                    kind="mergesort")

        # Sort by Cluster, then PhageID
        elif mode == 2:
            self.metadata = np.sort(self.metadata,
                                    order=["Cluster", "HostGenus", "PhageID"],
                                    kind="mergesort")

        self.phages = list(self.metadata["PhageID"])
        self.phages = [phage.decode('utf-8') for phage in self.phages]

        for phage in self.metadata:
            phageid = phage["PhageID"].decode('utf-8')
            host = phage["HostGenus"].decode('utf-8')
            cluster = phage["Cluster"].decode('utf-8')
            status = phage["Status"].decode('utf-8')
            add = "\t({}, {}, {})".format(host, cluster, status)
            display = "".join(["{:<20}".format(phageid), "{:<40}".format(
                add)])
            self.avail_list.insert(END, display)

            if phageid in selected_phages:
                self.chose_list.insert(END, display)

    def add(self):
        sel = self.avail_list.curselection()
        for i in sel:
            add_name = self.phages[i]
            print(i, add_name)
            if add_name not in self.chose_list.get(0, END):
                data = self.metadata[self.metadata["PhageID"] ==
                                     add_name.encode('utf-8')]
                host = data["HostGenus"][0].decode('utf-8')
                cluster = data["Cluster"][0].decode('utf-8')
                status = data["Status"][0].decode('utf-8')
                add = "\t({}, {}, {})".format(host, cluster, status)
                display = "".join(["{:<20}".format(add_name), "{:<40}".format(
                    add)])
                self.chose_list.insert(END, display)
        return

    def remove(self):
        sel = self.chose_list.curselection()
        # need to delete in reverse order because indices shift otherwise
        for i in list(reversed(sel)):
            self.chose_list.delete(i)

    def back(self):
        if self.runmode < 2:
            self.controller.redraw_window(frame=int(2 + self.runmode))
        else:
            self.controller.redraw_window(frame=2)

    def make_nexus(self):
        selection = self.chose_list.get(0, END)
        selection = [select.split()[0] for select in selection]
        result = asksaveasfilename(initialdir="~",
                                   title="Choose save filename",
                                   filetypes=(("Nexus", "*.nex *.nxs "
                                                        "*.nexus"),))
        self.root.update()
        if len(result) == 0 or result == "":
            showinfo(message="Program can't continue without a save "
                             "filename. Please click 'Make Nexus File' "
                             "again, and this time indicate a save filename.")
            return

        self.controller.selected_phages = list(selection)
        self.controller.append_cluster = self.append_cluster.get()
        self.controller.make_nexus(filename=result)
        self.controller.redraw_window(frame=1)
