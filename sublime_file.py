import sublime
import yaml
import json
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
		
	Todo:
		* Define a defintive way for the file to be written
		* Add the ability to have tests for each request
	"""
	def __init__(self, view, edit):
		self.view = view
		self.edit = edit
		info_dict = self.__parse_input()
		self.variables = info_dict['variables']
		self.requests = info_dict['requests']

	def __parse_input(self):
		region = self.view.substr(sublime.Region(0, self.view.size()))
		try:
			info_dict = json.loads(region)
			self.input = 'json'
		except ValueError as exc:
			info_dict = yaml.load(region)
			self.input = 'yaml'
		return info_dict

	def __dict_to_output(self, name, dictionary):
		if self.input == 'yaml':
			return self.__dict_to_yaml(name, dictionary)
		elif self.input == 'json':
			return self.__dict_to_json(name, dictionary)
		else:
			raise Exception("Input type was never set") 

	def __dict_to_yaml(self, name, dictionary):
		output = yaml.dump(dictionary, default_flow_style=False)
		return output

	def __dict_to_json(self, name, dictionary):
		output = json.dumps(dictionary, indent=4)
		return output

	def get_restestful_input(self):
		return self.variables, self.requests

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
				ord_dict['body'] = request['body']
			if 'headers' in request:
				ord_dict['headers'] = request['headers']
			if 'tests' in request:
				ord_dict['tests'] = self.__handle_tests(request['tests'])
			if 'variables' in request:
				ord_dict['variables'] = self.__handle_variables(request['variables'])
			ord_dict['output'] = request['output']
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

	def __variables_order_dict(self, variable):
		ord_dict = OrderedDict()
		ord_dict['name'] = variable['name']
		ord_dict['value'] = variable['value']
		return ord_dict

	def __handle_variables(self, variables):
		if type(variables) is list:
			result = []
			for variable in variables:
				result.append(self.__variables_order_dict(variable))
			return result
		else:
			return self.__variables_order_dict(variables)

	def set_output(self, results):
		self.__output_file(results['response'])
		self.__output_test_results(results['tests'], results['failures'])

	def __output_file(self, requests):
		file = self.view
		requests = self.__handle_requests(requests)
		output_dict = {
			'variables' : self.variables,
			'requests' : requests
		}
		output = self.__dict_to_output('requests', output_dict)
		file.erase(self.edit, sublime.Region(0, file.size()))
		file.insert(self.edit, file.size(), output)

	def __output_test_results(self, test_results, test_failures):
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