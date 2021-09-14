# Jay is games definition.
import fpclib
import re
import Curation

MONTHS = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12"
}

regex = 'jayisgames.com'

DEV = re.compile("(developed|created) by (\w+)", re.I)
DATE = re.compile("(.*?) (\d+), (\d+)")

class JayIsGames(Curation.Curation):
    def parse(self, url, soup):
        
        #self.meta['publisher'] = "Jay Is Games"
        
        # Get Description
        try: desc = soup.select_one(".entrybody > p")
        except: return None
        if desc:
            self.meta['originalDescription'] = desc.text
        else:
            desc = soup.find("meta", attrs={"name": "description"})
            if desc: self.meta['originalDescription'] = desc["content"]
        
        # Check for "Read More"
        more = soup.select_one(".read-more")
        if more:
            msoup = fpclib.get_soup(more["href"])
            text = msoup.select_one(".entrydate").text.split("|")

            self.meta['developer'] = text[0].strip()[3:]
            match = DATE.fullmatch(text[1].strip())
            try: self.meta['releaseDate'] = match[3].replace(" ", "") + "-" + MONTHS[match[1].replace(" ", "")] + "-" + match[2].zfill(2)
            except: pass
        elif self.meta['originalDescription']:
            try:
                dev = DEV.search(self.meta['originalDescription'])
                if dev: self.meta['developer'] = dev[2]
            except: pass

        # Return variables
        return self.meta
