class RTFRequest():
	def __init__(self, request):
		self.required_arguments = ('method', 'url')
		self.optional_arguments = ('body', 'headers', 'tests', 'variables')
		self.__set_required_arguments(request, self.required_arguments)
		self.__set_optional_arguments(request, self.optional_arguments)
		self.initial = self

	def __set_required_arguments(self, request, keys):
		for key in keys:
			if key in request:
				setattr(self, key, request[key])
			else:
				raise Exception("%s is a required field." % key)

	def __set_optional_arguments(self, request, keys):
		for key in keys:
			if key in request:
				setattr(self, key, request[key])