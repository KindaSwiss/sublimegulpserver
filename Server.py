import sublime_plugin
import sublime

import json
import traceback

from threading import Thread, Timer
from collections import defaultdict

from .SublimeTools.Utils import pluck, EventEmitter, Settings

# https://github.com/dpallot/simple-websocket-server
from .SimpleWebSocketServer.SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

# # https://github.com/riga/pymitter
# from .pymitter.pymitter import EventEmitter

# https://github.com/necaris/cuid.py/blob/master/cuid.py
from .cuid.cuid import cuid


SETTINGS_PATH = 'EditorConnect.sublime-settings'

SERVER_START_DELAY = 1500

END_OF_MESSAGE_BYTE = b'\n'[0]
END_OF_MESSAGE_STR = '\n'

HANDSHAKE = {
    'about': {
        'name': 'Sublime Text',
        'version': sublime.version(),
        'platform': sublime.platform(),
    },
    'handshake': True
}

HOST = '127.0.0.1'

port = None
server = None
server_thread = None
server_events = EventEmitter()


api_types = ['call', 'call-reply']

class Messages(object):

    REPLY = 'call-reply'
    CALL = 'call'

    @staticmethod
    def call(name, payload):
        return {
            'id': cuid(),
            'type': Messages.CALL,
            'event': name,
            'payload': payload,
        }

    @staticmethod
    def reply(payload, origin, part, done):
        return {
            'id': cuid(),
            'type': Messages.REPLY,
            'part': part,
            'done': done,
            'origin': {
                'id': origin['id'],
                'iid': origin['iid'],
                'event': origin['event'],
            },
            'payload': payload,
        };

# class Call(object):

    # def __init__

class Parser():
    """ Parses and encodes incoming and outgoing data from the server """

    def encode(self, data):
        return json.dumps(data) + END_OF_MESSAGE_STR

    def decode(self, data):
        return [json.loads(item) for item in str(data).split(END_OF_MESSAGE_STR) if item]


def validate(message):
    """ Returns true if the message conforms to the api """

    if not isinstance(message, dict):
        return False

    type = message.get('type')
    event = message.get('event')
    id = message.get('id')
    origin = message.get('origin', {})
    origin_id = origin.get('id')
    payload = message.get('payload')
    part = message.get('part')
    is_done = message.get('done')

    if type == Messages.CALL:
        return all([
            isinstance(event, str) and len(event) > 0 and
            'payload' in message
        ])

    elif type == Messages.REPLY:
        return all([
            isinstance(part, int) and part >= 0 and
            isinstance(is_done, bool) and
            isinstance(origin_id, str) and len(origin_id) > 0 and
            isinstance(event, str) and len(event) > 0 and
            'payload' in message

        ])

    return False


class WebSocketServerRequestHandler(WebSocket):

    def handleMessage(self):
        # simplesocketserver swallows exceptions, so we just have to catch them all and print them out
        try:
            try:
                messages = self.server.parser.decode(self.data)
            except Exception as ex:
                raise Exception('Could not not decode messages ' + str(self.data))

            if not isinstance(messages, list):
                raise Exception('parser.decode did not return a dict')

            for message in messages:
                message_type = message.get('type')
                event = message.get('event')
                message_id = message.get('id')
                origin = message.get('origin', {})
                origin_id = origin.get('id')
                payload = message.get('payload')

                if not validate(message):
                    raise Exception('Message does not conform to api' + str(message))

                if message_type == Messages.CALL:
                    origin = message
                    part = 0
                    is_done = False

                    def reply(data, done=False):
                        nonlocal part, is_done

                        if is_done:
                            raise Exception('reply called after done')

                        is_done = done

                        payload = self.server.parser.encode(Messages.reply(data, origin, part, done))
                        self.sendMessage(payload)
                        part += 1

                    # Emit for everyone listening to events on the server
                    self.server.hub.emit(event, payload, reply)

                elif message_type == Messages.REPLY:
                    # Fire the reply callback for the specified id
                    self.server.api.emit('{0}:{1}'.format(Messages.REPLY, origin_id), message)
        except Exception as ex:
            traceback.print_exc()

    def handleConnected(self):
        self.server.clients.append(self)

    def handleClose(self):
        print('close')
        self.server.clients.remove(self)


class WebSocketServer(SimpleWebSocketServer):

    def __init__(self, *args, **kwargs):
        SimpleWebSocketServer.__init__(self, *args, **kwargs)

        self.clients = [];
        self.parser = kwargs.get('parser', Parser())
        self.api = EventEmitter()
        self.hub = EventEmitter()

    def send_all(self, data):
        for client in self.clients:
            message = self.parser.encode(data)
            client.sendMessage(message)

    def on(self, name):
        def _on(name, fn):
            self.hub.on(name, fn)

        def decorator(original):
            if callable(original):
                _on(name, original)

            return original

        return decorator

    def off(self, name):
        def _off(name, fn):
            self.hub.off(name, fn)

        def decorator(original):
            if callable(original):
                _off(name, original)

            return original

        return decorator

    def call(
            self,
            name,
            payload=None,
            on_reply=None,
            on_done=None,
            reply_timeout=2000,
            done_timeout=2000
        ):
        """ Sends out a call to all listeners """
        if not self.is_listening:
            return False;

        call = Messages.call(name, payload)
        api_event_name = 'call-reply:{0}'.format(call['id'])
        off = lambda: self.api.off(api_event_name, on_reply)
        parts = []

        def on_reply_from_call(message):
            part, done, payload = pluck(message, 'part', 'done', 'payload')
            # print('reply', part, done, data)

            parts.append(payload)
            reply_timer.cancel()

            if done:
                done_timer.cancel()
                off()

                if callable(on_done):
                    on_done(payload, parts, part)
            else:
                # maybe asyncio will make this more consistent with the nodejs api
                if callable(on_reply):
                    on_reply(payload, part)

        self.api.on(api_event_name, on_reply_from_call);
        self.send_all(call)

        def on_timeout(name):
            off()
            raise Exception('timeout until {name} timeout has been exceeded'.format(name=name))

        reply_timer = Timer(reply_timeout / 1000, lambda: on_timeout('first reply'))
        reply_timer.start()

        done_timer = Timer(done_timeout / 1000, lambda: on_timeout('done'))
        done_timer.start()

        return True

def start_server():
    """ Start the server if it isn't running """
    global server, server_thread

    if server is not None and server.is_listening:
        return print('Editor Connect server is already running')

    server = WebSocketServer(HOST, user_settings.get('port'), WebSocketServerRequestHandler)
    server_thread = Thread(target=server.serveforever, daemon=True)
    server_thread.start()
    server.is_listening = True

    print('Editor Connect server started on port {0}'.format(port))


def stop_server():
    """ Stop the server if it's running """
    global server

    if server is None or not server.is_listening:
        return print('Editor Connect server is already shutdown')

    server.close()
    server_thread = None
    server.is_listening = False

    print('Editor Connect server stopped')


class StartServerCommand(sublime_plugin.ApplicationCommand):
    """ Start the server if it isn't running """
    def run(self):
        sublime.set_timeout_async(start_server, SERVER_START_DELAY)

    def is_enabled(self):
        return (server == None and not server.is_listening) and server_thread != None and not server_thread.is_alive()


class StartServerCommand(sublime_plugin.ApplicationCommand):
    """ Start the server if it isn't running """
    def run(self):
        sublime.set_timeout_async(start_server, SERVER_START_DELAY)

    def is_enabled(self):
        return (server == None and not server.is_listening) and server_thread != None and not server_thread.is_alive()



def plugin_loaded():
    global user_settings, port
    user_settings = Settings(SETTINGS_PATH)
    port = user_settings.get('port')

    # Setting a timeout will ensure the port is clear for reuse
    sublime.set_timeout(start_server, SERVER_START_DELAY)

    print('Plugin loaded!')

def plugin_unloaded():
    stop_server()
