import sublime_plugin
from .sublime_file import SublimeRequestFileParse
from . import restestful

class RunCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		srfp = SublimeRequestFileParse(self.view, edit)
		variables, restestful_requests = srfp.get_restestful_input()

		results = restestful.run(restestful_requests, variables)

		srfp.set_output(results)