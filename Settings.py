import sublime_plugin
import sublime

class Settings(object):
	""" A wrapper for a sublime.Settings object """
	# The sublime.Settings object
	loaded_settings = None
	path = 'EditorConnect.sublime-settings'

	def __init__(self, load=True):
		if load:
			self.load()

	def load(self):
		self.loaded_settings = sublime.load_settings(self.path)
		self.loaded_settings.clear_on_change(self.path)
		self.loaded_settings.add_on_change(self.path, self.load)

	def save(self):
		sublime.save_settings(self.path)

	def set(self, key, value):
		""" Set a value into the sublime.Settings object """
		self.load_setting.set(key, value)

	def get(self, key, default=None):
		""" Get a value by key from the settings. Loads from default settings if key doesn't the exist. """
		return self.loaded_settings.get(key)