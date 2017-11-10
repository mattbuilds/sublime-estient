import sublime_plugin
from .sublime_file import SublimeRequestFileParse
from .testrunner import TestRunner

class RunCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		srfp = SublimeRequestFileParse(self.view, edit)
		variables = srfp.get_environment_variables()
		http_reqs = srfp.get_requests()

		request_results = TestRunner().execute(http_reqs, variables)

		results = {
			'variables': variables,
			'requests': request_results
		}

		srfp.output_file(results)