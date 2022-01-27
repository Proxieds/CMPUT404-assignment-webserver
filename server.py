#  coding: utf-8
import socketserver
# Import os for handling path joins
import os
# Handling other mimetypes like application/octet-stream, etc.
import mimetypes

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
# https://docs.python.org/3/library/socketserver.html
# HTTP Part II Notes for formatting response
# https://stackoverflow.com/questions/21153262/sending-html-through-python-socket-server
# https://docs.python.org/3/library/mimetypes.html

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

    def move_path(self, path):
        """
        Function for checking the provided path, adding path endings when needed and returning the mime_type
        """
        # Join path from current working directory, have it only serve files after ./www
        joined_path = os.path.join(os.getcwd(), 'www' + path)
        if not joined_path.endswith('/') and not os.path.isfile(joined_path):
            joined_path += '/'
            if os.path.exists(joined_path):
                # Send a 301 Moved Permanently status code if a path exists after adding path ending
                self.send_content("moved")
        if not os.path.isfile(joined_path):
            joined_path += 'index.html'

        return joined_path

    def send_content(self, status, path=None):
        """
        Function for sending content and HTTP status code responses
        """
        # Path was provided, send some additional content, otherwise just send status code
        if path:
            # Try and convert the path to a mimetype
            try:
                # Old method for handling mimetypes, would not work with other types in the future, using stdlib mime_types instead 
                # mime_type = "text/css" if path.endswith(".css") else "text/html"
                mime_type = mimetypes.guess_type(path)[0]
                with open(path, 'r+b') as file:
                    content = file.read()
                    self.request.sendall(
                        bytearray(statusCodes[status], 'utf-8'))
                    self.request.sendall(
                        bytearray("Content-Type: {}\r\n".format(mime_type), 'utf-8'))
                    self.request.sendall(
                        bytearray("Content-Length: {}\r\n\r\n".format(len(content)), 'utf-8'))
                    self.request.sendall(content)
                    file.close()
            except:
                self.request.sendall(
                    bytearray(statusCodes["notFound"], 'utf-8'))

        # If no path is provided, print the status code
        else:
            self.request.sendall(bytearray(statusCodes[status], 'utf-8'))

    def handle(self):
        # Responses should be in HTTP/1.1 since this is a 1.1 compliant web server
        self.data = self.request.recv(BUFFER_SIZE).strip()
        print("Got a request of: %s\n" % self.data)
        # Split data and extract the request method and protocol
        parsedData = self.data.decode().split()
        requestMethod, path = parsedData[0], parsedData[1]
        print("Request Method: %s, Path: %s" % (requestMethod, path))

        # Handle Get Requests
        if requestMethod == "GET":
            file_path = self.move_path(path)

            # Check if the path exists, if it does, send the content along with a 200 status code
            if os.path.exists(file_path):
                self.send_content("OK", file_path)
            else:
                # Send a 404 error code otherwise
                self.send_content("notFound")

        # Return a 405 status code for other types of non-supported request methods (POST/PUT/DELETE)
        else:
            self.send_content("notAllowed")


if __name__ == "__main__":

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
