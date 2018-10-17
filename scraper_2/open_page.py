import urllib.request
from urllib import robotparser
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib import robotparser
from urllib.parse import urljoin
import re
from lxml.html import fromstring

# set path to module delay_time
import sys
sys.path.insert(0, r"D:\Python_projects\web_scraping\scraper_2")

from throttle import Throttle
from delay_time import Tajmer

def get_page(url, open_retry=2, user_agent="wswp", charset='utf-8'):
    """ Download a given URL and return the page content
        args:
            url (str): URL
        kwargs:
            user_agent (str): user agent (default: wswp)
            charset (str): charset if website does not include one in headers
            open_retry (int): number of retries if a 5xx error is seen (default: 2)
    """
    print("Getting url: ", url)

    # create request
    # add header to request -> used later to check if user_agent is allowed to scrap
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)

    try:
        # open url
        # check what encoding is used by web_page
        # if no encoding by default use utf-8
        resp = urllib.request.urlopen(request)
        cs = resp.headers.get_content_charset()
        if not cs:
            cs = charset
        html = resp.read().decode(cs)
    except (URLError, HTTPError, ContentTooShortError) as e:
        print("Error: ", e)
        html = None
        # check what error occurred
        # 5xx errors means that there is issue with server
        # retry open page if error 5xx
        if open_retry > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return get_page(url, open_retry - 1)

    return html


def link_finder(html):
    # reminder RE
    # char set: <a> b <c>
    # Using the RE <.*?> will match only <a>.
    # re.IGNORECASE => Perform case-insensitive matching; expressions like [A-Z] will match lowercase letters, too
    web_page_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)
    return web_page_regex.findall(html)


# get robots.txt for webpage
def robots_parser(robots_url):
    rob_p = robotparser.RobotFileParser()
    rob_p.set_url(robots_url)
    rob_p.read()
    return rob_p


def scrape_callback(url, html):
    """ Scrape each row from the country data using XPath and lxml """
    fields = ('area', 'population', 'iso', 'country', 'capital',
            'continent', 'tld', 'currency_code', 'currency_name',
            'phone', 'postal_code_format', 'postal_code_regex',
            'languages', 'neighbours')
    if re.search('/view/', url):
        tree = fromstring(html)
        all_rows = [
            tree.xpath('//tr[@id="places_%s__row"]/td[@class="w2p_fw"]' % field)[0].text_content()
            for field in fields]
        print(url, all_rows)


def link_checker(start_url, reg_ex, robots_url=None, user_agent="wswp",delay=4, max_depth=2, scrape_callback=None):
    """ Crawl from the given start URL following links matched by link_regex. In the current
        implementation, we do not actually scrapy any information.
        args:
            start_url (str): web site to start crawl
            link_regex (str): regex to match for links
        kwargs:
            robots_url (str): url of the site's robots.txt (default: start_url + /robots.txt)
            user_agent (str): user agent (default: wswp)
            delay (int): seconds to throttle between requests to one domain (default: 3)
            max_depth (int): maximum crawl depth (to avoid traps) (default: 4)
    """
    # create list for links which match our reg_ex
    page_queue = [start_url]
    # keep tracking links already seen in dict
    # web_pages are connected themselves
    seen = {}
    data = []

    # check if robots.txt exist
    if not robots_url:
        robots_url = "{}/robots.txt".format(start_url)
    # get robots txt
    rob_p = robots_parser(robots_url)
    timer_r = Tajmer(delay)
    #throttle = Throttle(delay)
    # loop links
    while page_queue:
        # get and then remove last element of list
        url = page_queue.pop()
        # check if passes web_page restrictions
        if rob_p.can_fetch(user_agent,url):
            # check url depth
            depth = seen.get(url, 0)
            # if max depth skip
            if depth == max_depth:
                print("Page skipped due to depth: ", url)
                continue

            timer_r.wait(url)
            #throttle.wait(url)
            # open page
            html = get_page(url, user_agent=user_agent)
            # if unable to open skip
            if not html:
                continue
            if scrape_callback:
                data.extend(scrape_callback(url, html) or [])
            # scrap data here

            # filter links matching regex
            # use link_finder function to get all links from html
            for link in link_finder(html):
                # check if matches reg_ex
                if re.match(reg_ex, link):
                    # create absolute link start url + link
                    abs_link = urljoin(start_url, link)
                    # add to seen dictionary if first time opened
                    # add to link list
                    if abs_link not in seen:
                        seen[abs_link] = depth + 1
                        page_queue.append(abs_link)
        else:
            print("Blocked by robots.txt: ", url)



link_checker(start_url="http://example.webscraping.com/places/default/", reg_ex='/.')