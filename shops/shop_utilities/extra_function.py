import urllib.parse as urlparse


def prepend_domain(url, domain_url):
    if domain_url is None:
        return url
    if url is not None:
        split_url = urlparse.urlsplit(url)
        if not split_url.scheme:
            if not split_url.netloc:
                split_domain = urlparse.urlsplit(domain_url)
                domain = "{}://{}".format(split_domain.scheme, split_domain.netloc)
                return urlparse.urljoin(domain, url)
            url = "https://{}".format(url.replace("//", ""))
    return url
