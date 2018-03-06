import sublime_plugin
import sublime

import json
import traceback

from threading import Thread, Timer
from collections import defaultdict

from SublimeTools.Settings import Settings
from SublimeTools.EventEmitter import EventEmitter
from SublimeTools.Utils import pluck, incremental_id_factory
from SublimeTools.cuid import cuid

# https://github.com/dpallot/simple-websocket-server
from .SimpleWebSocketServer.SimpleWebSocketServer import SimpleWebSocketServer, WebSocket


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

ORIGIN = {
    'id': 'sublimetext3',
}

HOST = '127.0.0.1'

port = None
server = None
server_thread = None

create_call_id = incremental_id_factory()
create_reply_id = incremental_id_factory()


class Messages(object):

    REPLY = 'reply'
    CALL = 'call'
    HANDSHAKE = 'handshake'
    HANDSHAKE_ACCEPT = 'handshake-accept'

    @staticmethod
    def call(name, payload, origin):
        return {
            'id': cuid(),
            'iid': create_call_id(),
            'type': Messages.CALL,
            'event': name,
            'payload': payload,
            'origin': {
                'id': origin['id'],
            }
        }

    @staticmethod
    def reply(payload, call, part, done, origin):
        return {
            'id': cuid(),
            'iid': create_reply_id(),
            'type': Messages.REPLY,
            'part': part,
            'done': done,
            'origin': {
                'id': origin['id'],
            },
            'to': {
                'id': call['id'],
                'iid': call['iid'],
                'event': call['event'],
            },
            'payload': payload,
        }

    @staticmethod
    def handshake(payload, origin):
        return {
            'id': cuid(),
            'type': 'handshake',
            'origin': {
              'id': origin['id'],
            },
            'payload': payload,
          }

    @staticmethod
    def handshake_accept(payload, to, origin):
        return {
            'id': cuid(),
            'type': Messages.HANDSHAKE_ACCEPT,
            'payload': payload,
            'to': {
                'id': to['id']
            },
            'origin': {
                'id': origin['id'],
            },
        }

    @staticmethod
    def is_valid(message):
        """ Returns true if the message conforms to the api """

        if not isinstance(message, dict):
            return False

        return Messages.is_reply(message) or Messages.is_call(message) or Messages.is_handshake(message)

    @staticmethod
    def is_handshake(message):
        if message.get('type') != Messages.HANDSHAKE:
            return False

        origin = message.get('origin')

        return all([
            is_non_empty_str(message.get('id')),
            isinstance(origin, dict) and is_non_empty_str(origin.get('id')),
            'payload' in message,
        ])

    @staticmethod
    def is_call(message):
        if message.get('type') != Messages.CALL:
            return False

        origin = message.get('origin')

        return all([
            is_non_empty_str(message.get('id')),
            isinstance(origin, dict) and is_non_empty_str(origin.get('id')),
            'payload' in message,
            is_non_empty_str(message.get('event'))
        ])

    @staticmethod
    def is_reply(message):
        if message.get('type') != Messages.REPLY:
            return False

        to = message.get('to')
        origin = message.get('origin')

        return all([
            is_non_empty_str(message.get('id')),
            isinstance(origin, dict) and is_non_empty_str(origin.get('id')),
            'payload' in message,
            is_length(message.get('part')),
            isinstance(message.get('done'), bool),
            isinstance(to, dict),
            is_non_empty_str(to.get('id')),
            is_length(to.get('iid')),
            is_non_empty_str(to.get('event')),
        ])


Messages.api_types = [Messages.REPLY, Messages.CALL, Messages.HANDSHAKE, Messages.HANDSHAKE_ACCEPT]


class Parser():
    """ Parses and encodes incoming and outgoing data from the server """

    def encode(self, data):
        return json.dumps(data) + END_OF_MESSAGE_STR

    def decode(self, data):
        return [json.loads(item) for item in str(data).split(END_OF_MESSAGE_STR) if item]


def is_length(value):
    return isinstance(value, int) and value >= 0

def is_non_empty_str(value):
    return isinstance(value, str) and len(value) > 0


class WebSocketServerRequestHandler(WebSocket):
    id = None

    def send(self, data):
        message = self.server.parser.encode(data)
        self.sendMessage(message)

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
                message_id = message.get('id')
                event = message.get('event')
                origin = message.get('origin', {})
                to = message.get('to')
                payload = message.get('payload')

                if not Messages.is_valid(message):
                    raise Exception('Message does not conform to api' + str(message))

                if message_type == Messages.CALL:
                    # print('Incoming call:', message)
                    origin = message
                    part = 0
                    is_done = False

                    def reply(data, done=False, origin=None):
                        nonlocal part, is_done

                        send_origin = ORIGIN.copy()

                        if isinstance(origin, dict) and 'id' in origin:
                            send_origin['child'] = origin['id']

                        if is_done:
                            raise Exception('reply called after done')

                        is_done = done

                        self.send(Messages.reply(data, origin, part, done, send_origin))

                        part += 1

                    # Emit for everyone listening to events on the server
                    self.server.emit(event, payload, reply)

                elif message_type == Messages.REPLY:
                    # print('Incoming reply:', message)
                    # Fire the reply callback for the specified id
                    self.server.api.emit('{0}:{1}'.format(Messages.REPLY, to['id']), message)

                elif message_type == Messages.HANDSHAKE:
                    # self.server.emit('handshake')

                    for client in self.server.clients:
                        if client.id == origin['id']:
                            self.close()
                            return print('Client with id "{}" already exists'.format(client.id))

                    self.id = origin['id']
                    self.send(Messages.handshake_accept(None, message, ORIGIN))
                    self.server.clients.append(self)
                    self.server.emit('{0}:{1}'.format(Messages.HANDSHAKE_ACCEPT, self.id))
                    print('Accepting client {}'.format(self.id))

        except Exception as ex:
            traceback.print_exc()

    def handleConnected(self):
        print('Client connected')

    def handleClose(self):
        print('Client closed')
        self.server.clients.remove(self)


class WebSocketServer(SimpleWebSocketServer, EventEmitter):

    def __init__(self, *args, **kwargs):

        self.clients = []
        self.parser = kwargs.get('parser', Parser())
        self.api = EventEmitter()

        options = {
            'wildcard': ':',
        }
        options.update(kwargs)

        EventEmitter.__init__(self,
            **options
        )

        SimpleWebSocketServer.__init__(self, *args, **kwargs)

    def send_all(self, data):
        for client in self.clients:
            client.send(data)

    def send_to(self, data, origin):
        for client in self.clients:
            if origin == self.id:
                client.send(data)

    def call(
            self,
            name,
            payload=None,
            on_reply=None,
            on_done=None,
            reply_timeout=2000,
            done_timeout=2000,
            origin=None,
        ):
        """ Sends out a call to all listeners """
        if not self.is_listening:
            return False

        send_origin = ORIGIN.copy()

        if isinstance(origin, dict) and 'id' in origin:
            send_origin['child'] = origin['id']

        call = Messages.call(name, payload, send_origin)
        api_event_name = '{0}:{1}'.format(Messages.REPLY, call['id'])
        off = lambda: self.api.off(api_event_name, on_reply)
        parts = []

        def on_reply_from_call(message):
            part, done, payload = pluck(message, 'part', 'done', 'payload')

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

        self.api.on(api_event_name, on_reply_from_call)

        if isinstance(origin, str):
            self.send_to(call, origin)
        else:
            self.send_all(call)


        def on_timeout(name):
            off()
            # raise Exception('timeout until {name} timeout has been exceeded'.format(name=name))
            print('timeout until {name} timeout has been exceeded'.format(name=name))

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


def plugin_unloaded():
    stop_server()
