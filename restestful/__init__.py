from .testrunner import TestRunner

def run(http_reqs, variables):
	runner = TestRunner()
	request_results = runner.execute(http_reqs, variables)
	test_results = runner.get_test_results()
	test_failures = runner.get_test_failures()

	return {
		'response': request_results,
		'tests': test_results,
		'failures': test_failures
	}