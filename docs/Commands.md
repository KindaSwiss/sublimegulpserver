# Gulp Commands

## Attributes

Each gulp command will the following attributes.

#### views

Type: list

A list of file names (that correspond to an open tab) that the command may run on. The list may be empty.

#### task

Type: str

The name of a Gulp task, which is suffixed with pluginId. 

## Commands 

### ShowError

Shows the errors, such as in a status message, gutter icon, or a popup. The attribute `task` is used as the id for the regions and status messages. 

### EraseError

Remove all status messages and regions associated with the task. 