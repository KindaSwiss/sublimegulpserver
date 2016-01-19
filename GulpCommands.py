import sublime
import sublime_plugin
import inspect
import sys
from sublime import Region
# from EditorConnect.Server import server_events
from EditorConnect.Utils import ignore, all_views, get_source_scope, get_views_by_file_names
from EditorConnect.Settings import Settings

POPUP_MAX_WIDTH = 700
POPUP_STYLE = """
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

# We keep track of the status bar message ids so that we can remove
# them when the Gulp file disconnects.
active_statuses = []
user_settings = None

class Command(object):
	def __init__(self, views, task=None):
		# The task is the name of a GulpJS task, suffixed with the pluginId
		if task:
			self.task = task

		if views == '<all>':
			self.views = all_views()
		else:
			self.views = get_views_by_file_names(views)

# FIXME: The error status message should probably only show in the same view, not the current one
# Displays a status message and popup for the error
class ShowErrorCommand(Command):
	def run(self, error, **kwargs):
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
				view.show_popup(popup_message + POPUP_STYLE, max_width=POPUP_MAX_WIDTH)

			if line != None:
				region = Region(view.text_point(line, 0))

				# Scroll to the line where the error occured
				if user_settings.get('scroll_to_error'):
					view.show_at_center(region)

				# Show an icon at the line where the error occured
				if user_settings.get('show_icon_at_error'):
					icon = user_settings.get('error_icon')
					view.add_regions(self.task, [region], get_source_scope(view), icon, sublime.DRAW_NO_OUTLINE)

		# Does the user want a status message to be shown?
		if user_settings.get('show_error_status'):
			active_statuses.append(self.task)

			# Does the user want the message to be shown in all
			# views or the single view that caused the error?
			if not user_settings.get('show_status_in_view'):
				views = all_views()

			status_message = user_settings.get('error_status_format').format(**error)

			for view in views:
				view.set_status(self.task, status_message)

# Erase gutters icons, status messages, etc associated with the id
class EraseErrorCommand(Command):
	def run(self, **kwargs):
		global active_statuses

		if self.task in active_statuses:
			active_statuses = [status for status in active_statuses if status != self.task]

		for view in self.views:
			view.erase_regions(self.task)
			view.erase_status(self.task)

def run_command(command_name, args, init_args):
	if not command_name in commands:
		raise Exception('Command not found for command name {0}'.format(command_name))

	command_class = commands[command_name]
	command = command_class(**init_args)

	with ignore(Exception, origin=command.__class__.__name__ + ".run"):
		command.run(**args)

def get_commands():
	""" Get the commands in all module """
	cmds = {}

	for class_name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
		if cls != Command and issubclass(cls, Command):
			command_name = class_name.replace('Command', '')
			cmds[command_name] = cls

	return cmds

commands = get_commands()

# Command should have a
def handle_received(command):
	command_name = command.get('name', None)
	command_data = command.get('data', {})

	if user_settings.get('dev'):
		print(command_name, command_data, command)

	if command_name == None or command_data == None:
		return

	init_args = {
		"views": command.get('views', []),
		"task": command.get('task', None)
	}
	run_command(command_name, command_data, init_args)

def handle_disconnect(id):
	# Erase status and gutters messages when the gulpfile disconnects because
	# when the gulpfile reconnects it won't override the same task names.
	# This is because the task names are suffixed by an id that is unique to each gulp file.
	for view in all_views():
		for status in active_statuses:
			if id in status:
				view.erase_regions(status)
				view.erase_status(status)

def plugin_unloaded():
	from EditorConnect.Server import server_events

	server_events.off('receive', handle_received)
	server_events.off('disconnect', handle_disconnect)

def plugin_loaded():
	global user_settings

	from EditorConnect.Server import server_events

	user_settings = Settings()
	server_events.on('receive', handle_received)
	server_events.on('disconnect', handle_disconnect)