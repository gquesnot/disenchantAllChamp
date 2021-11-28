import requests


class Session:
    def __init__(self, protocol, adress, port, headers):
        self.session = requests.session()
        self.session.headers.update(headers)
        self.headers = headers
        self.baseUrl = '{}://{}:{}'.format(protocol, adress, port)

    def request(self, method, path, data=""):
        fn = getattr(self.session, method)
        if method == "get":
            if data == "":
                return fn("{}{}".format(self.baseUrl, path), verify=False)
            else:
                return fn("{}{}?{}".format(self.baseUrl, path, data), verify=False)
        else:
            if data == "":
                return fn("{}{}".format(self.baseUrl, path), verify=False)
            else:
                return fn("{}{}".format(self.baseUrl, path), json=data, verify=False)
