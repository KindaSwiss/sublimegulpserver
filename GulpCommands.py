import sublime, sublime_plugin, inspect, sys, os

from sublime import Region

from GulpServer.Utils import ignore, all_views, get_command_name, get_source_scope
from GulpServer.Utils import get_views_by_ids, get_views_by_file_names, get_view_or_all

from GulpServer.Settings import Settings




IS_FAILURE = 0
IS_SUCCESS = 1




class Command(object):
	pass

class ViewCommand(Command):
	def __init__(self, views=None):
		
		if views == '<all>':
			self.views = all_views()
		else:
			self.views = get_views_by_file_names(views)




class SetStatusCommand(ViewCommand):
	def run(self, id, message=None, format=None, format_items=None, **kwargs):
		
		if not isinstance(message, str):

			message = format_message(format, format_items, kwargs.get('from_settings'))

		for view in self.views:
			view.set_status(id, message)




class EraseStatusCommand(ViewCommand):
	def run(self, id, **kwargs):
				
		for view in self.views:
			view.erase_status(id)




class HighlightTextLineCommand(ViewCommand):
	""" Highlight the text in a line """
	def run(self, id, line, **kwargs):

		for view in self.views:
			view.add_regions(id, [Region(view.text_point(line, 0))], get_source_scope(view), '', sublime.DRAW_NO_OUTLINE)




class ShowErrorCommand(ViewCommand):
	"""  """
	def run(self, id, error, **kwargs):
		file_name = error['file']
		line = error['line']

		views = self.views

		if not views:
			# Could add a setting to open the file if not already open 
			return
		
		view = views[0]

		region = Region(view.text_point(line, 0))

		# Scroll to the line where the error occured 
		if settings.get('scroll_to_error'):
			view.show_at_center(region)

		# Show an icon at the line where the error occured 
		if settings.get('show_icon_at_error'):
			icon = settings.get('error_icon')
			view.add_regions(id, [region], get_source_scope(view), icon, sublime.DRAW_NO_OUTLINE)


		if settings.get('show_error_popup'):
			popup_message = settings.get('error_popup_format').format(**error)

			# Show a popup message in the view where the error occured
			view.show_popup(popup_message)
		
		if settings.get('show_error_status'):

			if not settings.get('show_status_in_view'):
				views = all_views()

			status_message =  format_message('error_status_format', error, from_settings=True)
			
			for view in views:
				view.set_status(id, status_message)




class EraseErrorsCommand(ViewCommand):
	""" Erase gutters icons, status messages, etc produced from errors """
	def run(self, id, **kwargs):
		
		for view in self.views:
			view.erase_regions(id)
			view.erase_status(id)




class GutterLineCommand(ViewCommand):
	""" Add a gutter icon to a specific line """
	def run(self, id, line, **kwargs):
		icon = kwargs.get('icon', 'bookmark')

		for view in self.views:
			region = Region(view.text_point(line, 0))
			view.add_regions(id, [region], get_source_scope(view), icon, sublime.DRAW_NO_OUTLINE)
			



class RemoveGutterCommand(ViewCommand):
	""" Add a gutter icon to a specific line """
	def run(self, id, **kwargs):
		
		for view in self.views:
			view.erase_regions(id)




class ShowPopupCommand(ViewCommand):
	""" Show a popup message """ 
	def run(self, message=None, format=None, format_items=None, **kwargs):
		message = kwargs.get('message')

		if not isinstance(message, str):
			
			message = format_message(format, format_items, kwargs.get('from_settings'))
		
		for view in self.views:
			view.show_popup(message)




def format_message(message_format, format_items, from_settings=False):

	if from_settings:
		message_format = settings.get(message_format)
	
	message = message_format.format(**format_items)

	return message




def run_command(command_name, args, init_args=None):

	if not command_name in commands:
		raise Exception('Command not found for command name {0}'.format(command_name))
	
	command_class = commands[command_name]

	if init_args:
		command = command_class(**init_args)
	else:
		command = command_class()
	
	print(command.__class__.__name__, args)

	with ignore(Exception, origin=command.__class__.__name__ + ".run"):
		# print(command.__class__.__name__, args)
		command.run(**args)




def handle_received(command):
	with ignore(Exception, origin="handle_received"):
		# print(command)
		command_name = command['command_name']
		data = command['data']
		args = data['args']
		init_args = data.get('init_args')

		run_command(command_name, args, init_args)




def get_commands():
	""" Get the commands in the current module """
	cmds = {}
	
	for class_name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):

		if cls != Command and issubclass(cls, Command):
			command_name = get_command_name(class_name)
			cmds[command_name] = cls

	return cmds




commands = get_commands()
settings = None




def plugin_loaded():
	global settings

	settings = Settings('gulpserver.sublime-settings')
	settings.load()
	
	from GulpServer.Server import on_received
	on_received(handle_received)



