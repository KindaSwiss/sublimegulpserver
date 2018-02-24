# EditorConnect

A server for scripts to connect to sublime and send data back and forth to plugins through by means of a call/reply messaging system served over websockets.


## Install

Clone the repo into a folder named `EditorConnect` in the sublime packages directory. To find the packages directory, go to the `Preferences` tab and click `Browse packages...`. (This is not on packagecontrol.io)


## Why?

I'm sure there are other websocket/messaging platforms but I needed something that that:

1. Easily integrates into sublime text (using packages from pip can be a nightmare to setup or just flat out impossible for sublime).
2. Has a simple api.
3. Allows calling an event and returning data from either side.
4. The ability to use a single api from python, node, or the browser (with the [editorconnect/node](/)).


## API

The messaging api works off calls and call replies. A "call" is simply an event that is emitted on the other side, which may or may not reply with data (the examples will probably make more sense).

This is inspired by axon req/rep (which is inspired by something else).


### Listening to calls

```python
from EditorConnect import server

# Listen to messages from all socket connections
@server.on('order-milk')
def handle_milk_order(data, reply, done):
    receipt = order_milk(size=data['size'])
    reply(receipt)
    done()

# or just a simple .on call
server.on('order-milk', handle_milk_order)
```

### Sending calls

```
def on_reply(lint_errors, part):
    render(lint_errors)

def on_done(data, parts, part):
    render(lint_errors)

# we can call an action on the client (they are sent to all connected clients)
server.call('lint:javascript', on_reply=on_reply, on_done=on_done)
```

## on_reply(data: any, part: uint, done: bool)

May be called multiple times.

- `{str} data` is the resulting payload returned from the other side for the call.
- `{uint} part` represents what part of the reply is being sent.

## on_done(data: any, parts: list)

Is called when the other side sends the last payload.

- `{str} data` is the resulting payload returned from the other side for the call.
- `{uint} part` represents what part of the reply is being sent.


## Todo

- Set up logging

