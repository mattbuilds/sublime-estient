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
	def url_call(self, url, method='GET', data=None):
		headers = {
			'Content-type' : 'application/json', 
			'Accept' : 'text/plain'
		}

		if method == 'GET':
			response = requests.get(url)
		elif method == 'POST':
			response = requests.post(url, data=data)

		print(response.json())

		return response.json()

	def __json_to_dict(self, response):
		return json.loads(response)

	def __dict_to_json(self, response):
		return json.dumps(response)

	def set_environment_variables(self, request, variables):
		for key, value in variables.items():
			request['url'] = request['url'].replace("{{" + key + "}}",value)
		return request

	def __run_tests(self, tests, response):
		assertions = Assertions(response)
		response = []
		for test in tests:
			assertion = getattr(assertions, test['assert'])
			test['result'] = assertion(test)
			response.append(test)
		return response


	def execute(self, http_reqs, variables):
		results = []
		for request in http_reqs:
			result = {
				'url':request['url'],
				'method':request['method']
			}

			if 'body' in request:
				result['body'] = request['body']
				request = self.set_environment_variables(request, variables)
				response = self.url_call(request['url'], request['method'], request['body'])
			else:
				request = self.set_environment_variables(request, variables)
				response = self.url_call(request['url'], request['method'])
			
			
			if 'tests' in request:
				result['tests'] = self.__run_tests(request['tests'], response)
			result['response'] = self.__dict_to_json(response)
			results.append(result)
		return results