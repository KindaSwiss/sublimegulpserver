# editorconnect-sublime

A server for scripts to connect to sublime and send data back and forth to plugins through by means of a call/reply messaging system served over websockets.


## Install

First, follow the install instructions for https://github.com/anthonykoch/SublimeTools.

Clone this repo into a folder named `EditorConnect` into the same directory with the name "EditorConnect".


## Clients

You can use these to connect to this server:

**Node and browser**: [editorconnect-node](https://github.com/anthonykoch/editorconnect-node)


## Why?

I'm sure there are other websocket/messaging platforms but I needed the following:

1. Easily integrates into sublime text (using packages from pip can be a nightmare to setup or just flat out impossible for sublime).
2. Has a simple api.
3. Allows calling an event and returning data from either the client or the server.
4. The ability to use a single api from python, node, or the browser


## API

The messaging api works off calls and replies. A "call" is simply an event that is emitted on the other side, which may or may not reply with data (the examples will probably make more sense).

### Server.server.call(name, on_reply: callable, on_done: callable, origin=None)

```
from EditorConnect import Server

def on_reply(lint_errors, part):
    render(lint_errors)

def on_done(data, parts, part):
    render(lint_errors)

# we can call an action on the client (the call is sent to all connected clients)
Server.server.call('lint:javascript', on_reply=on_reply, on_done=on_done)

# or call to a specific client when you know the client's origin id
Server.server.call('lint:javascript', on_done=on_done, origin='abcdefid')
```

#### on_reply(data: any, part: int)

The reply callback may be called zero or more times. It will never be called on the last payload sent.

- `data (any)` is a part of the resulting payload returned for the call.
- `part (int)` represents what part of the reply is being sent.

#### on_done(data: any, parts: list)

The done callback will always be called once.

- `data (any)` is the last payload sent.
- `parts (list)` a list of payloads received for the call


### Listening to calls

```python
from EditorConnect import Server

# Listen to messages from all socket connections
@Server.server.on('order-milk')
def handle_milk_order(data, reply, done):
    receipt = order_milk(size=data['size'])
    reply(receipt)
    done()

# or like this
Server.server.on('order-milk', handle_milk_order)

def plugin_unloaded():
    # Make sure to remove the event handler when the plugin is reloaded,
    # or else you'll have code running a bunch of times
    Server.server.off('order-milk', handle_milk_order)
```

### Server lifecycle events

**`server.on('self:client:close') | listener(client_id: str)`**

When a client disconnects

**`server.on('self:client:close:<client_id>')`**

When a client disconnects

**`server.on('self:client:accept') | listener(client_id: str)`**

When a client is accepted and ready to receive calls

**`server.on('self:client:accept:<client_id>')`**

Called when the specified client is connected.

**`server.on('self:pre-stop')`**

Emitted before the server has stopped

**`server.on('self:stop')`**

Emitted after the server has stopped

**`server.on('self:pre-start')`**

Emitted right before the server starts

```python
from EditorConnect.Server import events

@Server.server.on('self:start', on_start)
def on_start():
    print('server has started')

def plugin_loaded(self):
    # Don't forget to remove old listeners!
    Server.server.off('self:start', on_start)
```


## Credit where credit is due

[SimpleWebSocketServer is MIT licensed by dpallot](https://github.com/dpallot/simple-websocket-server)



### Todo

- Callbacks for call timeouts
- Tests
- Clean up code
- Document how the cally/reply api works internally

