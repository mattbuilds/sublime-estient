import sublime
import sublime_plugin
import urllib.request

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

def get_request(view, file):
	results = []
	for line in file:
		if (line.b - line.a == 0):
			continue
		request = view.substr(line).split()
		results.append(url_call(request[1], request[0]))
	return results

class HelloCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		file = self.view.lines(sublime.Region(0, self.view.size()))
		results = get_request(self.view, file)

		#result = url_call(base_url, 'GET')
		new_file = sublime.Window.new_file(self.view.window())
		new_file.set_name("Test Results")

		for result in results:
			new_file.insert(edit, new_file.size(), result + "\n")
		#self.view.insert(edit, 0, "Hello")
