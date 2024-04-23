import re
from urllib import robotparser
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import datetime
#from reppy.robots import Robots


cache = {}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # if resp.status != 200:
    #     return None
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        a_tags = soup.find_all('a')
        extracted_links = []
        for tag in a_tags:
            href = tag.get('href')
            if href:
                extracted_links.append(href)
                base_url = resp.url  # The URL that was fetched to get this response
                normalized_links = [urljoin(base_url, link) for link in extracted_links]
                # filter ??
               # final_links = filter_links(normalized_links)  
        #print(normalized_links)
        return normalized_links

#extract URL

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        # figure out what to do with robots.txt
        # robots_url = f"{url}robots.txt"
        # robots = robotparser.RobotFileParser()
        # robots.set_url(robots_url)
        # robots.read()
        # allowed = robots.can_fetch("IR US24 43785070,25126906,66306666,36264445", url)
        # if allowed:
        #     return True
        # else:
        #     return False     
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
       
       #robots = Robots.parse(robots_url)
        
        #test = webbrowser.open(robots_url.read())
        #print(test)
        

        # if robots_url not in cache:
        #     response = requests.get(robots_url) # figure out how to do this w/o requests lib
        #     if response.status_code == 200:
        #         # stores robots.txt contents of domain and the time it was cached in dictionary
        #         cache[robots_url] = (response.text, datetime.now())
        #     elif response.status_code == 404: # 404 error
        #         cache[robots_url] = -1 # robots.txt not found
        # else:
        #     if cache[robots_url] != -1:
        #         r_parser = urllib.robotparser.RobotFileParser
        #         r_parser.set_url = robots_url
        #         r_parser.read()
        #         if r_parser.can_fetch() == True:
        #             return True
       
        



    except TypeError:
        print ("TypeError for ", parsed)
        raise
