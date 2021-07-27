# itch.io site definition (This is just the Unknown site definition but with a few extra kinks)

import fpclib
import Curation

regex = "itch.io"

class ItchIO(Curation.Curation):
    def parse(self, url, soup):

        # Get devs
        try:
            authors = soup.find("td", text="Author").parent
            self.meta['developer'] = "; ".join([e.text for e in authors.find_all("a")])
        except: pass
        
        # Get languages
        '''try:
            lang = soup.find("td", text="Languages").parent
            self.meta['language'] = "; ".join([e["href"][-2:] for e in lang.find_all("a")])
        except: pass'''
        
        #self.meta['publisher'] = "itch.io"

        # Release date
        try:
            self.meta['releaseDate'] = fpclib.DP_UK.parse(soup.select_one(".game_info_panel_widget tbody abbr")["title"])
        except: pass

        # Return variables
        return self.meta