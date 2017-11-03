import sublime
import sublime_plugin
import urllib.request
import sys
#import requests

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

	def execute(self, http_reqs, variables):
		results = []
		for request in http_reqs:
			request = self.set_environment_variables(request, variables)
			results.append(
				self.url_call(request['url'], request['method'])
			)
		return results	

class SublimeRequestFileParse():
	""" The SublimRequestFileParser uses the sublime API to parse an existing file 
	into the type of data that can be used to send and run tests

	Attributes:
		regions: an array of all the different Regions (sublime api) 
		varaibles: a dict of of all the individual variables
		requests: a list of all the requests parsed from the file
	Todo:
		* Define a defintive way for the file to be written
		* Add the ability to send data
		* Add the ability to have tests for each request
	"""
	def get_initial_regions(view):
		variable_start = view.find("##Varaibles", 0)
		variable_end = view.find("##Request",0)
		split = {
			'variables' : sublime.Region(variable_start.b, variable_end.a),
			'http_reqs' : sublime.Region(variable_end.b, view.size())
		}
		return split

	def get_environment_variables(view, variables_region):
		lines = view.lines(variables_region)
		variables = {}
		for line in lines:
			try:
				variable = view.substr(line).split('=')
				if len(variable) == 2:
					variables[variable[0]] = variable[1]
			except:
				pass
		return variables

	def get_http_reqs(view, http_reqs_region):
		lines = view.lines(http_reqs_region)
		http_reqs = []
		for line in lines:
			if (line.b - line.a == 0):
				continue
			request = view.substr(line).split()
			if len(request) == 2:
				http_reqs.append({
					'method' : request[0],
					'url' : request[1]
				})
		return http_reqs

class HelloCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		file = self.view.lines(sublime.Region(0, self.view.size()))
		regions = SublimeRequestFileParse.get_initial_regions(self.view)
		variables = SublimeRequestFileParse.get_environment_variables(self.view, regions['variables'])
		http_reqs = SublimeRequestFileParse.get_http_reqs(self.view, regions['http_reqs'])

		results = TestRunner().execute(http_reqs, variables)

		new_file = sublime.Window.new_file(self.view.window())
		new_file.set_name("Test Results")
		for result in results:
			new_file.insert(edit, new_file.size(), result + "\n")
