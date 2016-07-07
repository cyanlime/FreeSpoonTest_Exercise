import urlparse
from urllib import urlencode

def addQueryParams(url, params):
    url_parts = list(urlparse.urlparse(url))
    query = urlparse.parse_qs(url_parts[4])
    query.update(params)

    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)

def totalMicroseconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) 