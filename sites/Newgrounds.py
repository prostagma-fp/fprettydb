# Newgrounds definition.

import bs4
import fpclib
#import requests
import Curation

# This is the regex that will be used to match this site. It is required!
regex = 'newgrounds.com'

# This is a global variable that allows you to grab login-locked games. You'll have to replace it to get those games. You can comment it out if you like.
TOKEN_HEADERS = {"COOKIE": "COOKIE_CONTAINING_TOKEN_GOES=HERE"}

# This is the class to use to curate with. It is also required!
class Newgrounds(Curation.Curation):

    def parse(self, url, osoup):
        # Check for login-lock
        try: login = "requires a Newgrounds account to play" in osoup.select_one(".column").text
        except: return None
        if login:
            soup = fpclib.get_soup(url)
            #with requests.get(url, headers=TOKEN_HEADERS) as response:
            #    soup = bs4.BeautifulSoup(response.text, 'html.parser')
            #soup = fpclib.get_soup(self.url, headers=TOKEN_HEADERS)
        else:
            soup = osoup
        
        # Get Developer(s)
        devsl = []
        try:
            for div in soup.find('ul', class_='authorlinks').find_all('div', class_='item-details-main'):
                devsl.append(div.find('h4').text.strip())
        except (AttributeError, TypeError):
            pass
        self.meta['developer'] = "; ".join(devsl)
        #self.meta['publisher'] = "Newgrounds"
        
        # Get content area
        content_area = soup.find('div', id='content_area')
        
        # Get Release Date
        try: self.meta['releaseDate'] = content_area.find('meta', itemprop='datePublished')['content'][:10]
        except: pass

        # Get Description and author comments
        try:
            desc = content_area.find('meta', itemprop='description')['content']
            a_c = soup.find('div', id='author_comments')
            if a_c:
                if desc != '': desc += '\n\n'
                desc += 'Author Comments:\n'
                for elem in a_c.children:
                    if isinstance(elem, bs4.NavigableString):
                        continue
                    if elem.name == 'ul':
                        for li in elem.children:
                            if isinstance(li, bs4.NavigableString):
                                continue
                            desc += '\n  - ' + li.text
                    elif elem.name == 'ol':
                        i = 1
                        for li in elem.children:
                            if isinstance(li, bs4.NavigableString):
                                continue
                            desc += '\n  ' + str(i) + '. ' + li.text
                            i += 1
                    else:
                        desc += '\n' + elem.text
            self.meta['originalDescription'] = desc
        except: pass

        # Return variables
        return self.meta