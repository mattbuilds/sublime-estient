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
	def __init__(self, response):
		self.response = json.loads(response)
		pass

	def __parse_yaml_variables(self, test, key):
		try:
			actual = self.response[test[key]['response']]
		except:
			actual = test[key]
		return actual

	def __setup_assertion(self, test):
		expected = self.__parse_yaml_variables(test, 'expected')
		actual = self.__parse_yaml_variables(test, 'actual')
		return {'expected':expected, 'actual':actual}

	def equals(self, test):
		setup = self.__setup_assertion(test)
		try:
			assert setup['expected'] == setup['actual']
			return True
		except:
			return False

	def notEquals(self, test):
		setup = self.__setup_assertion(test)
		try:
			assert setup['expected'] != setup['actual']
			return True
		except:
			return False