# Y8 definition.

import Curation

regex = 'y8.com'

class Y8(Curation.Curation):
    def parse(self, url, soup):

        #self.meta['publisher'] = "Y8"
        
        # Get info and description
        try:
            info = soup.select(".game-description > div > div > div")
            self.meta['originalDescription'] = info[0].text.strip()
        except:
            return None
        # Get date, commented for now, Y8 isnt always reliable on it
        #date = info[1].select_one(".data").text.strip().split(" ")
        #self.meta['releaseDate'] = date[2] + "-" + fpclib.MONTHS[date[1]] + "-" + date[0]

        # Return variables
        return self.meta