# Coolmath Games definition. Only supports HTML5 because all flash games are already curated except those on wayback.
# Some games can only be curated through https links.

import Curation
import bs4, re

regex = 'coolmath-?games.com'

HTML_FILES = re.compile('.*\.(js|html|css|json)$')

class CoolmathGames(Curation.Curation):
    def parse(self, url, soup):
        
        # Get Description
        try:
            desc = soup.find('meta', property='og:description')['content'].replace('  ', '\n')
            i = desc.find(': ')+1
            desc = desc[:i] + '\n' + desc[i+1:]
            if desc.find("Math Games:\n") != -1:
                desc = desc[desc.find("Math Games:\n") + 12:]
        except:
            desc = ""
        
        try:
            for elem in soup.find('div', class_='game-instructions').children:
                if isinstance(elem, bs4.NavigableString):
                    continue
                if elem.attrs == {} or elem.attrs['class'][0] != 'mobile':
                    desc += '\n\n' + elem.text
        except:
            pass
        
        self.meta['originalDescription'] = desc
        
        # Return variables
        return self.meta
