# Miniclip definition. Only supports HTML5.

import json
import Curation

regex = 'miniclip.com'

class Miniclip(Curation.Curation):
    def parse(self, url, soup):
        # Base everything off of application data, which is hopefully more stable than the webpage format
        try: data = json.loads(soup.select_one("#jsonLdSchema").string)
        except: return None

        #self.meta["publisher"] = "Miniclip"
        try:
            if not data['datePublished'].startswith('-'): 
             self.meta['releaseDate'] = data["datePublished"][:10]
        except: pass

        # Get Description
        try: self.meta['originalDescription'] = soup.select_one(".game-description").text.strip()
        except: pass

        # Return variables
        return self.meta