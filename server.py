#  coding: utf-8
import socketserver
# Import os for handling path joins
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Victor Lieu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# Resources used for this assignment:
# https://docs.python.org/3/library/os.path.html


# Define host url and port number
HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 1024

"""
Dictionary for handling certain HTTP status codes in HTTP1.1 for this assignment
"""
statusCodes = {
    "OK": "HTTP/1.1 200 OK\r\n",
    "moved": "HTTP/1.1 301 Moved Permanently\r\n",
    "notFound": "HTTP/1.1 404 Not Found\r\n",
    "notAllowed": "HTTP/1.1 405 Method Not Allowed\r\n"
}


class MyWebServer(socketserver.BaseRequestHandler):

    def handle_mimetype(self, path):
        """
        Function for checking the provided path and returning the mime_type
        """
        if path.endswith(".css"):
            return "text/css"

        return "text/html"

    def send_request(self, status, path=None):
        """
        Function for sending content and HTTP status code responses
        """
        # Path was provided, send some additional content, otherwise just send status code
        if path:
            # Try and convert the path to a mimetype
            try:
                mime_type = self.handle_mimetype(path)
                f = open(path, 'r+b')
                content = f.read()
                self.request.sendall(bytearray(statusCodes["OK"], 'utf-8'))
                self.request.sendall(
                    bytearray("Content-Type: {}\r\n".format(mime_type), 'utf-8'))
                self.request.sendall(
                    bytearray("Content-Length: {}\r\n".format(len(content)), 'utf-8'))
                self.request.sendall(
                    bytearray("Connection: close\r\n", 'utf-8'))
                self.request.sendall(bytearray("\r\n", 'utf-8'))
                self.request.sendall(content)
                f.close()
            except:
                self.request.sendall(
                    bytearray(statusCodes["notFound"], 'utf-8'))
        else:
            self.request.sendall(bytearray(statusCodes["notFound"], 'utf-8'))

    def handle(self):
        # Responses should be in HTTP/1.1 since this is a 1.1 compliant web server
        self.data = self.request.recv(BUFFER_SIZE).strip()
        print("Got a request of: %s\n" % self.data)
        # Split data and extract the request method and protocol
        parsedData = self.data.split()
        requestMethod, path = parsedData[0], parsedData[1]
        print("Request Method: %s, Path: %s" % (requestMethod, path))

        # Handle Get Requests
        if requestMethod == "GET":
            # Join path from current working directory, have it only serve files after ./www
            joined_path = os.path.join(os.getcwd(), 'www' + path)
            if not joined_path.endswith('/') and not os.path.isfile(joined_path):
                joined_path += '/'
                self.send_request("moved")
            # Check that the absolute path of the joined path is www so no other directories are accessed
            # if not os.path.abspath(joined_path).endswith('www'):
            #     print("NOT FOUNDS")
            #     self.send_request("notFound")
            # else:
            if not os.path.isfile(joined_path):
                joined_path += 'index.html'
            self.send_request("OK", joined_path)
            # Return a 405 status code for other types of non-supported request methods (POST/PUT/DELETE)
        else:
            self.send_request("notAllowed")


if __name__ == "__main__":

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
