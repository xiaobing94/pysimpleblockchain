# coding:utf-8
import socket, threading
from xmlrpc.server import SimpleXMLRPCServer


class RPCServer(object):
    """
    export_functions = []
    export_functions.append((func1, "add"))
    export_functions.append((func2, "sub"))
    """
    def __init__(self, port=9999, export_functions=[], export_instance=None, name='RPC Server'):
        self._port = port
        self._started = False
        self._export_functions = export_functions
        self._export_instance = export_instance
        self._name = name
    
    def __del__(self):
        self.stop()

    @staticmethod
    def _rpc_server_thread(rpc_server):
        rpc_server._server.serve_forever()

    def stop(self):
        if self._started:
            self._started = False
            self._server.shutdown()
            self._server.server_close()

    def start(self, blocking=True):
        if not self._started:
            try:
                self._server = SimpleXMLRPCServer(('127.0.0.1', self._port), logRequests=False, allow_none=True)
            except socket.error as e:
                pass
            else:
                self._server.register_multicall_functions()
                for func in self._export_functions:
                    self._server.register_function(func[0], func[1])

                if self._export_instance is not None:
                    self._server.register_instance(self._export_instance)
                self._started = True
                if not blocking:
                    self._thread = threading.Thread(target=RPCServer._rpc_server_thread, args=(
                     self,), name='%s thread' % self._name)
                    self._thread.daemon = True
                    self._thread.start()
                else:
                    RPCServer._rpc_server_thread(self)
        return self._started

    def get_listening_port(self):
        return self._port

    def is_started(self):
        return self._started

    def wait_stopped(self):
        if hasattr(self, '_thread'):
            while self._thread.is_alive():
                self._thread.join(1)

if __name__ == '__main__':
    def func1(a, b):
        return a + b


    def func2(a, b):
        return a - b
    
    functions = []
    functions.append((func1, 'add'))
    functions.append((func2, 'sub'))
    server = RPCServer(80, export_functions=functions)
    print('RPC server created (not started yet)')
    server.start(False)
    server.wait_stopped()