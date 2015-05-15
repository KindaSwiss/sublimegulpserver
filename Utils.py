import sublime, traceback
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




def get_source_scope(view):
	return view.scope_name(0).split(' ')[0]




def get_view_or_all(file_name):
	views = None
	
	if isinstance(file_name, str):
		views = get_views_by_file_names(file_name)
	else: 
		views = all_views()

	return views



