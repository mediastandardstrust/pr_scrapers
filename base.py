""" minimal stand-alone implementation of BaseScraper from churnalism.com """
import urllib2
from BeautifulSoup import UnicodeDammit
from lxml.html import parse, fromstring
from urllib2helpers import CacheHandler


# cache all downloaded files in ".cache" subdirectory...
# makes repeated test scraper runs nice and quick :-)
# just delete the directory to clear the cache.
opener = urllib2.build_opener(CacheHandler('.cache'))
urllib2.install_opener(opener)


class BaseScraper:
    def run(self):
        # derived scrapers implement this
        pass

    def upsert_press_release(self,pr):
        """ process a scraped press release """

        # Here, we just dump the release out to stdout.
        # force utf-8 output to make sure python won't encode to ascii
        # if it doesn't know where the output it going...
        # Most releases include non-ascii characters, which would cause
        # ascii encoding to blow up in our faces.
        enc = 'utf-8'
        print "title: %s" % (pr['title'].encode(enc),)
        print "published: %s" % (pr['published'].date(),)
        print "source_link: %s" % (pr['source_link'],)
        print "-------- text --------"
        print pr['text'].encode(enc)
        print "----------------------\n\n"

    def get_url(self,url):
        """ fetch url, return it as an lxml.html doc """

        content = urllib2.urlopen(url).read()
#        content = re.sub( """<?xml version="1.0" encoding="(.*?)"?>""", '', content)
        #"""<?xml version="1.0" encoding="ISO-8859-1"?>"""

        converted = UnicodeDammit(content, isHTML=True)


        if not converted.unicode:
            raise UnicodeDecodeError(
                "Failed to detect encoding, tried [%s]",
                ', '.join(converted.triedEncodings))
        doc = fromstring(converted.unicode)
        doc.make_links_absolute(url)
        return doc

