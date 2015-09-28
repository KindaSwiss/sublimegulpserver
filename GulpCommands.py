import sublime, sublime_plugin, inspect, sys, os

from sublime import Region

from GulpServer.Utils import ignore, all_views, get_command_name, get_source_scope
from GulpServer.Utils import get_views_by_ids, get_views_by_file_names, format_message
from GulpServer.Utils import isstr, islist, isdict, isint, nth
from GulpServer.Settings import Settings
from GulpServer.Logging import Console




popup_style = """
<style>
html {
    background-color: #393b3d;
    color: #CCCCCC;
}

body {
    background-color: #232628;
    margin: 1px;
    padding: 1em 2em 1em 1em;
    font-weight: 100;
}
</style>
"""




class Command(object):
	pass

class ViewCommand(Command):
	def __init__(self, views):

		if views == '<all>':
			self.views = all_views()
		else:
			self.views = get_views_by_file_names(views)




# Show a popup message
class ShowPopupCommand(ViewCommand):

	# @param {str}      id
	# @param {str|None} message      The message to show for the status, or None if the status
	#                                message is to be retrieved from a template string in user_settings
	# @param {str}      template     The template to use when formatting
	# @param {dict}     format_items The items that template will be formatted with
	def run(self, message, format, format_items, **kwargs):
		message = kwargs.get('message')

		# If the message wasn't sent in the command, create
		# the message from the format string specified in the settings
		if not isinstance(message, str):
			message = format_message(format, format_items, user_settings)

		for view in self.views:
			view.show_popup(message)




# Sets a status messages in the specified views
class SetStatusCommand(ViewCommand):

	def run(self, id, message=None, template=None, format_items=None, **kwargs):
		# If the message wasn't sent in the command, create
		# the message from the template string specified in the settings
		if not isinstance(message, str):
			message = format_message(template, format_items, user_settings)

		for view in self.views:
			view.set_status(id, message)




# Erases status messages from the specified views
class EraseStatusCommand(ViewCommand):

	def run(self, id, **kwargs):

		for view in self.views:
			view.erase_status(id)




# Displays a status message and popup for the error
class ShowErrorCommand(ViewCommand):

	def run(self, id, error, **kwargs):
		file_name = error['file']
		line = error['line']

		# There should only be one view, which is the file the error occured in
		# Could add a setting/keybinding to open the file if not already open
		views = self.views

		for view in views:

			# Does the user want a popup to show?
			if user_settings.get('show_error_popup'):
				popup_message = user_settings.get('error_popup_format').format(**error)

				# Show a popup message in the view where the error occured
				view.show_popup(popup_message + popup_style, max_width=500)

			if line != None:
				region = Region(view.text_point(line, 0))

				# Scroll to the line where the error occured
				if user_settings.get('scroll_to_error'):
					view.show_at_center(region)

				# Show an icon at the line where the error occured
				if user_settings.get('show_icon_at_error'):
					icon = user_settings.get('error_icon')
					view.add_regions(id, [region], get_source_scope(view), icon, sublime.DRAW_NO_OUTLINE)

		# Does the user want a status message to be shown?
		if user_settings.get('show_error_status'):

			# Does the user want the message to be shown in all
			# views or the single view that caused the error?
			if not user_settings.get('show_status_in_view'):
				views = all_views()

			status_message = format_message('error_status_format', error, user_settings)

			for view in views:
				view.set_status(id, status_message)




# Erase gutters icons, status messages, etc associated with the id
class EraseErrorsCommand(ViewCommand):
	def run(self, id, **kwargs):

		for view in self.views:
			view.erase_regions(id)
			view.erase_status(id)




def run_command(command_name, args, init_args=None):

	if not command_name in commands:
		raise Exception('Command not found for command name {0}'.format(command_name))

	command_class = commands[command_name]

	# Log the commands if in dev mode
	if user_settings.get('dev'):
		console.log(command_name, args, init_args)

	if init_args:
		command = command_class(**init_args)
	else:
		command = command_class()

	with ignore(Exception, origin=command.__class__.__name__ + ".run"):
		command.run(**args)




def get_commands():
	""" Get the commands in all module """
	cmds = {}

	for class_name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):

		if cls != Command and issubclass(cls, Command):
			command_name = get_command_name(class_name)
			cmds[command_name] = cls

	return cmds




commands = get_commands()
user_settings = None
console = None




# Add a callback to when the data is received from the server
def handle_received(command):
	with ignore(Exception, origin="handle_received"):
		console.log(command)
		command_name = command['name']
		data = command['data']
		args = data['args']
		init_args = data.get('init_args')

		run_command(command_name, args, init_args)




def plugin_loaded():
	global user_settings, console

	user_settings = Settings()
	console = Console()

	from GulpServer.Server import on_received
	on_received(handle_received)