import multiprocessing


class NexusHandler:
	def __init__(self, dictionary, all_phams, filename):
		self.dictionary = dictionary
		self.all_phams = all_phams
		self.filename = filename

		self.task_queue = list()
		self.done_queue = multiprocessing.Manager().Queue()
		self.done_list = list()

	def create_queue(self):
		for phageid in self.dictionary.keys():
			task = [phageid, self.dictionary[phageid], self.all_phams]
			self.task_queue.append(task)

	def create_nexus_string(self, task):
		nexus_list = []
		phageid = task[0]
		phams = task[1]
		phams_to_search = task[2]
		for pham in phams_to_search:
			if pham in phams:
				nexus_list.append("1")
			else:
				nexus_list.append("0")
		nexus_string = "".join(nexus_list)
		self.done_queue.put([phageid, nexus_string])

	def write_nexus_file(self):
		self.create_queue()
		available_cpus = multiprocessing.cpu_count()
		print("Using {} cpus".format(available_cpus))
		with multiprocessing.Pool(available_cpus) as p:
			p.map(self.create_nexus_string, self.task_queue)

		while not self.done_queue.empty():
			done_task = self.done_queue.get()
			self.done_list.append(done_task)

		print("Nexus strings done")
		# Create the nexus file.
		f = open(self.filename, "w")

		# Write out header information.
		f.write("#NEXUS\n")
		f.write("BEGIN TAXA;\n")
		f.write("\tdimensions ntax={};\n".format(len(self.dictionary.keys())))
		f.write("\ttaxlabels {};\n".format(" ".join([phage[0] for phage in
													 self.done_list])))
		f.write("END;\n")
		f.write("BEGIN CHARACTERS;\n")
		f.write("\tdimensions nchar={};\n".format(len(self.all_phams)))
		f.write("\tformat datatype=standard missing=? gap=- matchchar=. "
				"interleave;\n")
		f.write("\tmatrix\n")

		indices = range(0, len(self.all_phams), 100)
		# print(indices[0:])
		for i in range(len(indices)-1):
			start = indices[i]
			end = indices[i+1]
			for phage in self.done_list:
				phageid = phage[0]
				string = phage[1][start:end]
				line = '{:<27}\t{:>100}\n'.format(phageid, string)
				f.write(line)
			f.write("\n")
		start = indices[-1]

		for phage in self.done_list:
			phageid = phage[0]
			string = phage[1][start:]
			line = '{:<27}\t{}\n'.format(phageid, string)
			f.write(line)
		f.write("\n;\nend;\n")
		f.close()
		print("Done writing file")
