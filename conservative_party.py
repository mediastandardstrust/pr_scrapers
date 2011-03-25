import dateutil.parser
from base import BaseScraper
import re
import urllib2
import lxml.html
from subprocess import Popen, PIPE, STDOUT
import email
import email.feedparser
import tempfile

# Scrape press release archive from the conservative party website.
#
# The site commits a litany of atrocities, which makes it a good
# example of a typical web site.
#
# Requirements:
#   antiword  (word->text converter)
#   Email::Outlook::Message  (CPAN module)
#
# As if press releases in word docs weren't bad enough, a lot (~75%?)
# of the conservative releases are in .msg files, which is an
# undocumented microsoft exchange (or outlook?) format.
#
# Luckily, Email::Outlook::Message in CPAN can parse them and turn
# them into something sane.
#
# To install it from CPAN (please forgive the perl-naivite here):
#
#  $ sudo perl -MCPAN -e shell
#  cpan> install Email::Outlook::Message
#
# it depends in turn on OLE::Storage_Lite and IO:All - cpan shell
# should ask you if you want to install them first.
#

class Scraper(BaseScraper):
    long_name = "The Conservative Party" 
 
    def run(self):

        # grab the latest 100
        start_url = 'http://www.conservatives.com/Activist_centre/Press_Releases.aspx?take=100'

        links_page = self.get_url(start_url)
        for link in links_page.cssselect('.results .clfx h2 a'):
            page_url = link.get('href')
            title = unicode(link.text_content()).strip()
            self.extract(page_url)
            continue


    def extract(self,url):
        html = urllib2.urlopen(url).read()
        # convert to unicode. page meta tags _claim_ page is iso-8859-1, but
        # http headers say it's utf-8. sigh.
        html = html.decode('utf-8')  # (The headers are right.)
        doc = lxml.html.fromstring(html)
        doc.make_links_absolute(url)

        date_txt = unicode(doc.cssselect(".lg-content .info")[0].text_content()).strip()
        title = unicode(doc.cssselect(".lg-content h1")[0].text_content()).strip()

        published = dateutil.parser.parse(date_txt)
#        print " title: ",title
#        print " date: ",published

        # annoyingly, the press releases can be either:
        # - on the page, as you'd expect
        # - attached as a word doc. grr.
        # - attached as a .msg file. WTF?
        attached = doc.cssselect('.lnklist a')
        txt = u''
        if len(attached)>0:
            # press release in attachement
            attachment_url = attached[0].get('href')
            txt = self.text_from_attachment(attachment_url)
        else:
            # press release on page
            maintxt = doc.cssselect('.main-txt')[0]
            for cruft in maintxt.cssselect('.botlnks'):
                cruft.getparent().remove(cruft)
            txt = unicode(maintxt.text_content())

        self.upsert_press_release({
            'published'     : published,
            'title'         : title,
            'text'          : txt,
            'source_link'   : url,
        })

    def text_from_attachment(self,attachment_url):
        attachment_url = attachment_url.replace(' ','%20')
        f = urllib2.urlopen(attachment_url)
        data = f.read()

        m = re.compile(r'filename=(.*)').search(f.info()['Content-Disposition'])
        filename = m.group(1)
        if filename.lower().endswith('.doc'):
            # word file - convert to text.
            p = Popen(['antiword', '-m', 'UTF-8', '-'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            txt = p.communicate(input=data)[0]

            # kill the table at the top
            pat = re.compile('^\s*[|].*?$',re.DOTALL|re.MULTILINE)
            txt = pat.sub('',txt).strip()

            txt = unicode(txt,'utf-8')

            return txt

        if filename.lower().endswith('.msg'):
            # it's an exchange ".msg" file! oh, the humanity...

            # first step - extract from silly .msg format
            f = tempfile.NamedTemporaryFile()
            f.write(data)
            f.flush()
            perlcmd = """use Email::Outlook::Message; print new Email::Outlook::Message('""" + f.name + """')->to_email_mime->as_string;"""
            devnull = open('/dev/null', 'w')
            p = Popen(['perl', '-w', '-e', perlcmd], stdout=PIPE, stdin=PIPE, stderr=devnull)
            mimedata = p.communicate()[0]
            f.close()

            # second step - find the email text (just look for the first 'text/plain' part)
            msg = email.message_from_string(mimedata)
            for part in msg.walk():
                if part.get_content_type()=='text/plain':
                    txt = part.get_payload()
#                    txt = txt.decode(part.get_content_charset())
                    txt = txt.decode('utf-8',"ignore")       # KLUDGE!
                    txt = txt.strip()
                    return txt

            assert False        # uhoh - couldn't get email text

        assert False    # shouldn't get this far...

if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()


