import requests
from string import Template
from .constants import osrs_wiki_base_url

class OsrsWikiLink(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def __str__(self):
        return f"Name: {self.name} Link: {self.url}"

    def get_markdown(self):
        return f"[{self.name}]({self.url})"

class OsrsWikiSearchResult(object):
    def __init__(self, query, links : list):
        self.query = query
        self.links = links

    def get_query(self):
        return self.query
    
    def get_links(self):
        return self.links
        

def fetch_results(query):
    query_clean = query.replace(" ", "_")
    url = Template('${baseurl}action=opensearch&search=${squery}&format=json&limit=10').substitute(
                   baseurl=osrs_wiki_base_url, squery=query_clean)
    try:
        payload = requests.get(url)
    except Exception as e:
        raise e
    else:
        return payload.json()

def parse_payload(payload):
    query = payload[0]
    names = payload[1]
    urls = payload[3]
    links = []
    for name, url in zip(names, urls):
        links.append(OsrsWikiLink(name, url))
    return OsrsWikiSearchResult(query, links)

def search(query):
    try:
        payload = fetch_results(query)
        result = parse_payload(payload)
    except Exception as e:
        raise e
    else:
        return result
        
