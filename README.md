# python-serves-php
A simple web server for PHP. python-serves-php just wraps around python's built-in `HTTPServer`.
It uses custom URL processing schemes, and is particularly designed to execute PHP scripts through CGI.

python-serves-php has following features:

* Handles each request in a saparate thread using `ThreadingMixIn`
* GET requests
* POST requests
* Supports directory index files: `index.php index.html`
* Provides `http.ini` file to configure the server
* supports HTTPS
* Custom error pages
* Custom Directory Listing
