# Python Serves PHP
A simple web server for PHP. python-serves-php just wraps around python's built-in `HTTPServer`.
It uses custom URL processing schemes and is particularly designed to execute PHP scripts through CGI.

### Features:

- [x] Handles each request in a separate thread using `ThreadingMixIn`
- [x] GET requests
- [x] POST requests
- [x] Supports directory index files: `index.php index.html ...`
- [x] Provides `http.ini` file to configure the server
- [x] supports HTTPS
- [x] Custom error pages
- [x] Custom Directory Listing

### TO-DO:

- [ ] Handle file uploads
- [ ] Ability to rewrite requested URLs (forwarding requests to a single PHP file)

___
NOTE: do not use this as a production server. Security measures have not been implemented.
___

## Usage
By default, the `www` directory is set as the root. put your files inside it and run the server:

`$ python main.py`

next, navigate to `localhost` in your browser.
