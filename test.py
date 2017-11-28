import sublime_plugin
from .sublime_file import SublimeRequestFileParse
from .testrunner import TestRunner

class RunCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		srfp = SublimeRequestFileParse(self.view, edit)
		test_runner = TestRunner()
		variables = srfp.get_environment_variables()
		http_reqs = srfp.get_requests()

		request_results = test_runner.execute(http_reqs, variables)
		test_results = test_runner.get_test_results()
		test_failures = test_runner.get_test_failures()

		results = {
			'variables': variables,
			'requests': request_results
		}

		srfp.output_file(results)
		srfp.output_test_results(test_results, test_failures)