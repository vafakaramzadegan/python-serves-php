import time
from core.config import server_config


def render_error_page(code):
    # get current timestamp
    now = time.strftime('%b %d %Y %H:%M:%S', time.localtime())

    if code == 302:
        # redirect does not require output
        return ''
    elif code == 403:
        title = '403 Forbidden'
        desc = 'This may be due to not having the necessary permissions for the resource.'
    elif code == 404:
        title = '404 Not Found'
        desc = 'The requested resource could not be found but may be available in the future.<br/>Subsequent requests are permissible.'
    elif code == 500:
        title = '500 Internal Error'
        desc = 'Ooops! :('
    else:
        return ''

    # error page template
    template = (
        '<!DOCTYPE html>'
        '<html>'
            '<head>'
                '<meta charset="utf-8">'
                '<title></title>'
            '</head>'
            '<style>'
                'body{padding:16px;font-family:tahoma}'
                'a{text-decoration:none}'
                'h1{margin-top:0;margin-bottom:24px;}'
                '.sig{margin-top:48px;font-size:12px}'
            '</style>'
            '<body>'
                f'<h1>{title}</h1>'
                f'<p>{desc}</p>'
                f'<div class="sig">Generated on: {now}<br/><br/><b>{server_config.server_version}</b>&nbsp;-&nbsp;<a href="{server_config.server_website}">{server_config.server_website}</a></div>'
            '</body>'
        '</html>'
    )
        
    return template