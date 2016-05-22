import sublime_plugin
import sublime
import json
import socketserver
from threading import Thread
from collections import defaultdict
from EditorConnect.Utils import ignore, EventEmitter
from EditorConnect.Settings import Settings


END_OF_MESSAGE_BYTE = b'\n'[0]
END_OF_MESSAGE_STR = '\n'
HANDSHAKE = {
	"name": 'Sublime Text 3',
	"handshake": True
}
HOST = '127.0.0.1'


port = None
server = None
server_thread = None
server_events = EventEmitter()


class Parser():
	""" Parses and encodes incoming and outgoing data from the server """
	def encode(self, data):
		return json.dumps(data) + END_OF_MESSAGE_STR

	def decode(self, data):
		return [json.loads(item) for item in str(data, encoding='utf8').split(END_OF_MESSAGE_STR) if item]


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	def __init__(self, server_address, RequestHandlerClass):
		socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)
		self.clients = []

	def add_client(self, client):
		server.clients.append(client)

	def remove_client(self, client):
		if client in self.clients:
			self.clients.remove(client)

	def send_all(self, data):
		""" Send data to all clients """
		for client in self.clients:
			client.send(data)

	def send(self, data, id_name):
		""" Send data to a specific client """
		for client in self.clients:
			if client.id == id_name:
				client.send(data)

	def close_requests(self):
		""" Close all requests of the server """
		for client in self.clients:
			client.finish()
		self.clients = []


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
	""" Server request handler """

	def is_valid_handshake(self):
		self.parser = Parser();

		try:
			handshake = self.parser.decode(self.recvall())[0]
		except Exception as ex:
			if user_settings.get('dev'):
				print('Handshake error', ex)

			return False

		plugin_id = handshake.get('pluginId')

		if plugin_id:
			self.id = plugin_id
			self.server.add_client(self)
			self.send(HANDSHAKE)
			server_events.emit('connect', plugin_id)

			if user_settings.get('dev'):
				print('"{0}" connected - Total {1}'.format(self.id, len(self.server.clients)))

			return True
		else:
			return False

	def handle(self):
		self.should_receive = True
		self.closed = False

		with ignore(Exception, origin="ThreadedTCPRequestHandler.handle"):
			if not self.is_valid_handshake():
				return self.finish()

			while self.should_receive:
				data_bytes = self.recvall()

				if not data_bytes:
					break

				messages = self.parser.decode(data_bytes)

				for message in messages:
					server_events.emit('receive', message)

	def finish(self):
		""" Tie up any loose ends with the request """
		# If the client has not already been closed then close it
		if not self.closed:
			self.request.close()

		# Remove self from list of server clients
		self.server.remove_client(self)
		self.closed = True
		server_events.emit('disconnect', self.id)

	def send(self, data):
		# Send data to the client
		with ignore(Exception, origin='ThreadedTCPRequestHandler.send'):
			data = sublime.encode_value(data)
			self.request.sendall((data).encode('utf8'))
			return

		self.finish()

	# Keep receiving until an END_OF_MESSAGE is hit.
	def recvall(self, buffer_size=4096):
		try:
			data_bytes = self.request.recv(buffer_size)

			if not data_bytes:
				return data_bytes

			# Keep receiving until the end of message is hit
			while data_bytes[-1] != END_OF_MESSAGE_BYTE:
				data_bytes += self.request.recv(buffer_size)

		except Exception as ex:
			if user_settings.get('dev'):
				print('Receiving error', ex)

			return b''

		return data_bytes


def start_server():
	""" Start the server """
	global server, server_thread

	if server != None:
		return print('Editor Connect server is already running')

	# FIXME: Need to catch the error where previous server didn't shut down
	server = ThreadedTCPServer((HOST, port), ThreadedTCPRequestHandler)

	server_thread = Thread(target=server.serve_forever, daemon=True)
	server_thread.deamon = True
	server_thread.start()
	print('Editor Connect server started on port {0}'.format(port))


def stop_server():
	""" Stop the server """
	global server

	if server == None:
		return print('Editor Connect server is already shutdown')

	server.close_requests()
	server.shutdown()
	server = None
	server_thread = None
	print('Editor Connect server stopped')


class StartServerCommand(sublime_plugin.ApplicationCommand):
	""" Start the server """
	def run(self):
		sublime.set_timeout_async(start_server, 2000)

	def is_enabled(self):
		return server == None and server_thread != None and not server_thread.is_alive()


class StopServerCommand(sublime_plugin.ApplicationCommand):
	""" Stop the server """
	def run(self):
		stop_server()

	def is_enabled(self):
		return server != None and server_thread != None and server_thread.is_alive()


def plugin_loaded():
	global user_settings, port
	user_settings = Settings()
	port = user_settings.get('port')
	# Setting a timeout will ensure the port is clear for reuse
	sublime.set_timeout_async(start_server, 2000)


def plugin_unloaded():
	stop_server()