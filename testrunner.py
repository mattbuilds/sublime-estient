import urllib.request
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
			request = self.set_environment_variables(request, variables)
			request['response'] = self.url_call(request['url'], request['method'])
			request['tests'] = self.__run_tests(request['tests'], request['response'])
			results.append(request)
		return results