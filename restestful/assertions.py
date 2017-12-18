import json

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
	""" Handles the assertions of all tests

	Attributes:
		response: the response from the request that will be used in testing
	Todo:
		finish adding all the assertions and test them to make sure they
			all work
	"""
	def __init__(self, response):
		self.response = response

	def __parse_variables(self, test, key):
		if 'response' in test[key]:
			actual = self.response.json()
			for k in test[key]['response']:
				actual = actual[k]
		elif 'status_code' in test[key]:
			actual = self.response.status_code
		else:
			actual = test[key]
		return actual

	def __setup_assertion(self, test):
		expected = test['expected']
		actual = self.__parse_variables(test, 'actual')
		return {'expected':expected, 'actual':actual}

	def equal(self, test):
		setup = self.__setup_assertion(test)
		try:
			assert setup['expected'] == setup['actual']
			return True
		except:
			return False

	def notEqual(self, test):
		setup = self.__setup_assertion(test)
		try:
			assert setup['expected'] != setup['actual']
			return True
		except:
			return False

	def isTrue(self, test):
		pass

	def isFalse(self, test):
		pass

	def contain(self, test):
		setup = self.__setup_assertion(test)
		actual_json = json.dumps(setup['actual'])
		try:
			assert setup['expected'] in actual_json
			return True
		except:
			return False

	def notContain(self, test):
		setup = self.__setup_assertion(test)
		actual_json = json.dumps(setup['actual'])
		try:
			assert setup['expected'] not in actual_json
			return True
		except:
			return False

	def hasKey(self, test):
		pass

	def notHaveKey(self, test):
		pass

	def exist(self, test):
		pass

	def notExist(self, test):
		pass

	def greaterThan(self, test):
		pass

	def lessThan(self, test):
		pass




