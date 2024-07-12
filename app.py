import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
import urllib.robotparser
import time
import validators
import xml.etree.ElementTree as ET
import random
from datetime import datetime
import re
from db import do_db

robot_txt_data = ""
sitemap_data = ""
visited_urls = set()
queue:[str] = []

def is_unicode_escape_sequence(string):
  pattern = r"\\([uU][0-9a-fA-F]{4,8})"
  return bool(re.search(pattern, string))

def convert_unicode_escape(string):
  result = ""
  i = 0
  while i < len(string):
    if string[i] == '\\':
      if i + 1 < len(string):
        if string[i+1] == 'u' or string[i+1] == 'U':
          # Extract hexadecimal code and handle potential errors
          try:
            code_length = 4 if string[i+1] == 'u' else 8
            code = int(string[i+2:i+2+code_length], 16)
            result += chr(code)
            i += code_length + 1
          except ValueError:
            # Handle invalid escape sequences gracefully (e.g., replace with a placeholder)
            result += "\\" + string[i+1]  # Preserve invalid escape sequence
            i += 2
        else:
          # Handle other escape sequences like \n, \t, etc.
          result += string[i+1]
          i += 2
      else:
        # Handle trailing backslash
        result += string[i]
        i += 1
    else:
      result += string[i]
      i += 1
  return result


def get_timestamp():
    curr_dt = datetime.now()
    timestamp = int(round(curr_dt.timestamp()))
    return timestamp

def get_useragent():
    with open('browser_agents.txt', 'r') as file_handle:
        USER_AGENTS = file_handle.read().splitlines()
    return random.choice(USER_AGENTS)

def extract_domain(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}/"

def get_sitemap_data(url):
    """Fetches data from sitemap.xml."""
    sitemap_url = urljoin(url, "/sitemap.xml")
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def parse_sitemap_data(xml_content):
    """Parses sitemap XML data and returns a dictionary of URLs with last modified date and change frequency."""
    root = ET.fromstring(xml_content)
    urls_data = {}
    for child in root:
        if child.tag.endswith('url'):
            loc = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text.strip()
            lastmod = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            last_modified = lastmod.text.strip() if lastmod is not None else ""
            changefreq = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
            change_frequency = changefreq.text.strip() if changefreq is not None else ""
            priority_parent = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
            priority = priority_parent.text.strip() if priority_parent is not None else ""
            urls_data[loc] = {
                "last_modified": last_modified,
                "change_frequency": change_frequency,
                "priority": priority
            }
    return urls_data

def is_allowed(robot_parser, url, user_agent="*"):
    return robot_parser.can_fetch(user_agent, url)


def crawl(current_url, user_agent, robot_parser, delay=0.5):
        global visited_urls
        global sitemap_data
        global queue
        parsed_url = urlparse(current_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        if current_url not in visited_urls and is_allowed(robot_parser, base_url, user_agent):
            try:
                response = requests.get(current_url, headers={"User-Agent": user_agent})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    robot = False
                    robots_root = soup.find("meta", attrs={"name": "robots"})
                    if robots_root:
                        robots_val = robots_root["content"].strip()
                        if robots_val == "noindex":
                            robot = True
                    if robot == False:
                        title = soup.title.text.strip() if soup.title else ""
                        if is_unicode_escape_sequence(title):
                            title = convert_unicode_escape(title)
                        description = ""
                        meta_description = soup.find("meta", attrs={"name": "description"})
                        if meta_description:
                            description = meta_description["content"].strip()
                        else:
                            for paragraph in soup.find_all("p"):
                                description += paragraph.text.strip()[:100]  # Limit snippet length
                                break
                        if is_unicode_escape_sequence(description):
                           description = convert_unicode_escape(description)

                        last_modified = ""
                        change_frequency = ""
                        priority = ""
                        if current_url in sitemap_data:
                            last_modified = sitemap_data[current_url]["last_modified"]
                            change_frequency = sitemap_data[current_url]["change_frequency"]
                            priority = sitemap_data[current_url]["priority"]
                        
                        # Save information in JSON format
                        data = {
                            "url": current_url,
                            "title": title,
                            "description": description,
                            "sm_last_modified": last_modified, #sm_ denotes sitemap
                            "sm_change_freq" : change_frequency,
                            "sm_priority" : priority,
                            "crawled_on" : get_timestamp()
                        }
                        do_db(data)

                        visited_urls.add(current_url)

                        # Extract links from the page
                        links = soup.find_all("a", href=True)
                        for link in links:
                            absolute_link = urljoin(current_url, link.get('href'))
                            if validators.url(absolute_link):
                                queue.append(absolute_link)
                        #Sorting with current domain
                        current_url_array = [url for url in queue if url.startswith(extract_domain(current_url))]
                        other_urls = [url for url in queue if url not in current_url_array]
                        queue = current_url_array + other_urls

                        # Add a delay to avoid overloading the server
                        time.sleep(delay)
            except Exception as e:
                print(f"Error crawling {current_url}: {e}")

def preppare_crawler(base_urls:[str]):
    """Crawls a given URL and saves information in JSON format."""
    global queue
    global sitemap_data
    queue = base_urls
    parser = urllib.robotparser.RobotFileParser()
    current_running_domain = ""
    while queue:
        current_url = queue.pop(0)
        if current_running_domain != extract_domain(current_url):
            current_running_domain = extract_domain(current_url)
            parser.set_url(current_url)
            parser.read()
        # Fetch URLs from sitemap.xml if available
        if extract_domain(current_url) not in sitemap_data:
            sitemap_data_raw = get_sitemap_data(extract_domain(current_url))
            sitemap_data = parse_sitemap_data(sitemap_data_raw) if sitemap_data_raw else {}
        crawl(current_url=current_url, user_agent=get_useragent(), robot_parser=parser, delay=random.uniform(0.2, 2.0))

if __name__ == "__main__":
    seed_url_global = ["https://www.wikipedia.org/", "https://www.google.com/", "https://www.bing.com/", "https://www.x.com/"]
    seed_urls_us = ["https://www.nationalgeographic.com/", "https://www.nytimes.com/", "https://www.technologyreview.com/", "https://www.washingtonpost.com/", "https://www.si.edu/", "https://www.theatlantic.com/"]
    seed_url_europe = ["https://www.bbc.com/", "https://www.theguardian.com/", "https://www.economist.com/"]
    seed_url_india = ["https://www.thehindu.com/", "https://www.timesofindia.com/", "https://economictimes.indiatimes.com/", "https://www.india.gov.in/", "https://www.iitk.ac.in/", "https://www.iisc.ac.in/"]
    seed_url_asia = ["https://www3.nhk.or.jp/", "https://www.channelnewsasia.com/"]
    seed_url_latin_americas = ["https://english.elpais.com/", "https://www.folha.uol.com.br/", "https://www.telemundo.com/"]
    seed_url_africa = ["https://theconversation.com", "https://allafrica.com/"]
    seed_url_middle_east = ["https://www.aljazeera.net/", "https://www.jpost.com/", "https://www.tehrantimes.com/"]
    seed_url_australia = ["https://www.abc.net.au/", "https://www.smh.com.au/", "https://www.theage.com.au/"]
    seed_url = seed_url_global + seed_urls_us + seed_url_europe + seed_url_india + seed_url_asia + seed_url_latin_americas + seed_url_africa + seed_url_middle_east + seed_url_australia
    preppare_crawler(seed_url)
