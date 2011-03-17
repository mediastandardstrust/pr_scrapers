from dateutil import parser
from base import BaseScraper
import re

class Scraper(BaseScraper):
    long_name = "One Poll" 
    
    def run(self):
        links_page = self.get_url("http://www.onepoll.com/press-archive/")
        links = links_page.cssselect('div.pressReleases td a')
        for link in links:
            page_url=link.get('href').replace("sex-o'clock",'Popular-time-for-sex')
            doc = self.get_url(page_url)
            title = doc.cssselect('div#content-page h2')
            published = link.getparent().getnext()
            content = doc.cssselect("div#content-page p")[3:-1]
            valid = len(content)>0 and len(title)>0
            if valid:
                self.upsert_press_release({
                    'published'     : parser.parse(unicode(published.text_content())),
                    'title'         : unicode(title[0].text_content().strip().replace('PRESS RELEASE: ','')),
                    'text'          : "\n".join([unicode(paragraph.text_content().strip()) for paragraph in content]),
                    'source_link'   : page_url,
                })



if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
