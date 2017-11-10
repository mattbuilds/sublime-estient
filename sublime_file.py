import sublime
import yaml

class SublimeRequestFileParse():
	""" The SublimeRequestFileParse uses the sublime API to parse an existing file 
	into the type of data that can be used to send and run tests

	Attributes:
		view: a sublime.View object of your current view
		edit: a sublime edit object used for outputing a file
		variables: a region that is created fom the variables in the file
		requests: a region that is created for the requests in the file
		regions: an array of all the different Regions (sublime api)
			right now that is just variables and requests
	Todo:
		* Define a defintive way for the file to be written
		* Add the ability to send data
		* Add the ability to have tests for each request
	"""
	def __init__(self, view, edit):
		self.view = view
		self.edit = edit
		info_dict = self.__parse_yaml()
		self.variables = info_dict['variables']
		self.requests = info_dict['requests']

	def __parse_yaml(self):
		region = self.view.substr(sublime.Region(0, self.view.size()))
		info_dict = yaml.load(region)
		return info_dict

	def __dict_to_yaml(self, dictionary):
		output = yaml.dump(dictionary, default_flow_style=False)
		return output

	def get_environment_variables(self):
		return self.variables

	def get_requests(self):
		return self.requests

	def output_file(self, output):
		file = sublime.Window.new_file(self.view.window())
		file.set_name("results.yaml")
		result = self.__dict_to_yaml(output)
		file.insert(self.edit, file.size(), result)
		#for test in output:
		#	file.insert(self.edit, file.size(), test +"\n")