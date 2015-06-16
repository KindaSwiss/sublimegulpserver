import sublime, sublime_plugin
from sublime import Region
from functools import partial

from GulpServer.Utils import all_views


# Insert text without automatic indentation 
class GulpServerInsertTextCommand(sublime_plugin.TextCommand):
	def run(self, edit, characters, point=0, **kwargs):
		view = self.view
		view.insert(edit, point, characters)



# Replace all text 
class GulpServerReplaceAllTextCommand(sublime_plugin.TextCommand):
	def run(self, edit, characters, **kwargs):
		view = self.view
		view.replace(edit, Region(0, view.size()), characters)
		sels = view.sel()
		sels.clear()
		



class GulpSublimeReporter(sublime_plugin.TextCommand):
	def run(self, edit):
		s = self.view.settings()
		reporter_on = s.get('gulp_sublime_report')
		
		if not reporter_on:
			s.set('gulp_sublime_report', True)
		else:
			s.set('gulp_sublime_report', False)
		
	def is_visible(self):
		view = self.view
		syntax = view.settings().get('syntax')
		return syntax == 'Packages/JavaScript/JavaScript.tmLanguage'

	def is_checked(self):
		return bool(self.view.settings().get('gulp_sublime_report'))


	


def plugin_loaded():
	for view in all_views():
		view_settings = view.settings()
		syntax = view_settings.get('syntax')

		if syntax == 'Packages/JavaScript/JavaScript.tmLanguage':
			view_settings.set('gulp_sublime_report', True)




