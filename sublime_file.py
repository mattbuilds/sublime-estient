import sublime
import yaml
from collections import OrderedDict

def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

yaml.add_representer(OrderedDict, represent_ordereddict)

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

	def __dict_to_yaml(self, name, dictionary):
		request = {name:dictionary[name]}
		output = yaml.dump(request, default_flow_style=False)
		return output

	def get_environment_variables(self):
		return self.variables

	def get_requests(self):
		return self.requests

	def __request_file_write(self, file, key, dictionary):
		string = self.__dict_to_yaml(key, dictionary)
		file.insert(self.edit, file.size(), '    ' + string)

	def __handle_requests(self, requests):
		result = []
		for request in requests:
			ord_dict = OrderedDict()
			ord_dict['method'] = request['method']
			ord_dict['url'] = request['url']
			if 'body' in request:
				ord_dict['boyd'] = request['body']
			if 'tests' in request:
				ord_dict['tests'] = self.__handle_tests(request['tests'])
			ord_dict['output'] = {
				'status_code' : request['status_code'],
				'response' : request['response'],
				'headers' : request['headers']
			}
			result.append(ord_dict)
		return result
		
	def __handle_tests(self, tests):
		result = []
		for test in tests:
			ord_dict = OrderedDict()
			ord_dict['assert'] = test['assert']
			ord_dict['expected'] = test['expected']
			ord_dict['actual'] = test['actual']
			ord_dict['result'] = test['result']
			result.append(ord_dict)
		return result

	def output_file(self, output):
		file = self.view ##sublime.Window.new_file(self.view.window())
		#file.set_name("results.yaml")
		variables = self.__dict_to_yaml('variables', output)
		output['requests'] = self.__handle_requests(output['requests'])
		requests = self.__dict_to_yaml('requests', output)
		file.erase(self.edit, sublime.Region(0, file.size()))
		file.insert(self.edit, file.size(), variables)
		file.insert(self.edit, file.size(), '\n')
		file.insert(self.edit, file.size(), requests)

	def output_test_results(self, test_results, test_failures):
		file = sublime.Window.new_file(self.view.window())
		file.set_name("results.yaml")
		total = len(test_results)
		passes = test_results.count(True)
		if total == passes:
			file.insert(self.edit, file.size(), "All Tests Passed!\n")
		summary = "A total of %s out of %s tests passed\n" % (passes, total)
		file.insert(self.edit, file.size(), summary)

		if test_failures:
			file.insert(self.edit, file.size(), "\nList of Failures:\n")
			for failure in test_failures:
				file.insert(self.edit, file.size(), failure + "\n")