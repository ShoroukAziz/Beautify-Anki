import  os, re
from aqt.mediasrv import RequestHandler
from anki.hooks import wrap

materialize_path = "assets/materialize.css"
fonts_path = "assets/flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2"


FILES = re.compile(r'\.(?:jpe?g|gif|css|woff2|png|tiff|bmp)$', re.I) #Perl FTW! <3

RES_DIR = 'assets'
FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), RES_DIR))

def _redirectWebExports(self, path, _old):
    targetPath = os.path.join(os.getcwd(), RES_DIR, '')
    if path.startswith(targetPath):
        return os.path.join(FILES_DIR, path[len(targetPath):])
    return _old(self,path)

RequestHandler._redirectWebExports = wrap(RequestHandler._redirectWebExports, _redirectWebExports, 'around')
