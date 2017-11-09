import sublime
import sublime_plugin
import urllib.request
import sys
import json
import re
import yaml
#import requests

"""
A List of assertions
assertEquals
assertNotEquals
assertTrue
assertFalse
assertIs
assertIsNot
assertIsNone
assertIsNotNone
assertIn
assertNotIn
"""

class Assertions():
	def __init__(self):
		pass

	def __parse_response_regex(self, actual):
		pass

	def equals(self, test, response):
		self.__parse_response_regex(test['actual'])
		pass

	def assertEquals(response, assertion):
		try:
			response_regex = "\['(.*?)'\]"
			paramater_str = re.search('assertEquals\((.*)\)',assertion).group(1)
			# if response loop through and get all keys
		except:
			pass

		# try:
		# 	assert a == b
		# except:
		# 	print(a + " does not equal " + b)

class TestRunner():
	""" A test runner for RESTful APIs

	Takes a list of http requests and runs them, then comapres the results to tests

	Attributes:
		requests: a list of http requests to run, each test will include a URL, mthod, and data
		varaibles: a dict of environment variables that can replace anything in the tests
	Todo:
		* Add the ability to create a JSON and/or JUnit report
	"""
	def url_call(self, url, method='GET', data=None):
		try:
			request = urllib.request.Request(
				url=url,
				method=method,
				data = data)
			response =  urllib.request.urlopen(request)
			return response.read().decode('utf-8')
		except:
			print("Failure")

	def set_environment_variables(self, request, variables):
		for key, value in variables.items():
			request['url'] = request['url'].replace("{{" + key + "}}",value)
		return request

	def check_assertion(self, response, assertion):
		response = json.loads(response)
		regex = "\(.*\)"
		assertion_name = re.sub(regex, '', assertion)
		func = getattr(Assertions, assertion_name)
		func(response, assertion)
		#except:
			#print("Not a Valid Assertion Type")

	def __run_tests(self, tests, response):
		assertions = Assertions()
		for test in tests:
			assertions.equals(test, response)
			

	def execute(self, http_reqs, variables):
		results = []
		for request in http_reqs:
			request = self.set_environment_variables(request, variables)
			response = self.url_call(request['url'], request['method'])
			self.__run_tests(request['tests'], response)
			results.append(response)

		return results	

class SublimeRequestFileParse():
	""" The SublimRequestFileParser uses the sublime API to parse an existing file 
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
		print(info_dict)
		return info_dict

	def get_environment_variables(self):
		return self.variables

	def get_requests(self):
		return self.requests

	def output_file(self, output):
		file = sublime.Window.new_file(self.view.window())
		file.set_name("Test Results")
		for test in output:
			file.insert(self.edit, file.size(), test +"\n")


class RunCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		srfp = SublimeRequestFileParse(self.view, edit)
		variables = srfp.get_environment_variables()
		http_reqs = srfp.get_requests()

		print(variables)
		print(http_reqs)

		results = TestRunner().execute(http_reqs, variables)

		srfp.output_file(results)