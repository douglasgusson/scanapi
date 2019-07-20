#!/usr/bin/env python3

import json
import logging
import requests


class CodeBlock:
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        self.file.write("\n```\n")

    def __exit__(self, type, value, traceback):
        self.file.write("\n```\n")


class HTTPMessageWriter:
    def __init__(self, message, file):
        self.message = message
        self.file = file

    def write_headers(self):
        self.file.write("\nHEADERS:\n")
        if not self.message.headers:
            self.file.write("None\n")
            return

        with CodeBlock(self.file):
            json.dump(dict(self.message.headers), self.file, indent=2)


class RequestWriter(HTTPMessageWriter):
    def __init__(self, request, file):
        HTTPMessageWriter.__init__(self, request, file)
        self.request = request

    def write(self):
        self.file.write(
            "### Request: {} {}\n".format(self.request.method, self.request.url)
        )
        self.write_headers()
        self.write_body()

    def write_body(self):
        self.file.write("\nBODY:\n")

        if not self.request.body:
            self.file.write("None\n")
            return

        with CodeBlock(file):
            json.dump(dict(self.request.body), docs, indent=2)


class ResponseWriter(HTTPMessageWriter):
    def __init__(self, response, file):
        HTTPMessageWriter.__init__(self, response, file)
        self.response = response

    def write(self):
        self.file.write("\n### Response: {}\n".format(self.response.status_code))
        self.write_is_redirect()
        self.write_headers()
        self.write_content()

    def write_is_redirect(self):
        self.file.write("\nIs redirect? {}\n".format(self.response.is_redirect))

    def write_content(self):
        self.file.write("\nContent:\n")

        if not self.response.content:
            self.file.write("None\n")
            return

        with CodeBlock(self.file):
            json.dump(self.response.json(), self.file, indent=2)


class DocsWriter:
    def __init__(self, file_path):
        self.file_path = file_path

    def write(self, responses):
        open(self.file_path, "w").close()
        [self.write_response(response) for response in responses]

    def write_response(self, response):
        request = response.request

        if "application/json" not in response.headers["Content-Type"]:
            print(
                "Error: response is not a JSON: \n\tContent-Type: {} \n\tRequest: {} \n\tResponse {}: {}".format(
                    response.headers["Content-Type"],
                    request.url,
                    response.status_code,
                    response.content,
                )
            )
            return

        with open(self.file_path, "a", newline="\n") as docs:
            RequestWriter(request, docs).write()
            ResponseWriter(response, docs).write()


def scan_api():
    responses = []
    responses.append(requests.get("https://cheesecakelabs.com/challenge/"))
    responses.append(requests.get("http://dummy.restapiexample.com/api/v1/employees"))
    responses.append(requests.get("https://jsonplaceholder.typicode.com/todos/1"))
    responses.append(requests.get("https://jsonplaceholder.typicode.com/posts"))

    return responses


if __name__ == "__main__":
    responses = scan_api()
    DocsWriter("docs.md").write(responses)
