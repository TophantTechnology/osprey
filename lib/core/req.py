import requests
from requests.hooks import default_hooks
from requests.models import DEFAULT_REDIRECT_LIMIT
from requests.cookies import cookiejar_from_dict
from requests.compat import OrderedDict
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict


def request_init(headers, proxies, params, cookies=cookiejar_from_dict({})):
    def set_request_headers(headers, proxies, params, cookies):
        def session_init(self):
            self.headers = CaseInsensitiveDict(headers)
            self.auth = None
            self.proxies = proxies
            self.hooks = default_hooks()
            self.params = params
            self.stream = False
            self.verify = False
            self.cert = None
            self.max_redirects = DEFAULT_REDIRECT_LIMIT
            self.trust_env = True
            self.cookies = cookies
            self.adapters = OrderedDict()
            self.mount('https://', HTTPAdapter())
            self.mount('http://', HTTPAdapter())
        requests.sessions.Session.__init__ = session_init

    set_request_headers(headers, proxies, params, cookies)
