import re
from urllib import robotparser
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.error import URLError
from simhash import Simhash



from crawler import worker
from crawler.worker import word_counter
from crawler.worker import longestPage
from crawler.worker import ics_domains

cache = {}
url_counter = 0
depth = 0
english_stopwords = [
    "a","about","above","after","again","against","all","am",
    "an","and","any","are","aren't","as","at","be","because","been","before","being",
    "below","between","both","but","by","can't","cannot","could","couldn't","did",
    "didn't","do","does","doesn't","doing","don't","down","during","each","few","for",
    "from","further","had","hadn't","has","hasn't","have","haven't","having","he","he'd",
    "he'll","he's","her","here","here's","hers","herself","him","himself","his","how",
    "how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its",
    "itself","let's","me","more","most","mustn't","my","myself","no","nor","not","of","off",
    "on","once","only","or","other","ought","our","ours","ourselves","out","over","own",
    "same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such",
    "than","that","that's","the","their","theirs","them","themselves","then","there","there's",
    "these","they","they'd","they'll","they're","they've","this","those","through","to","too",
    "under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were",
    "weren't","what","what's","when","when's","where","where's","which","while","who","who's",
    "whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're",
    "you've","your","yours","yourself","yourselves"
]
uniqueURLs = set()



def tokenize(content):
    #print("THIS IS CONTENT |||||||||:", content, "\n")
    soup = BeautifulSoup(content, 'html.parser')
    #text = re.sub(r'[^>]+>', '', content)
    text = soup.get_text()
    text = text.strip().lower()
    for tok in text:
        if tok == '':
            text.remove(tok)
            
    tokens = []
    token = ""

    for char in text:
        if char.isalnum() and char.isascii():
            token += char
        else:
            t = token.lower()
            if t != '':
                tokens.append(t)
                token = ""
    if token:
        tokens.append(token.lower())
    #print("THIS IS TOKENS: |||||||||||||||||||||||", tokens)
    #print("working here")
    return tokens

def scraper(url, resp):
    global url_counter
    global uniqueURLs
    #print("work1")
    #print()
    url_counter -= 1
    #print("HHHHHHHHH:", url)
    if robot_check(url) and length_check(resp):
        #print("work2")
        if normalizer(url) not in uniqueURLs:
            uniqueURLs.add(normalizer(url))
        print("uniqueurl:", uniqueURLs)
        #print("HHHHHHHHH:", url)
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        pageText = soup.get_text()
        cleaned = re.sub(r'\s+', ' ', pageText).strip()
        token = tokenize(cleaned)
        page_simhash = Simhash(token)
        #print("working here2")
        #print("HHHHHHHHH:", url)
        urls = url
        for urls, simhash in cache.items():
            #fix with duct tape
            #print("working herezzz")
            #print(type(page_simhash), type(simhash))

            if page_simhash.distance(simhash) < 5:
                print("working herereturn")
                return []
        #print(print("working here3"))
        #print("AAAAAAAAA:", url)
        cache[urls] = page_simhash
        #print("HHHHHHHHH:", url)
        #print("THIS IS CLEAN ||||||||||||||||", token, "\n")
        pageLength = len(cleaned.split())
        print(f"PAGE LENGTH: {pageLength}")


        for c in cleaned.split():
            if not (c.lower() in english_stopwords) and (c.isalpha()):
                if c.lower() in word_counter:
                    word_counter[c.lower()] += 1
                else:
                    word_counter[c.lower()] = 1
        #print(url)
        parsed = urlparse(url)
        #print(parsed.netloc)
        if parsed.netloc.endswith(".ics.uci.edu"):
            #print(parsed.netloc)
            #print("ics domain")
            #print(ics_domains)
            if parsed.netloc in ics_domains.keys():
                ics_domains[parsed.netloc] += 1
            else:
                ics_domains[parsed.netloc] = 1
                
        # unique_urls.add(parsed.netloc)
        if longestPage[1] < pageLength:
            longestPage[0] = url
            longestPage[1] = pageLength

        links = extract_next_links(url, resp)
        if links:
            #print("links")
            #print("\n", [link for link in links if is_valid(link)])
            all_links = []
            for link in links:
                if is_valid(link):
                    all_links.append(link)
            #print("extracted:", all_links)
            url_counter += len(all_links)
            #print("number of URLS:", url_counter)
            return [link for link in links if is_valid(link)]
        else:
            #word_counter = dict(sorted(word_counter.items(), key=lambda item: item[1]))
            return []
    else:
        return []

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
    global cache
    global depth
    depth = 0
    #print("resp.url:", resp.url)
    #print("cache", cache.keys())

    #parsed_url = urlparse(resp.url)
    norm_url = normalizer(resp.url)
    #if norm_url in cache:
    #    return []
    
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        a_tags = soup.find_all('a')
        extracted_links = []
        normalized_links = []
        extracted_links = [tag.get('href') for tag in a_tags if tag.get('href')]
       # print("Extracted URLS:", extracted_links, "\n")

       #BIG CHANGE
        #base_url = resp.url
        base_url = norm_url
    
        for link in extracted_links:
            full_link = urljoin(base_url, link)

            #think we should add to cache regardless
            #cache[full_link] = resp.raw_response.content


            #THSI STUPID THING NOT WORKING!!!!!

            n_full_link = normalizer(full_link)

            #print("\n\nFULL LINK",full_link)
            depth += 1      
            if n_full_link not in cache.keys():
                normalized_links.append(n_full_link)
            #think we should add to cache regardless
            #cache[n_full_link] = resp.raw_response.content


        #normalized_links = [urljoin(base_url, link) for link in extracted_links]
        
       # print("Normalized_links:", normalized_links, "\n") 
        return normalized_links
    elif response.status == 301 or response.status == 302:
        # new_redirect_url = resp.raw_response.content.get('Location')
        print(resp.raw_response)
        print(resp.raw_response.content)

        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        location = soup.find('Location')

        base_url = norm_url
        if new_redirect_url.startswith('http://'):
            full_link = new_redirect_url
        else:
            full_link = urljoin(base_url, new_redirect_url)
        n_full_link = normalizer(full_link)
        if n_full_link not in cache.keys():
                normalized_links.append(n_full_link)

        # normalized_links.append(resp.url) // like resp.url is post redirection


        #not sure about depth

#extract URL

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        #print("Depth:", depth, "\n")
        if parsed.scheme not in set(["http", "https"]):
            return False
        #print(parsed.netloc)
        if not (parsed.netloc.endswith(".ics.uci.edu") or parsed.netloc.endswith(".cs.uci.edu") or parsed.netloc.endswith(".informatics.uci.edu") or parsed.netloc.endswith(".stat.uci.edu")):
            #print(f"rejected: |{parsed.netloc}|")
            
            return False
        
        if depth > 200: # figure out threshold
            return False
        
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


def robot_check(url):
 # figure out what to do with robots.txt
    robots_url = urljoin(url,'robots.txt')
    robots = robotparser.RobotFileParser(robots_url)
    try:
        robots.read()
        allowed = robots.can_fetch("IR US24 43785070,25126906,66306666,36264445", url)
        #print(f"Fetch allowed: {allowed}, {robots_url}")  # Debug: Print if fetching is allowed

        return allowed
    except URLError as e:
        print(f"Failed to access {robots_url}: {e.reason}")  # Debug: Print error message
        return False
    #except Exception as e:
    #    print(f"Unexpected error: {str(e)}")  # Debug: Print unexpected errors
    #    return False

def length_check(resp):
    #checks if content is None
    if resp.raw_response is not None:
        #check length of content
        if (len(resp.raw_response.content) < 5 * 1024 *1024) and len(resp.raw_response.content) > 0:                       #CHECKS LENGTH OF FILES 
            return True
        else:
            return False
    else:
        return False

def normalizer(url):

    url = url.split('#')[0]
    return url