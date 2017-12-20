import json
import requests
from .assertions import Assertions

class RTFRequest():
	""" The RFTRequest clas is used to create and execute RESTFul APi
	requests

	Attributes:
		required_arguments: a list of the arguments that are required to
			make a request
		optional_arguments: a list of the arguments that are optional but
			can be included in a request
		request: the object that will be used to create the http request
			made up of required_arguments and optional_arguments
		result: the result of a request that will be returned. Includes
			the original request
	"""
	def __init__(self, request):
		self.required_arguments = ('method', 'url')
		self.optional_arguments = ('body', 'headers', 'tests', 'variables')
		self.result = {}
		self.__set_attributes(request, self.required_arguments, True)
		self.__set_attributes(request, self.optional_arguments, False)

	def set_environment_variables(self, variables):
		""" Sets the environement varaibles before the request
		Args:
			variables: a dictionary of what to look for and replace
		"""
		for key, value in variables.items():
			for arg in self.result:
				argument = getattr(self, arg)
				arg_value = self.__replace_argument(argument, key, value)
				setattr(self, arg, arg_value)

	def __replace_argument(self, argument, key, value):
		""" Checks if an object is a string and if so replaces the key and
		value if it exists. If not a string, drill down until we hit a string 
		otherwise just return the value

		Todo:
			Find a way to preserve type of value (ex boolean or int instead
			of always making it a string)
		"""
		if isinstance(argument, str):
			return argument.replace("{{" + key + "}}",str(value))
		elif type(argument) is list or type(argument) is tuple:
			for idx, item in enumerate(argument):
				argument[idx] = self.__replace_argument(item, key, value)
			return argument
		elif type(argument) is dict:
			for idx, item in argument.items():
				argument[idx] = self.__replace_argument(item, key, value)
			return argument
		else:
			return argument

	def url_call(self):
		"""Make the RESTFul Request"""
		self.headers.setdefault('Content-type', 'application/json')
		self.headers.setdefault('Accept', 'text/plain')
			
		if self.method == 'GET':
			response = requests.get(self.url, headers=self.headers)
		elif self.method == 'POST':
			response = requests.post(self.url, data=self.data, headers=self.headers)
		self.response = response
		self.__set_output()

	def run_tests(self):
		"""Runs the tests."""
		assertions = Assertions(self.response)
		updated_tests = []
		test_results = []
		test_failures = []

		for test in self.tests:
			assertion = getattr(assertions, test['assert'])
			test['result'] = assertion(test)
			if test['result'] != True:
				failure_string = self.method + " " + self.url
				test_results.append(failure_string)
			test_results.append(test['result'])
			updated_tests.append(test)
		self.tests = updated_tests
		return test_results, test_failures

	def get_variables(self, variables):
		""" Add variables from response to dictionary of environment 
			variables
		Args:
			variables: existing dictionary of environment variables

		Returns:
			an updated variables dictionary
		"""
		if not hasattr(self, 'variables'):
			pass
		else:
			variable = self.response.json()
			for request_variable in self.variables:
				for k in request_variable['value']['response']:
					variable= variable[k]
				variables[request_variable['name']] = variable
		return variables

	def __set_output(self):
		""" Sets the output of request"""
		self.result['output'] = {
			'status_code' : self.response.status_code,
			'response' : self.response.json(),
			'headers' : dict(self.response.headers)
		}

	def __set_attributes(self, request, keys, required = False):
		""" Sets request values into object and set
		Args:
			request: the incoming request
			keys: a list of keys to match
			required: if the keys are required values
		"""
		for key in keys:
			if key in request:
				setattr(self, key, request[key])
				self.result[key] = request[key]
			else:
				if required:
					raise Exception("%s is a required field." % key)

