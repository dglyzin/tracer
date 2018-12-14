# parser$ ~/anaconda3/bin/python3 -m translator.tokenizer.io.server.server_main

import tornado
import tornado.ioloop
import tornado.web
import os
import json
from translator.tokenizer.io.model.model_main import TokenizerDB
from translator.tokenizer.io.server.server_handlers_special import DialectHandlers


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
        (r"/login", handlers.SignInHandler),
        (r"/logout", handlers.LogoutHandler),
        (r"/signup", handlers.SignUpHandler),

        #api
        # (r"/api/tree", TreeHandler),
        # (r"/api/editor", EditorHandler),
        # (r"/api/net", NetHandler),
        (r"/api/tables/path", handlers.PathHandler),
        (r"/api/tables/dialect", handlers.DialectTableHandler),
        (r"/api/tables/user", handlers.UsersTableHandler),

        # statics from /client folder
        (r"/static/", tornado.web.StaticFileHandler,
         dict(path=settings['static_path'])), ], **settings)


if __name__ == "__main__":

    model = TokenizerDB()
    model.load_all_tables()

    handlers = DialectHandlers(model)

    app = make_app(handlers)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
