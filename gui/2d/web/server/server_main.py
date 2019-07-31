# parser$ ~/anaconda3/bin/python3 -m gui.web.server.server_main

import tornado
import tornado.ioloop
import tornado.web
import os

from server.server_handlers import Handlers


class MyStaticFileHandler(tornado.web.StaticFileHandler):

    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control',
                        ('no-store, no-cache,'
                         + ' must-revalidate, max-age=0'))
            

def make_app(handlers):
    settings = {
        "template_path": os.path.join(os.path
                                      .dirname(os.path
                                               .dirname(__file__)),
                                      "client", "templates"),
        "static_path": os.path.join(os.path
                                    .dirname(os.path
                                             .dirname(__file__)),
                                    "client"),
        "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        "login_url": "/login",
        "xsrf_cookies": False,
        "debug": True,
    }
    print("template_path:")
    print(settings["template_path"])

    return tornado.web.Application([
        #html
        (r"/", handlers.MainHandler),
        
        #api
        # (r"/api/tree", TreeHandler),
        # (r"/api/editor", EditorHandler),

        # statics from /client folder
        (r"/static/", MyStaticFileHandler,
         dict(path=settings['static_path'])), ], **settings)


if __name__ == "__main__":

    handlers = Handlers()

    app = make_app(handlers)
    port = 8888
    print("http://localhost:" + str(port) + "/")
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
