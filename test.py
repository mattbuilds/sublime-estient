import sublime
import sublime_plugin
import urllib.request

base_url = "http://matt.duchamp/mastermind/accountRead/DEMO1018?login=aff_admin&secret=affuser"

def url_call(url, method='GET', data=None):
	try:
		request = urllib.request.Request(
			url=url,
			method=method,
			data = data)
		response =  urllib.request.urlopen(request)
		return response.read().decode('utf-8')
	except:
		print("Failure")

class HelloCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		print(view.substr(sublime.Region(0, view.size())))

		result = url_call(base_url, 'GET')
		file = sublime.Window.new_file(self.view.window())
		file.set_name("Test Results")
		file.insert(edit,0,result)
		#self.view.insert(edit, 0, result)
