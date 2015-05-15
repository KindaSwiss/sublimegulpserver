
# Gulp Commands
[Gulp commands](https://github.com/KindaSwiss/sublimegulpserver/blob/master/GulpCommands.py) are used to execute code in Sublime Text, such as showing a error message in the status bar. They are run from a gulpfile with `sublime.run`. 



#### set_status(id, message=None, format=None, format_items=None, from_settings=False)
Sets a status bar message for all views. The id will be used as the key for the status message. Using the same key will overwrite the previous status message. 

##### id: 
The `id` to associate with the status message. Using the same `id` will overwrite previous status messages. 

##### message
The status message to show. If `status` is `None`, `format` and `format_items` must not be `None`. 

##### format
The format string of the message e.g. `Line {line}; File {file_name}`. If `from_settings` is True, format will be used as a key to retrieve the format string from Packages/User settings file. 

##### format_items
A dictionary whose items will used to format the string 

##### from_settings
Whether or not to retrieve the format string from settings 






### erase_status(id)
Remove the status bar message with the specified `id` from all views. 

##### id
The id of the status to remove 





#### show_error(id, error)
Show an error in several different ways, depending on whether they have been enabled in the package settings. 

##### id
The ID to associate with the gutter icon regions and status messages 




#### erase_errors(id)
Remove all status messages and regions associated with the id 
##### id
The ID of the regions and status messages to remove 




#### gutter_line(id, line)
Adds a gutter icon to a specified line. If no icon is passed, the bookmark icon will be used. 

##### id
The ID to associate with the region

##### line
The line number to show the icon at 




#### remove_gutter(id)
Removes gutter icons from all views associated with the `id`

##### id
The ID of the region to remove 





#### show_popup(message=None, format=None, format_items=None, from_settings=False)
Shows a popup in the view with the same file name as the specified file. Arguments work the same as set_status. 










