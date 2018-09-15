import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup as bs

def get_content_size(url, proxy_dict={}):
    """ Returns content size of data requested from a particular URL

    :param url: URL to retrieve content size of.
    :param proxy_dict: in case the system requires proxy
    """
    if not url.startswith("data:"):
        response = requests.head(url, proxies=proxy_dict)
        if 'content-length' in response.headers:
            return int(response.headers['content-length'])
    return 0

def get_link_data(url, proxy_dict={}):
    """ Returns the BeautifulSoup object created by parsing the content
    received as response of sending GET request to the base_url.

    :param url: URL to retrieve the html content from
    :param proxy_dict: in case the system requires proxy
    """
    try:
        r = requests.get(url, proxies=proxy_dict)
        data = bs("".join(r.text), "html.parser")
        return data
    except ConnectionError as e:
        print("Link read error")
        exit(0)

def get_total_pages(url, proxy_dict={}):
    """ Returns the total number of pages in the current issue.

    :param url: URL to retrieve the html content from
    :param proxy_dict: in case the system requires proxy
    """
    data = get_link_data(url, proxy_dict)
    dropdowns = data.findAll('select')
    for dropdown in dropdowns:
        options = dropdown.findAll('option')
        if len(options) and options[-1].get_text().isnumeric():
            return int(options[-1].get_text())
