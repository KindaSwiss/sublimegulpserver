import sublime_plugin
import sublime

class Settings(object):
	""" A wrapper for a sublime.Settings object """
	# The sublime.Settings object
	loaded_settings = None

	# Default settings will be used where no user settings have been defined
	default_settings = {
		"scroll_to_error": True,
		"show_icon_at_error": True,
		"show_error_popup": True,
		"show_error_status": True,
		"show_status_in_view": False,
		"error_status_format": "{plugin_name} error, Line {line}, File: {file_name}",
		"error_popup_format": "Line {line}; {message}",
		"error_icon": "bookmark",
		"port": 35048,
	}
	settings_path = 'EditorConnect.sublime-settings'

	def __init__(self, settings_path=None, load=True):
		if isinstance(settings_path, str):
			# Case sensitive
			self.settings_path = settings_path

		if load:
			self.load()

	def load(self):
		self.loaded_settings = sublime.load_settings(self.settings_path)
		self.loaded_settings.clear_on_change(self.settings_path)
		self.loaded_settings.add_on_change(self.settings_path, self.load)

	def save(self):
		sublime.save_settings(self.settings_path)

	def set(self, key, value):
		""" Set a value into the sublime.Settings object """
		self.load_setting.set(key, value)

	def get(self, key, default=None):
		""" Get a value by key from the settings. Loads from default settings if key doesn't the exist. """
		return self.loaded_settings.get(key, self.default_settings[key])