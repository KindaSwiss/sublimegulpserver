# Settings

### show_status_in_view

Default:  `False`

Whether to show the error status message in the view with the same open file that caused the error or to all open views. 

### show_error_status

Default: `true`

Enables or disables showing error status messages. 

### scroll_to_error

Default: `true`

Enables or disables scrolling to the line where the error when viewing file that caused the error. 

### show_error_popup

Default: `true`

Enables or disables showing an error message in a popup when viewing the file that caused the error. Only available in ST3 build 3070 or later.  

### show_icon_at_error

Default: `true`

Enables or disables showing a gutter icon at the line where the error occured. 

### error_icon

Default: `bookmark`

The type of gutter icon to show. Possible values are `dot`, `circle`, `bookmark`, and `cross`. 

### error_popup_format

Default: `Line {line}; {message}`

The template for error message popups. 

### error_status_format

Default: `{plugin_name} error, Line {line}, File: {file_name}`

The template for error status messages. 

### port

Default: `35048`

The port on which the server will listen and gulp files will connect  

## Formatting error messages 

Error messages may be customized using the following values. 

__Note:__ None of these attributes are guaranteed to exist. The properties of the error are entirely dependent on the plugin that emitted the error. 

| Name | Description |
| ---- | ----------- | 
| _plugin_name_    | The name of the plugin that caused the error          |
| _file_           | The absolute path to the file where the error occured |
| _file_path_      | The directory portion of the file path                |
| _file_name_      | The root name of the file with the extension          |
| _file_base_name_ | The root name of the file                             |
| _file_ext_       | The extension of the file                             |
| _line_           | The line number where the error occured               |
| _message_        | The message associated with the error                 |

### Usage 

The messages are set in the settings file `User/EditorConnect.sublime-settings`.

Example of a `User/EditorConnect.sublime-settings` file.

```json
{
	"error_status_format": "{plugin_name} error, Line {line}, File: {file_name}"
}
```
