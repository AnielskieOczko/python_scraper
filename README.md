# python_scraper
Simple website crawler + data scraping

Content:
1) open_page.py: main module, contain following functions:
  - get_page
Download a given URL and return the page content
        args:
            url (str): URL
        kwargs:
            user_agent (str): user agent (default: wswp)
            charset (str): charset if website does not include one in headers
            proxy (str): proxy url, ex 'http://IP' (default: None)
            num_retries (int): number of retries if a 5xx error is seen (default: 2)
  - robots_parser: get robots.txt of webpage
  - link_finder: pull all lings from web_site
  - link_checker: Crawl from the given start URL following links matched by link_regex. 
        In the current
        implementation, we do not actually scrapy any information.
        args:
            start_url (str): web site to start crawl
            link_regex (str): regex to match for links
        kwargs:
            robots_url (str): url of the site's robots.txt (default: start_url + /robots.txt)
            user_agent (str): user agent (default: wswp)
            proxy (str): proxy url, ex 'http://IP' (default: None)
            delay (int): seconds to throttle between requests to one domain (default: 3)
            max_depth (int): maximum crawl depth (to avoid traps) (default: 4)
            scrape_callback (function): function to call after each download (default: None)
