import sublime
import sublime_plugin
import urllib.request
import sys
import json
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

	def check_assertion(self, response, assertion):
		response = json.loads(response)
		try:
			exec(assertion)
		except:
			print("It Failed")

	def execute(self, http_reqs, variables):
		results = []
		for request in http_reqs:
			request = self.set_environment_variables(request, variables)
			results.append(
				self.url_call(request['url'], request['method'])
			)
			for assertion in request['assertions']:
				self.check_assertion(results[-1], assertion)
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
		variable_start = self.view.find("##Varaibles", 0)
		variable_end = self.view.find("##Request",0)
		self.variables = sublime.Region(variable_start.b, variable_end.a)
		self.requests = sublime.Region(variable_end.b, view.size())

	def get_environment_variables(self):
		lines = self.view.lines(self.variables)
		variables = {}
		for line in lines:
			try:
				variable = self.view.substr(line).split('=')
				if len(variable) == 2:
					variables[variable[0]] = variable[1]
			except:
				pass
		return variables

	def get_requests(self):
		lines = self.view.lines(self.requests)
		http_reqs = []
		for line in lines:
			if (line.b - line.a == 0):
				continue
			if 'assert' in self.view.substr(line):
				http_reqs[-1]['assertions'].append(self.view.substr(line))
			else:
				request = self.view.substr(line).split()
				if len(request) == 2:
					http_reqs.append({
						'method' : request[0],
						'url' : request[1],
						'assertions' : []
					})
		return http_reqs

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

		results = TestRunner().execute(http_reqs, variables)

		srfp.output_file(results)