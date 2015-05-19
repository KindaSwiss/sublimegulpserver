import sublime, traceback, json, re
from contextlib import contextmanager




@contextmanager
def ignore(*exceptions, origin="", message="", print_exception=True):
	try:
		yield exceptions
	except exceptions as exs:
		if print_exception:
			print('\n' + origin)
			traceback.print_exc(limit=None, file=None, chain=True)
			print()



# Return whether all items passed are of a single type 
def all_of_type(items, t):
	""" Check if all items are of a single type """
	a = all([isinstance(item, t) for item in items])
	# print('all_of_type', a, items, t)
	return a




# Return a list of every view from every window 
def all_views():
	""" Get all views from every window """
	views = []
	for window in sublime.windows():
		for view in window.views():
			views.append(view)
	return views




def get_command_name(clsname):
	name = clsname[0].lower()
	last_upper = False
	for c in clsname[1:]:
		if c.isupper() and not last_upper:
			name += '_'
			name += c.lower()
		else:
			name += c
		last_upper = c.isupper()
	if name.endswith("_command"):
		name = name[0:-8]
	return name




def get_views_by_ids(ids):
	return [view for view in all_views() if view.id() in (ids if isinstance(ids, list) else [ids])]




def get_views_by_file_names(file_names):
	""" Get views by a file name """ 
	if not isinstance(file_names, list):
		file_names = [file_names]

	views = []
	
	for window in sublime.windows():
		for file_name in file_names:
			view = window.find_open_file(file_name)
			if view:
				views.append(view)

	return views




def get_view_or_all(file_name):
	views = None
	
	if isinstance(file_name, str):
		views = get_views_by_file_names(file_name)
	else: 
		views = all_views()

	return views




def get_source_scope(view):
	return view.scope_name(0).split(' ')[0]




def parse_commands(data_bytes, end_of_message="\n"):
	data_strings = [string for string in data_bytes.decode('UTF-8').split(end_of_message) if string]
	commands = [json.loads(data_string) for data_string in data_strings if data_string]
	return commands




def isstr(value):
	return isinstance(value, str)

def isdict(value):
	return isinstance(value, dict)

def islist(value):
	return isinstance(value, dict)

def isint(value):
	return isinstance(value, int)




def make_report_view(id):
	active_window = sublime.active_window()
	report_view = None

	# If the view has already been created for reporting, use it and replace all 
	# text with the new report text 
	if isstr(id):
		for view in all_views():
			
			if view.settings().get('report_id') == id:
				report_view = view

	# Or create the view if it does not exist 
	if not report_view:
		report_view = active_window.new_file()
		report_view.set_name(id)

		view_settings = report_view.settings()
		
		# Set the ID so the view can be identified later 
		view_settings.set('report_id', id)
		# Stuff so the opening files will like find-in-files
		view_settings.set('syntax', 'Packages/Default/Find Results.hidden-tmLanguage')
		view_settings.set('result_file_regex', '^([A-Za-z\\\\/<].*):$')
		view_settings.set('result_line_regex', '^ +([0-9]+):')

	return report_view




# param message {str}        The format string 
# param format_items {dict}  The values used to format the string 
# param settings {Settings}  The settings to retrieve the format  str from 

def format_message(message_format, format_items, settings=None):

	if settings:
		message_format = settings.get(message_format)
	
	message = message_format.format(**format_items)

	return message










