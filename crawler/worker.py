from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time

ics_domains = dict()
longestPage = ["", 0]

word_counter = dict()

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        retry_count = 0
        count = 0
        while count < 300:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            try:
                retry_count = 0
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                
                self.logger.info(f"FRONTIER{self.frontier.to_be_downloaded}")
                scraped_urls = scraper.scraper(tbd_url, resp)
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
                self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)
            except Exception as e:
                print("ERROR:", e)
                retry_count += 1
                self.frontier.add_url(tbd_url)
                if retry_count > 3:
                    skipped = self.frontier.get_tbd_url()
                    print(f"Exceeded retry amounts for: {skipped}")
                else:
                    time.sleep(self.config.time_delay * retry_count)
            count += 1
        
        print(count)
        print(ics_domains)
        print(longestPage)
        sortedWords = sorted(word_counter.items(), key=lambda item: -item[1])
        print(sortedWords[:50])
