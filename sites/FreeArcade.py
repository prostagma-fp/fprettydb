# Free Arcade definition. Only supports Flash and Java.
import Curation

regex = 'freearcade.com'

class FreeArcade(Curation.Curation):
    def parse(self, url, soup):
        #self.meta.publisher = "FreeArcade"

        # Get description
        try:
            self.meta['originalDescription'] = soup.select_one(".game > p").text.replace("\t", "") + \
                        "\n\n" + \
                        soup.select_one(".sidebox > p").text.replace("\t", "")
        except:
            pass

        # Return variables
        return self.meta