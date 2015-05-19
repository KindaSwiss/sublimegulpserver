import sublime, sublime_plugin
from sublime import Region




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
		




