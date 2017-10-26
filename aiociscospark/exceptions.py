class SparkResponseError(Exception):
    @classmethod
    async def get(cls, http_resp, session=None):
        text = await http_resp.text()
        try:
            json = await http_resp.json()
        except Exception:
            json = {}
        finally:
            http_resp.close()

        if session:
            session.close()

        return cls(http_resp, text=text, json=json)

    def __init__(self, response, text=None, json=None):
        """
        A helper class to give some human readable meaning to errors returned from Spark.

        :param response: `aiohttp.ClientResponse` object
        :return:
        """
        self._response = response

        self.status = response.status
        self.reason = response.reason
        self.headers = response.headers
        self.text = text
        self.json = json or {}

        self.error_code = self.json.get('errorCode')
        self.tracking_id = self.json.get('trackingId')
        self.message = self.json.get('message')
        self.errors = self.json.get('errors')

    def __str__(self):
        request_descr = f"{self._response.method} {self._response.url}"
        if self.json:
            err = "Request: %s. Reply [%d]: %r. " \
                  "errorCode=%s, errors=%s" % (request_descr, self.status,
                                               self.message, self.error_code,
                                               self.errors)
        else:
            err = "Request: %s. Reply [%d]: %.120r. " \
                  "Headers: %r" % (request_descr, self.status, self.text, self.headers)
        return err


class SparkRateLimitExceeded(SparkResponseError):

    @property
    def retry_after(self):
        return int(self.headers['Retry-After'])


class SparkResponseNotReceived(Exception):
    pass


class SparkClientConfigurationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
