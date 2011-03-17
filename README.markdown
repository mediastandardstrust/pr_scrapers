pr_scrapers
===========

Scrapers to collect press releases. In Python.

This project is a stand-alone sandbox for easy development of press release
scrapers for incorporation into [churnalism.com](http://churnalism.com).
It's designed to require minimal setup...


Requirements
------------

* lxml
* BeautifulSoup (for UnicodeDammit)


Details
-------

Just copy an existing scraper (eg onepoll.py) and start hacking about!

base.py is a mockup of the churnalism.com scraper interface. Rather than
working against a database it just dumps scraped press releases out to
stdout.
It provides the BaseScraper interface to derive scrapers from.
It also installs a caching handler for urllib2 which creates a ".cache"
directory to stores downloaded files. This makes repeated test runs during
development a _lot_ quicker. Just delete the ".cache" dir to clear the
cache.

To try out your scraper, add something like this:

    if __name__ == "__main__":
        scraper = Scraper()
        scraper.run()

Then you can just run it directly, eg:

    $ python <your_scraper>

