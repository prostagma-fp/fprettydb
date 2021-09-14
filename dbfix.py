import sqlite3
import importlib
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Get site defs
SITES_FOLDER = "sites"
try:
    with open(SITES_FOLDER+"/defs.txt", 'r') as sites_data:
        site_python_list = sites_data.read().replace("\r", "").split("\n")
except:
    print("Could not read "+SITES_FOLDER+"/defs.txt")

site_defs = []
for script in site_python_list:
    name = script[script.replace('\\', '/').rfind('/')+1:-3]
    m = importlib.import_module(SITES_FOLDER+"."+script[:-3])
    importlib.reload(m) #reimporting a python file doesn't import the file newly (it uses a cached version to save time), this saves it
    site_defs.append((re.compile(m.regex), getattr(m, name)))

# Source replacements
source_dict = dict([
    ('ungrounded.net', (lambda lc: "https://www.newgrounds.com/portal/view/"+re.search(r'(?<=\d/)(.*?)(?=_)', lc).group(0))),
    ('y8.com', (lambda lc: None if (lc.endswith('.html') or lc.endswith('.html"')) else "https://en.y8.com/games"+lc[lc.rindex("/"):lc.rindex(".")])),
    ('cms.miniclip.com', (lambda lc: "https://www."+re.search(r'miniclip.com/games/(.*?)/', lc).group(0)+"en/")),
    ('miniclip.com/games/', (lambda lc: "https://www."+re.search(r'miniclip.com/games/(.*?)/', lc).group(0)+"en/")),
    ('miniclip.com/gameloader.swf', (lambda lc: "https://www.miniclip.com/games/"+re.search('(?<=fn.)(.*?)/', lc).group(0)+"en/")),
    ('/miniclip.com', (lambda lc: "https://www.miniclip.com/games/"+re.search('(?<=.com/)(.*?)/', lc).group(0)+"en/")),
    ('www.miniclip.com', (lambda lc: "https://www.miniclip.com/games/"+re.search('(?<=.com/)(.*?)/', lc).group(0)+"en/")),
    ('coolmathgames.com', (lambda lc: lc[:lc.rindex("/")+1])),
    ('games.jayisgames.com', (lambda lc: "https://jayisgames.com/games"+lc[lc.rindex("/"):lc.rindex(".")]+"/")),
    ('kraisoft.com', (lambda lc: re.search(r'(.*)/(.*)/(.*?)/', lc).group(0)))
    ])

# Publisher replacements
publisher_list = [
    (r'\.com/', '.com'),
    (r'(www.)?[nN]ewgrounds(\.com)?', 'Newgrounds'),
    (r'(www.)?[dD]eviant\s?[aA]rt(\.com)?', 'DeviantArt'),
    (r'(www.)?[aA]rmor\?[gG]ames(\.com)?', 'Armor Games'),
    (r'(www.)?[cC]artoon\?[nN]etwork(\.com)?', 'Cartoon Network'),
    (r'(www.)?[kK]ongregate(\.com)?', 'Kongregate'),
    (r'(www.)?[yY]8(\.com)?', 'Y8'),
    (r'(www.)?[aA]ndkon(\.com)?', 'Andkon'),
    (r'(www.)?[mM]ax\s?[gG]ames(\.com)?', 'Max Games'),
    (r'(www.)?[rR]usty\s?[aA]rcade(\.com)?', 'Rusty Arcade'),
    (r'(www.)?[rR]oxi\s?[gG]ames(\.com)?', 'RoxiGames'),
    (r'(www.)?[gG]ames\?[sS]umo(\.com)?', 'GamesSumo'),
    (r'(www.)?[cC]artoon\s?[rR]ace(\.com)?', 'CartoonRace'),
    (r'(www.)?[pP]pupu\s?[gG]ames(\.com)?', 'Pupu Games'),
    (r'(www.)?[pP]lay\s?[tT]oon\s?[gG]ames(\.com)?', 'Play Toon Games'),
    (r'(www.|^)[kK]ing\s?[gG]ames(\.net)?', 'King Games')
    ]

# Trim spaces and break lines
strip_all = lambda value: value.strip('\r\n').strip('\n').strip().replace('\n\n\n', '\n\n').replace('\r\n\r\n\r\n', '\r\n\r\n')

# Match url with site definitions and try to download meta if any matches
def get_web_meta(url):
    if not url.endswith((".com", ".com/", ".io", ".swf", ".dcr")):
        try:
            for site in site_defs: #site[0] = regex, site[1] = class
                if re.search(site[0], url):
                    print("(" + str(round((currentCuration/numCurations)*100, 3)) + "%) Fetching " + url + " with " + str(site[0]))
                    try:
                        html_source = requests.get(url)
                    except:
                        html_source = requests.get("https://web.archive.org/web/2id_/"+url)
                    meta = site[1]
                    response = meta().parse(url, BeautifulSoup(html_source.text, 'html.parser'))
                    return response
        except:
            raise
    return None

# Meta fetcher test
def test_sites():
    print(get_web_meta("https://www.newgrounds.com/portal/view/817"))
    print(get_web_meta("https://www.addictinggames.com/shooting/stack-colors"))
    print(get_web_meta("http://www.coolmathgames.com/0-lavanoid/"))
    print(get_web_meta("http://www.freearcade.com/Legor3.flash/Legor3.html"))
    print(get_web_meta("https://cosmicadventuresquad.itch.io/deepest-sword"))
    print(get_web_meta("https://jayisgames.com/games/arijigora/"))
    print(get_web_meta("https://www.kongregate.com/games/Ninjakiwi/bloons-td-5"))
    print(get_web_meta("http://www.miniclip.com/games/mars-patrol/en/"))
    print(get_web_meta("https://miniclip.com/games/lavalab/en/"))
    print(get_web_meta("https://pt.y8.com/games/cyber_swat"))
    print(get_web_meta("http://panget2007panget.deviantart.com/art/Pokemon-Platinum-Pokedex-166528325"))

changes_counter = 0
full_changelog = ''

#Create sqlite connection and execute query
try: fpFile = sqlite3.connect('flashpoint.sqlite')
except:
    print("This script should in the same folder as flashpoint.sqlite.")
    exit()
cursor = fpFile.cursor()

# Percentage indicators
cursor.execute('SELECT Count() FROM game')
numCurations = cursor.fetchone()[0]
currentCuration = 0

# Query
full_query = 'SELECT id, title, alternateTitles, developer, publisher, source, launchCommand, releaseDate, originalDescription FROM game'
cursor.execute(full_query)

meta_list = ['id', 'title', 'alternateTitles', 'developer', 'publisher', 'source', 'launchCommand', 'releaseDate', 'originalDescription'] #dirty hack
query_item = {}

#for item_id, item_title, item_developer, item_publisher, item_source, item_launchCommand, item_releaseDate, item_originalDescription in cursor.fetchall():
for items in cursor.fetchall():
    for i in range(len(meta_list)):
        query_item[meta_list[i]] = items[i]

    changelog = query_item['id'] + '\n'

    # Title
    new_title = query_item['title'].strip().replace("  ", " ")
    if query_item['title'] != new_title:
        cursor.execute('UPDATE game SET title = (?) WHERE id = (?)', (new_title, query_item['id']))
        changelog += "TITLE - (TRIMMED TO) -> " + new_title + '\n'
        
    # Alternate title
    new_title = query_item['alternateTitles'].strip().replace("  ", " ")
    if query_item['alternateTitles'] != new_title:
        cursor.execute('UPDATE game SET alternateTitles = (?) WHERE id = (?)', (new_title, query_item['id']))
        changelog += "ALTERNATETITLES - (TRIMMED TO) -> " + new_title + '\n'
    
    #Publisher
    if query_item['publisher'] != '':
        for list_publisher_regex in publisher_list:
            if re.search(list_publisher_regex[0], query_item['publisher']):
                new_publisher = re.sub(list_publisher_regex[0], list_publisher_regex[1], query_item['publisher'])
                if new_publisher != query_item['publisher']:
                    cursor.execute('UPDATE game SET publisher = (?) WHERE id = (?)', (new_publisher, query_item['id']))
                    changelog += "PUBLISHER - " + query_item['publisher'] + " -> " + new_publisher + '\n'

    # Source, also used to online search
    testing_source = query_item['source']
    if testing_source.endswith(".com") or testing_source.find(".") == -1:
        for dict_matchingurl, dict_lambda in source_dict.items():
            if query_item['launchCommand'].find(dict_matchingurl) != -1:
                try:
                    testing_source = re.sub(r"(\?|\s)(.*)", "", dict_lambda(query_item['launchCommand']))
                    if testing_source != None:
                        cursor.execute('UPDATE game SET {} = (?) WHERE id = (?)'.format(key), (value, query_item['id']))
                        changelog += "SOURCE - " + query_item['source'] + " -> " + testing_source + '\n'
                except:
                    pass
                break

    # Developer, Release Date, Original Description = online search
    no_publisher = query_item
    no_publisher.pop('publisher')
    no_publisher.pop('alternateTitles')
    if '' in no_publisher.values():
        fetched_meta = get_web_meta(testing_source)
        if fetched_meta != None:
            for key, value in fetched_meta.items():
                if value and query_item[key] == (None or ''):
                    if key == 'originalDescription':
                        value = strip_all(value)
                    #print('UPDATE game SET ' + key + ' = "' + value.replace('"', '""') + '" WHERE id = "' + query_item['id'] + '"')
                    cursor.execute('UPDATE game SET {} = (?) WHERE id = (?)'.format(key), (value, query_item['id']))
                    changelog += key.upper() + " - (NONE) -> " + value + '\n'
    
    # Release Date format
    if query_item['releaseDate'] != '' and re.fullmatch(r'\d{4}(\-(0[1-9]|1[012])|\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01]))?', query_item['releaseDate']) == None:
        new_releaseDate = re.sub(r'-(?=\d-|\d$)', '-0', query_item['releaseDate'])
        cursor.execute('UPDATE game SET releaseDate = (?) WHERE id = (?)', (new_releaseDate, query_item['id']))
        changelog += "RELEASEDATE - " + query_item['releaseDate'] + " -> " + new_releaseDate + '\n'

    # Original Description
    new_originalDescription = strip_all(query_item['originalDescription'])
    if new_originalDescription != query_item['originalDescription']:
        cursor.execute('UPDATE game SET originalDescription = (?) WHERE id = (?)', (new_originalDescription, query_item['id']))
        changelog += "ORIGINALDESCRIPTION - (TRIMMED TO) -> " + new_originalDescription + '\n'

    # Add to changelog
    if len(changelog) > 37: #id + \n
        cursor.execute('UPDATE game SET dateModified = (?) WHERE id = (?)', (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), query_item['id']))
        print(changelog)
        full_changelog += changelog + '\n'
        changes_counter += 1
    
    currentCuration += 1

full_changelog += '\n' + str(changes_counter) + ' curations changed.'
#print(full_changelog)

# Commit and close sqlite
try:
    cursor.close()
    fpFile.commit()
    fpFile.close()
except:
    print("Could not write into the sqlite.")
    raise

print (str(changes_counter) + ' curations changed.')

# Create changelog file
f = open("changelog.txt", "w", encoding="utf-8")
f.write(full_changelog)
f.close()
