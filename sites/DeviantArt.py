# DeviantArt definition.

import re
from html import unescape
import Curation

regex = 'deviantart.com'

class DeviantArt(Curation.Curation):
    def parse(self, url, soup):

        #self.meta['publisher'] = "DeviantArt"

        #Get developer
        try: self.meta['developer'] = soup.select_one('a[data-hook="user_link"]')['data-username']
        except: return None
        
        # Skippable meta (content not from users)
        skiplist = ['liamandnico', 'Hudsun28Studios', 'PeasOnNoggin12']
        if self.meta['developer'] in skiplist: return None

        # Get info and description
        try:
            originalDescription = str(soup.select(".XeBxZ > .legacy-journal")[0]).replace('\xa0', ' ')
            replacements = [
                (r'<a(.+?)href="(https:..www.deviantart.com.users.outgoing\?)?(.+?)"(.+?)>',  r'\3'),
                (r'<img (.*?)alt="(.+?)"(.+?)\/>',  r'\2'),
                (r'\s?<br\/?>', '\n'),
                (r'\n?(<ul>)?<li>', '\n• '),
                (r'<\/?(.+?)>', ''),
                (r'\s?\n\n\n\s?', '\n\n')
            ]
            for old, new in replacements:
                originalDescription = re.sub(old, new, originalDescription)
            self.meta['originalDescription'] = originalDescription.strip('\n').strip()
        except:
            pass
        
        # Get date
        try:
            date = soup.select_one("._1iHMP > span > time")['datetime']
            self.meta['releaseDate'] = date[:10]
        except:
            pass

        # Return variables
        return self.meta
