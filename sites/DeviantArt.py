# DeviantArt definition.

import Curation

regex = 'deviantart.com'

class DeviantArt(Curation.Curation):
    def parse(self, url, soup):

        #self.meta['publisher'] = "DeviantArt"

        #Get developer
        try: self.meta['developer'] = soup.select_one('a[data-hook="user_link"]')['data-username']
        except: return None

        # Get info and description
        try:
            info = soup.select(".XeBxZ > .legacy-journal")
            self.meta['originalDescription'] = info[0].text.strip()
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
