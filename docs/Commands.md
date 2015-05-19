
# Gulp Commands
[Gulp commands](https://github.com/KindaSwiss/sublimegulpserver/blob/master/GulpCommands.py) are used to execute code in Sublime Text, such as showing a error message in the status bar. They are not actual Sublime Text commands. The API for running the commands from a gulp file can be found [here](https://github.com/KindaSwiss/sublimejs/blob/master/docs/API.md#sublimeruncommand_name-args-init_args). 


<br>


## Types of commands

There are two types of commands. 

### Command 

A base class from which other command classes may inherit 

### ViewCommand

```Python
def __init__(self, views):
````

#### views

Type: `str` or `list`

May be either `'<all>'`, meaning get all views from every window, or a list of file names of which views with the same open file will be retrieved. The command will run on the views retrieved. 


<br>


## Commands
<!--  -->
Below is a list of commands and their arguments. 

### SetStatusCommand

Type: `ViewCommand`

```Python
def run(self, id, message=None, format=None, format_items=None, settings=None):
````

Sets a status bar message for all views. The id will be used as the key for the status message. Using the same key will overwrite the previous status message. 


#### id

Type: `str`

The `id` to associate with the status message. Using the same `id` will overwrite previous status messages. 

#### message

Type: `str`

The status message to show. If `status` is `None`, `format` and `format_items` must not be `None`. 

#### format

Type: `str`

The format string of the message e.g. `Line {line}; File {file_name}`. If `from_settings` is True, format will be used as a key to retrieve the format string from Packages/User settings file. 

#### format_items

Type: `dict`

A dictionary whose items will used to format the string. 

#### settings

Type: `Sublime.Settings`

A settings object to retrieve the format string from. 




### EraseStatusCommand

Type: `ViewCommand`

```Python
def run(self, id):
````

Remove the status bar message with the specified `id`. 

#### id

Type: `str`

The id of the status to remove. 




### ShowErrorCommand

Type: `ViewCommand`

```Python
def run(self, id, error):
````

Show an error in several different ways, depending on whether they have been enabled in the package settings. 

#### id

Type: `str` 

The ID to associate with the gutter icon regions and status messages. 




### EraseErrorsCommand

Type: `ViewCommand`

```Python
def run(self, id):
````

Remove all status messages and regions associated with the id. 

#### id

Type: `str` 

The ID of the regions and status messages to remove. 




#### ShowPopupCommand

Type: `ViewCommand`

```Python
def run(message=None, format=None, format_items=None, from_settings=False):
```

Shows a popup in the view with the same file name as the specified file. Arguments work the same as set_status. 



#### ReportCommand

Type: `Command`

```Python
def run(self, reports, id):
````

Opens a new tab with JSHint results in the format of "Find in Files" results. File names and line numbers within the tab can be clicked to open the file, the same as a "Find in Files" results tab. 

##### reports 

Type: `list`

A list of reports for each file that was run through JSHint. 

##### id

Type: `str`

An ID to associate with the report tab. This allows the report tab to be updated instead of creating a new tab every time the reporter is run. 





