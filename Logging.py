
from GulpServer.Settings import Settings



user_settings = None



def plugin_loaded():
	global user_settings
	user_settings = Settings()





class Console(object):

	def log(self, *args):

		if user_settings.get('dev'):
			print(*args)