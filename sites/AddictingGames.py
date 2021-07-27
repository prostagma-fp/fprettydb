# Addicting Games definition.

import Curation

regex = 'addictinggames.com'

class AddictingGames(Curation.Curation):
    def parse(self, url, soup):

        # Get Developer and set Publisher
        try: self.meta['developer'] = soup.select_one(".author-span > strong").text
        except: pass
        #self.meta['publisher'] = "Addicting Games"

        # Get Release Date
        try: date = soup.select_one(".release-span > strong").text
        except: return None
        self.meta['releaseDate'] = date[-4:] + "-" + Curation.MONTHS[date[3:6]] + "-" + date[:2]

        # Get Description
        for s in soup.select('.game-page-video, div[class^=instru-blk_], div[class^=realted-games]'):
            s.extract()
        desc = "\n\n".join(i.text for i in soup.select(".instru-blk > h5, .instru-blk > p")).strip()
        if desc.endswith("Game Reviews"):
            desc = desc[:-12].strip()
        self.meta['originalDescription'] = desc

        # Return variables
        return self.meta
