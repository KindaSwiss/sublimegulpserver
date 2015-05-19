import sublime, sublime_plugin, inspect, sys, os

from sublime import Region
from operator import itemgetter

from GulpServer.Utils import ignore, all_views, get_command_name, get_source_scope
from GulpServer.Utils import get_views_by_ids, get_views_by_file_names, get_view_or_all
from GulpServer.Utils import format_message, make_report_view
from GulpServer.Utils import isstr, islist, isdict, isint

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
		
		# If the message is None, create the message from the format string and items 
		if not isinstance(message, str):
			message = format_message(format, format_items, user_settings)

		for view in self.views:
			view.set_status(id, message)




class EraseStatusCommand(ViewCommand):
	def run(self, id, **kwargs):
				
		for view in self.views:
			view.erase_status(id)




class ShowErrorCommand(ViewCommand):
	"""  """
	def run(self, id, error, **kwargs):
		file_name = error['file']
		line = error['line']

		# There should only be one view, which is the file the error occured in 
		# Could add a setting/keybinding to open the file if not already open 
		views = self.views

		for view in views:

			region = Region(view.text_point(line, 0))

			# Scroll to the line where the error occured 
			if user_settings.get('scroll_to_error'):
				view.show_at_center(region)

			# Show an icon at the line where the error occured 
			if user_settings.get('show_icon_at_error'):
				icon = user_settings.get('error_icon')
				view.add_regions(id, [region], get_source_scope(view), icon, sublime.DRAW_NO_OUTLINE)

			if user_settings.get('show_error_popup'):
				popup_message = user_settings.get('error_popup_format').format(**error)

				# Show a popup message in the view where the error occured
				view.show_popup(popup_message)
		

		if user_settings.get('show_error_status'):

			# Decide whether or not to show the error all views 
			# or the single view that caused the error
			if not user_settings.get('show_status_in_view'):
				views = all_views()

			status_message =  format_message('error_status_format', error, user_settings)
			
			for view in views:
				view.set_status(id, status_message)




class EraseErrorsCommand(ViewCommand):
	""" Erase gutters icons, status messages, etc produced from errors """
	def run(self, id, **kwargs):
		
		for view in self.views:
			view.erase_regions(id)
			view.erase_status(id)




class ShowPopupCommand(ViewCommand):
	""" Show a popup message """ 
	def run(self, message=None, format=None, format_items=None, **kwargs):
		message = kwargs.get('message')

		# If the message is None, create the message from the format string and items 
		if not isinstance(message, str):
			
			message = format_message(format, format_items, user_settings)
		
		for view in self.views:
			view.show_popup(message)




# Print some data 
class PrintCommand(Command):
	def run(self, **kwargs):
		print(kwargs)




# Keybinding to do the following tasks  

# Open an output panel with the results 
# Have a keybinding to open / close the output panel 
class ReportCommand(Command):
	def run(self, reports, id, **kwargs):
		active_window = sublime.active_window()

		errors = {}
		
		# Loop through each report, gathering the results from each file 
		for report in reports:
			success = report['success']
			results = report.get('results', [])

			for result in results:
				file_name = result['file']

				if not file_name in errors:
					errors[file_name] = []

				error = result.get('error')
				errors[file_name].append(error)

		for error in errors.values():
			print([err.get('line') for err in error])

		sorted_errors = {}

		# Sort the line numbers from smallest to largest 
		for file_name, errs in errors.items():
			sorted_errors[file_name] = sorted(errs, key=itemgetter('line'))
			
		errors = sorted_errors

		# Set the view heading 
		chars = '{0} results\n'.format(id)
		
		# Loop through each error, appending the file name and errors for each result 
		for file_name, errs in errors.items():
			chars += '\n{0}:\n'.format(file_name)

			for err in errs:
				spaces = ' ' * abs(user_settings.get('max_leading_spaces') - len(str(err['line'])))
				chars += spaces + '{line}: {reason}\n'.format(**err)

		report_view = make_report_view(id)


		# Replace all text with the new report 
		report_view.run_command('gulp_server_replace_all_text', {'characters': chars})
		
		report_view.sel().clear()
		# Setting the view to scratch seems to make the Sublime Text 
		# freezing and closing error go away 
		report_view.set_scratch(True)




def run_command(command_name, args, init_args=None):

	if not command_name in commands:
		raise Exception('Command not found for command name {0}'.format(command_name))
	
	command_class = commands[command_name]
	
	# Just so large args aren't printed out to the console 
	if command_name in ['report']:
		print(command_name)
	else:
		print(command_name, args, init_args)
	
	if init_args:
		command = command_class(**init_args)
	else:
		command = command_class()
	
	with ignore(Exception, origin=command.__class__.__name__ + ".run"):
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
user_settings = None




def plugin_loaded():
	global user_settings

	user_settings = Settings()
	
	from GulpServer.Server import on_received
	on_received(handle_received)



