import sublime
import traceback
from contextlib import contextmanager

@contextmanager
def ignore(*exceptions, origin="", message="", print_ex=True):
	try:
		yield exceptions
	except exceptions as exs:
		if print_ex:
			print('\n' + origin)
			traceback.print_exc(limit=None, file=None, chain=True)
			print()

def all_of_type(items, t):
	""" Check if all items are of a single type """
	a = all([isinstance(item, t) for item in items])
	return a

def all_views():
	""" Get all views from every window """
	views = []
	for window in sublime.windows():
		for view in window.views():
			views.append(view)
	return views

# @param {list} ids
def get_views_by_ids(ids):
	""" Returns a list of views whose ids match the ids passed """
	return [view for view in all_views() if view.id() in (ids if isinstance(ids, list) else [ids])]

# @param {str|list} file_names
def get_views_by_file_names(file_names):
	""" Get views by the specified filenames """
	if not isinstance(file_names, list):
		file_names = [file_names]

	views = []

	for window in sublime.windows():
		for file_name in file_names:
			view = window.find_open_file(file_name)
			if view:
				views.append(view)

	return views

# @param {View} view
def get_source_scope(view):
	""" Returns the source scope of the page, such as source.python """
	return view.scope_name(0).split(' ')[0]

# @param {list} items
# @param {int} index
def nth(items, index):
	""" Return an item from a list by index, or None if the index does not exist """
	try:
		return items[index]
	except Exception:
		return None