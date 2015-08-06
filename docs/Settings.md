
# Settings


### show_status_in_view

__Default:__ `False`

Whether to show the error status message in the view with the same open file that caused the error or to all open views. 



### show_error_status

__Default:__`true`

Enables or disables showing error status messages. 



### scroll_to_error

__Default:__`true`

Enables or disables scrolling to the line where the error when viewing file that caused the error. 




### show_error_popup

__Default:__`true`

Enables or disables showing an error message in a popup when viewing the file that caused the error. Only available in ST3 build 3070 or later.  




### show_icon_at_error

__Default:__`true`

Enables or disables showing a gutter icon at the line where the error occured. 




### error_icon

__Default:__`bookmark`

The type of gutter icon to show. Possible values are `dot`, `circle`, `bookmark`, and `cross`. 




### error_popup_format

__Default:__`Line {line}; {message}`

The template for error message popups. 


### error_status_format

__Default:__`{plugin_name} error, Line {line}, File: {file_name}`

The template for error status messages. 






### port

__Default:__`30048`

The port on which the server will listen and gulp files will connect  



<br>

## Formatting error messages 
Error messages may be customized using the following values. 

| Name | Description |
| ---- | ----------- | 
| _plugin_name_ | The name of the plugin that caused the error |
| _file_ | The absolute path to the file where the error occured |
| _file_path_ | The directory portion of the file path | 
| _file_name_ | The root name of the file with the extension |
| _file_base_name_ | The root name of the file |
| _file_ext_ | The extension of the file |
| _line_ | The line number where the error occured |
| _message_ | The message associated with the error |



