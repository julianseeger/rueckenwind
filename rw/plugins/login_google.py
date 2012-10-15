import os
import time

from rw.www import RequestHandler, get, post, url_for
from tornado.auth import GoogleMixin
import rplug

PATH = os.path.expanduser('~/.rw/')
DB_PATH = PATH + 'plugins.mail_local'


class Mail(object):
    def __init__(self, toaddrs, subject, body):
        self.toaddrs = toaddrs
        self.subject = subject
        self.body = body
        self.time = time.time()


class GoogleLogin(rplug.rw.login):
    def handler(self):
        class GoogleLoginHandler(RequestHandler, GoogleMixin):
            @get('/')
            def index(self):
                if self.get_argument('openid.mode', None):
                    self.get_authenticated_user(self._on_auth)
                    return
                url = self.request.protocol + '//' + self.request.host
                self.authenticate_redirect(callback_uri=url)

            def _on_auth(self, user):
                if not user:
                    raise tornado.web.HTTPError(500, "Google auth failed")
                # Save the user with, e.g., set_secure_cookie()
                self.set_secure_cookie('email', user['email'])
                self.redirect('/')
        return GoogleLoginHandler


class GoogleLoginRequestProcessing(rplug.rw.request_handling):
    def pre_process(self, handler):
        handler['email'] = handler.get_secure_cookie('email', None)


def activate():
    GoogleLogin.activate()
    GoogleLoginRequestProcessing.activate()
