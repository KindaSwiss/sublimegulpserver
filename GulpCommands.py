import sublime, sublime_plugin, inspect, sys, os

from sublime import Region

from Server.Utils import ignore, all_views, get_command_name, get_source_scope
from Server.Utils import get_views_by_ids, get_views_by_file_names




IS_FAILURE = 0
IS_SUCCESS = 1




class Command(object):
	pass




class UpdateStatusCommand(Command):
	def run(self, status_id, status, **kwargs):
		for view in all_views():
			view.set_status(status_id, status)




class EraseStatusCommand(Command):
	def run(self, status_id, **kwargs):
		for view in all_views():
			view.erase_status(status_id)




class HighlightTextLineCommand(Command):
	""" Highlight the text in a line """
	def run(self, id, line, file_name, **kwargs):
		line = line - 1
		views = get_views_by_file_names(file_name)

		for view in views:
			view.add_regions(id, [Region(view.text_point(line, 0))], get_source_scope(view), '', sublime.DRAW_NO_OUTLINE)




class GutterLineCommand(Command):
	""" Add a gutter icon to a specific line """
	def run(self, id, line, file_name, **kwargs):
		line = line - 1
		icon = kwargs.get('icon', 'bookmark')
		views = get_views_by_file_names(file_name)

		for view in views:
			view.add_regions(id, [Region(view.text_point(line, 0))], get_source_scope(view), icon, sublime.DRAW_NO_OUTLINE)




# Show a popup with a status
class ShowPopupCommand(Command):
	def run(self, message, file_name, **kwargs):
		views = get_views_by_file_names(file_name)
	
		for view in views:
			view.show_popup(message)




def run_command(command_name, args):
	if not command_name in commands:
		raise Exception('Command not found for command name {0}'.format(command_name))

	command_class = commands[command_name]
	command = command_class()

	with ignore(Exception, origin=command.__class__.__name__ + ".run"):
		command.run(**args)




def handle_received(command):
	with ignore(Exception, origin="handle_received"):
		# print(command)
		command_name = command['command_name']
		data = command['data']

		run_command(command_name, data)




def get_commands():
	""" Get the commands in the current module """
	cmds = {}
	
	for class_name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):

		if obj != Command and issubclass(obj, Command):
			cmds[get_command_name(class_name)] = obj
	
	return cmds




commands = get_commands()




def plugin_loaded():
	from Server.Server import on_received
	on_received(handle_received)
	





