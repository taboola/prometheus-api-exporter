import json

import requests


class HttpManager:
    TIMEOUT = 30

    def __init__(self):

        self.__ensure_connector()

    def __ensure_connector(self):
        requests.packages.urllib3.disable_warnings()
        self.request = requests.session()
        self.request.headers.update({'content-type': 'application/json'})

    def query(self, url, method='get', status_expected=200, data=None):

        if method == 'get':
            response = self._get_query(url)
        elif method == 'post':
            response = self._post_query(url, data)
        else:
            return None

        return self._parse_content(response, status_expected)

    def _get_query(self, url):

        return self.request.get(
            url,
            verify=False,
            timeout=self.TIMEOUT,
        )

    def _post_query(self, url, data):

        return self.request.get(
            url,
            verify=False,
            timeout=self.TIMEOUT,
        )

    def _parse_content(self, response, status_expected):
        if response.status_code == status_expected:
            return json.loads(response.content)
        else:
            return None
