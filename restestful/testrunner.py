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

	def url_call(self, url, method='GET', data=None, user_headers=None):
		headers = {
			'Content-type' : 'application/json', 
			'Accept' : 'text/plain'
		}

		if user_headers is not None:
			headers.update(user_headers)
			
		if method == 'GET':
			response = requests.get(url, headers=headers)
		elif method == 'POST':
			response = requests.post(url, data=data, headers=headers)

		return response

	def __set_environment_variables(self, request, variables):
		for key, value in variables.items():
			request['url'] = request['url'].replace("{{" + key + "}}",str(value))
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

	def __get_variables(self, request_variables, variables, response):
		variable = response.json()
		for k in request_variables['value']['response']:
			variable= variable[k]
		variables[request_variables['name']] = variable
		return variables

	def __check_in_request(self, request, result, key):
		if key in request:
			result[key] = request[key]
		else:
			request[key] = None
		return result, request

	def get_test_failures(self):
		return self.test_failures

	def get_test_results(self):
		return self.test_results

	def execute(self, http_reqs, variables):
		results = []
		for request in http_reqs:
			print(variables)
			result = {
				'url':request['url'],
				'method':request['method']
			}

			result, request = self.__check_in_request(request, result, 'body')
			result, request = self.__check_in_request(request, result, 'headers')
			request = self.__set_environment_variables(request, variables)
			response = self.url_call(request['url'], request['method'], 
									 request['body'], request['headers'])
			
			if 'tests' in request:
				result['tests'] = self.__run_tests(request, request['tests'], response)
			
			if 'variables' in request:
				result['variables'] = request['variables']
				variables =  self.__get_variables(request['variables'], variables, response)

			result['output'] = {
				'status_code' : response.status_code,
				'response' : response.json(),
				'headers' : dict(response.headers)
			}
			results.append(result)
		return results