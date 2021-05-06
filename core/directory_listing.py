import os, platform, time
from core.config import server_config


# get last modified time of file
def get_mtime(path_to_file):
    t = 0
    if platform.system() == 'Windows':
        t = os.path.getmtime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        t = stat.st_mtime

    return time.ctime(t)


def list_files_in_dir(uri, path):
    # get current timestamp
    now = time.strftime('%b %d %Y %H:%M:%S', time.localtime())
    # list files and folders in the given path
    files = []
    dirs = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        dirs.extend(dirnames)
        files.extend(filenames)
        break
    # generate output html
    template = (
        '<!DOCTYPE html>'
        '<html>'
            '<head>'
                '<meta charset="utf-8">'
                f'<title>Index of {uri}</title>'
                '<link rel="stylesheet" href="//cdn.jsdelivr.net/npm/file-icon-vectors@1.0.0/dist/file-icon-vivid.min.css" />'
            '</head>'
            '<style>'
                'body{padding:16px;font-family:tahoma}'
                'a{text-decoration:none}'
                'h1{margin-top:0;margin-bottom:24px;}'
                '.sig{margin-top:48px;font-size:12px}'
                'table{border:solid 1px #aaa;border-left:none;border-right:none;border-collapse:collapse}'
                'table th{text-align:left;border-bottom:solid 1px #aaa;background:#f5f5f5}'
                'table td{padding-right:24px}'
                'table td:not(:first-of-type){font-size:12px;}'
            '</style>'
            '<body>'
                f'<h1>Index of {uri}</h1>'
                '<table>'
                    '<thead>'
                        '<th>Name</th>'
                        '<th>Modified</th>'
                        '<th>Size</th>'
                    '</thead>'
                    '<tbody>'
    )
    for d in dirs:
        template += (
            '<tr>'
                f'<td><a href="{uri}{d}/"><span class="fiv-viv fiv-icon-folder"></span>&nbsp;{d}</a></td>'
                f'<td>{get_mtime(path)}</td>'
                '<td>-</td>'
            '</tr>'
        )
    for f in files:
        abs_path = os.path.join(path, f)
        f_size = '{:.2f}'.format(os.path.getsize(abs_path)/1024)
        template += (
            '<tr>'
                f'<td><a href="{uri}{f}"><span class="fiv-viv fiv-icon-{os.path.splitext(f)[1][1:]}"></span>&nbsp;{f}</a></td>'
                f'<td>{get_mtime(abs_path)}</td>'
                f'<td>{f_size} KiB</td>'
            '</tr>'
        )
    template += (
                    '</tbody>'
                '</table>'
                f'<div class="sig">Generated on: {now}<br/><br/><b>{server_config.server_version}</b>&nbsp;-&nbsp;<a href="{server_config.server_website}">{server_config.server_website}</a><br/>Icons by:&nbsp;<a href="https://github.com/dmhendricks/file-icon-vectors">https://github.com/dmhendricks/file-icon-vectors</a></div>'
            '</body>'
        '</html>'
    )
        
    return template