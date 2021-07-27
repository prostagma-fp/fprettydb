# Kongregate definition.

import Curation
import bs4, re

regex = 'kongregate.com'

class Kongregate(Curation.Curation):
    def parse(self, url, soup):

        # Get Developer and set Publisher
        try: self.meta['developer'] = "; ".join([dev.text.strip() for dev in soup.select(".game_dev_list > li")])
        except: return None
        #self.meta["publisher"] = "Kongregate"
        
        # Get Release Date
        try: date = soup.select_one(".game_pub_plays > p > .highcontrast").text
        except: return None
        self.meta['releaseDate'] = date[-4:] + "-" + Curation.MONTHS[date[:3]] + "-" + date[5:7]

        # Get description (combination of instructions and description)
        # idata is inside a script tag and hasn't been inserted yet.
        idata = bs4.BeautifulSoup(soup.select_one("#game_tab_pane_template").string, "html.parser")

        desc = ""
        try:
            n = idata.select_one("#game_description > div > .full_text").text.replace("\t", "")[:-9]
            #desc += "Description\n\n" + n
            desc += n
        except: pass
        try:
            if desc: desc += "\n\n"
            desc += "Instructions\n\n" + idata.select_one("#game_instructions > div > .full_text").text[:-9].replace("\t", "")
        except: pass

        self.meta['originalDescription'] = desc

        # Return variables
        return self.meta