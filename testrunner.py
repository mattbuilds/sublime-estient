import urllib.request
import json
import requests
from .assertions import Assertions


class TestRunner():
	""" A test runner for RESTful APIs

	Takes a list of http requests and runs them, then comapres the results to tests

	Attributes:
		requests: a list of http requests to run, each test will include a URL, mthod, and data
		varaibles: a dict of environment variables that can replace anything in the tests
	Todo:
		* Add the ability to create a JSON and/or JUnit report
	""" 
	def __init__(self):
		self.test_results = []
		self.test_failures = []

	def url_call(self, url, method='GET', data=None, headers=None):
		default_headers = {
			'Content-type' : 'application/json', 
			'Accept' : 'text/plain'
		}

		if headers is None:
			headers = default_headers

		if method == 'GET':
			response = requests.get(url, headers=headers)
		elif method == 'POST':
			response = requests.post(url, data=data, headers=headers)

		return response

	def __json_to_dict(self, response):
		return json.loads(response)

	def __dict_to_json(self, response):
		return json.dumps(response)

	def __set_environment_variables(self, request, variables):
		for key, value in variables.items():
			request['url'] = request['url'].replace("{{" + key + "}}",value)
		return request

	def __run_tests(self, request, tests, response):
		assertions = Assertions(response)
		response = []
		for test in tests:
			assertion = getattr(assertions, test['assert'])
			test['result'] = assertion(test)
			self.__set_test_result(test['result'])
			if test['result'] != True:
				failure_string = request['method'] + " " + request['url']
				self.__set_test_failures(failure_string)
			response.append(test)
		return response

	def __set_test_failures(self, failure_string):
		self.test_failures.append(failure_string)

	def __set_test_result(self, result):
		self.test_results.append(result)

	def get_test_failures(self):
		return self.test_failures

	def get_test_results(self):
		return self.test_results

	def execute(self, http_reqs, variables):
		results = []
		for request in http_reqs:
			result = {
				'url':request['url'],
				'method':request['method']
			}

			if 'body' in request:
				result['body'] = request['body']
			else:
				request['body'] = None
			request = self.__set_environment_variables(request, variables)
			response = self.url_call(request['url'], request['method'], request['body'])
			
			if 'tests' in request:
				result['tests'] = self.__run_tests(request, request['tests'], response)
			result['status_code'] = response.status_code
			result['response'] = self.__dict_to_json(response.json())
			result['headers'] = dict(response.headers)
			results.append(result)
		return results