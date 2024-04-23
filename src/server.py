from http.server import BaseHTTPRequestHandler, HTTPServer
from os import listdir
from urllib.parse import urlparse

class BaseHandler():
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def get_endpoint(self):
        return self._endpoint

    def do_GET(self, handler, *args):
        pass

    def do_POST(self, handler, *args):
        pass

class WebPageHandler(BaseHandler):
    def __init__(self, endpoint, path, stylesheets, scripts):
        self._path = path
        self._stylesheets = stylesheets
        self._scripts = scripts

        super().__init__(endpoint)

    def __stylesheet_tag_html(self, path):
        return f"<link rel='stylesheet' href='{path}'>"

    def __script_tag_html(self, path):
        return f"<script type='text/javascript' src='{path}'></script>"

    def do_GET(self, handler, *args):
        handler.send_response(200)
        handler.send_header("Content-type", "text/html")
        handler.end_headers()

        for path in self._stylesheets:
            handler.wfile.write(bytes(self.__stylesheet_tag_html(path), "utf-8"))

        for path in self._scripts:
            handler.wfile.write(bytes(self.__script_tag_html(path), "utf-8"))

        with open(self._path, "rb") as file:
            handler.wfile.write(file.read())

class ResourceHandler(BaseHandler):
    def __init__(self, endpoint, path, content_type):
        self._path = path
        self._content_type = content_type

        super().__init__(endpoint)

    def do_GET(self, handler, *args):
        handler.send_response(200)
        handler.send_header("Content-type", self._content_type)
        handler.end_headers()

        with open(self._path, "rb") as file:
            handler.wfile.write(file.read())

class APIHandler(BaseHandler):
    def __init__(self, endpoint, get_function, post_function):
        self._get_function = get_function
        self._post_function = post_function

        super().__init__(endpoint)

    def do_GET(self, handler, *args):
        self._get_function(handler, *args)

    def do_POST(self, handler, *args):
        self._post_function(handler, *args)

class WebServer(HTTPServer):
    def __init__(self, *args):
        self._handlers = []
        super().__init__(*args)

    def add_handler(self, handler):
        self._handlers.append(handler)

    def get_handler_by_endpoint(self, endpoint):
        for handler in self._handlers:
            if handler.get_endpoint() == endpoint:
                return handler

        return BaseHandler("")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parsed.query
        params = parsed.params

        handler = self.server.get_handler_by_endpoint(path)
        
        if handler.get_endpoint() == "":
            self.send_response(404)
        else:
            handler.do_GET(self, query, params)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parsed.query
        params = parsed.params

        handler = self.server.get_handler_by_endpoint(path)

        if handler.get_endpoint() == "":
            self.send_response(404)
        else:
            handler.do_POST(self)
