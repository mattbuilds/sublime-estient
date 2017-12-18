import json
import requests
from .assertions import Assertions
from .rtf_request import RTFRequest

class TestRunner():
	""" A test runner for RESTful APIs

	Takes a list of http requests and runs them, then comapres the results to tests

	Attributes:
		test_results: a list of the results of all tests run from multiple requests
		test_failures: a list of all the tests that have failed
	Todo:
		* Add the ability to create a JSON and/or JUnit report
	""" 
	def __init__(self):
		self.test_results = []
		self.test_failures = []

	def __set_tests(self, test_results, test_failures):
		for test_result in test_results:
			self.test_results.append(test_result)
		for test_failure in test_failures:
			self.test_failures.append(test_failure)

	def get_test_failures(self):
		return self.test_failures

	def get_test_results(self):
		return self.test_results

	def execute(self, http_reqs, variables):
		results = []
		for request in http_reqs:
			try:
				req = RTFRequest(request)
			except Exception as e:
				print(e)

			req.set_environment_variables(variables)
			response = req.url_call()
			test_results, test_failures = req.run_tests()
			self.__set_tests(test_results, test_failures)
			variables = req.get_variables(variables)
			results.append(req.result)
		return results
