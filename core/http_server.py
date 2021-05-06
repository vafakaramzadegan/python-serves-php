from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from core.config import server_config
import time, os, subprocess, re
from core.error_pages import render_error_page


class HttpServer(BaseHTTPRequestHandler):

    # pattern to compare url against
    filename_pattern = re.compile(r'([\w]+(\.[\w]+)+)*$', re.I)
    path_pattern = re.compile(r'\/((\w+\/*)*)$', re.I)

    def __init__(self, *args, **kwargs):
        # initialize parent(BaseHTTPRequestHandler)
        super().__init__(*args, **kwargs)
        # set custom server information
        self.server_version = server_config.server_version
        self.sys_version = ''

    # handles common errors that may occur before calling php-cgi
    def error(self, code):
        if code == 302:
            self.c_headers['Status'] = '302 Found'
        elif code == 403:
            self.c_headers['Status'] = '403 Forbidden'
        elif code == 404:
            self.c_headers['Status'] = '404 Not Found'
        else:
            self.c_headers['Status'] = '500 Internal Error'
        self.send_text(render_error_page(code))
        exit()

    # resets the list of headers to be sent to browser
    def reset(self):
        self.c_headers = {
            'Content-type': 'text/html',
            'Pragma': 'no-cache',
            'cache-control': 'no-store, no-cache, must-revalidate',
            'x-xss-protection': '1; mode=block'
        }

    # server must be able to send any filetypes rather than just executing php scripts
    def send_file(self, path):
        f = open(path, 'rb')
        self.send_response(200)
        # content-type header is sent automatically based on file extension
        self.send_header('Content-type', server_config.mime_types[os.path.splitext(path)[1][1:]])
        self.end_headers()
        self.wfile.write(f.read())
        f.close()
        exit()

    # send text to browser
    def send_text(self, data):
        # set response code to 200 if not already set by PHP script
        code = 200 if 'Status' not in self.c_headers else int(''.join(x for x in self.c_headers['Status'] if x.isdigit()))
        self.send_response(code)
        # send headers to browser
        for k, v in self.c_headers.items():
            self.send_header(k, v)
        self.end_headers()
        # send data to browser
        self.wfile.write(bytes(data, 'utf-8'))
        exit()

    # parse php headers and prepare them to be sent to browser
    def add_php_headers(self, headers):
        items = headers.split('\n')
        for h in items:
            k = h.split(':')[0]
            v = h.split(':')[1]
            self.c_headers[k] = v

    # analise the url and find out what to do with it
    def resolve_url(self, url):
        parsed = urlparse(url)
        # check if url points to a valid filename
        check = self.filename_pattern.search(parsed.path)
        if (not check or not check.group(0)) and parsed.path != '/':
            # we have a path.
            # check if the path contains trailing slash. if not,
            # add a slash, append query string and redirect to the correct path.
            check = self.path_pattern.search(parsed.path)
            if check and check.group(0):
                if not check.group(1).endswith('/'):
                    query = '?' + parsed.query if parsed.query != '' else ''
                    self.c_headers['Location'] = f'{parsed.path}{os.sep}{query}'
                    self.error(302)

        # the url is validated now and we can move on
        fn = unquote(f'{server_config.document_root}{parsed.path}')
        # if the url is not pointing to a specific file, we should
        # check if there's an index.php or index.html file in the path
        # and execute them automatically.
        if not os.path.isfile(fn):
            for item in server_config.exec_order:
                tmp = f'{server_config.document_root}{parsed.path}{os.sep}{item}'
                if os.path.isfile(tmp):
                    fn = tmp
                    break
        # check if the url is pointing to a directory.
        # list the files inside directory if directory_listing is enabled,
        # otherwise throw 403 error.
        if os.path.isdir(fn):
            if server_config.directory_listing:
                from core.directory_listing import list_files_in_dir
                self.send_text(list_files_in_dir(self.path, fn))
            else:
                self.error(403)
        # the url seems to be pointing to a file rather than a directory,
        # check if the file exists.
        if not os.path.isfile(fn):
            self.error(404)
        # send the file to the browser if it's not a php file
        if not os.path.splitext(fn)[1] in ['.php']:
            self.send_file(fn)

        # we sure have a php file to be executed.
        return fn, parsed.query

    # execute php script through cgi
    def execute_cgi_command(self, command):
        sp = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        res, err = sp.communicate()
        if err and not server_config.display_errors:
            self.error(500)
        if res:
            # split headers and body recieved from cgi.
            data = res.decode().split('\r\n\r\n')
            self.add_php_headers(data[0])
            if len(data) > 1:
                self.send_text(res.decode()[len(data[0]):])

    # handle GET requests
    def do_GET(self):
        self.reset()
        fn, qs = self.resolve_url(self.path)

        self.execute_cgi_command(f'{server_config.php_path}php-cgi {fn} {qs}')

    # handle POST requests
    def do_POST(self):
        self.reset()
        fn, qs = self.resolve_url(self.path)
        post_data = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        # build the cgi command.
        # POST requests may also have GET parameters, so both {qs} and
        # {post_data} will be passed to cgi.
        command = (
            'export GATEWAY_INTERFACE="CGI/1.1"\n'\
            f'export SCRIPT_FILENAME={fn}\n'\
            'export REQUEST_METHOD="POST"\n'\
            'export REDIRECT_STATUS=true\n'\
            'export SERVER_PROTOCOL="HTTP/1.1"\n'\
            f'export CONTENT_LENGTH={len(post_data)}\n'\
            'export CONTENT_TYPE="application/x-www-form-urlencoded"\n'\
            f'echo "{post_data}" | {server_config.php_path}php-cgi {qs}'
        )

        self.execute_cgi_command(command)