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
    (r'(www.)?[aA]rmor\s?[gG]ames(\.com)?', 'Armor Games'),
    (r'(www.)?[cC]artoon\s?[nN]etwork(\.(com|nl|es|fr))?', 'Cartoon Network'),
    (r'(www.)?[kK]ongregate(\.com)?', 'Kongregate'),
    (r'(www.)?[yY]8(\.com)?', 'Y8'),
    (r'(www.)?[aA]ndkon(\.com)?', 'Andkon'),
    (r'(www.)?[mM]ax\s?[gG]ames(\.com)?', 'Max Games'),
    (r'(www.)?[rR]usty\s?[aA]rcade(\.com)?', 'Rusty Arcade'),
    (r'(www.)?[rR]oxi\s?[gG]ames(\.com)?', 'RoxiGames'),
    (r'(www.)?[gG]ames\s?[sS]umo(\.com)?', 'GamesSumo'),
    (r'(www.)?[pP]pupu\s?[gG]ames(\.com)?', 'Pupu Games'),
    (r'(www.)?[pP]lay\s?[tT]oon\s?[gG]ames(\.com)?', 'Play Toon Games'),
    (r'(www.|^)[kK]ing\s?[gG]ames(\.net)?', 'King Games'),
    (r'(www.)?[iI]nka\s?[gG]ames(\.com)?', 'Inka Games'),
    (r'(www.)?[nN]ickelodeon(\.com)?', 'Nickelodeon'),
    (r'(www.)?1000([wW]eb)?\s?[gG]ames(\.com)?', '1000 Web Games'),
    (r'(www.)?123\s?[bB]ee(\.com)?', '123Bee'),
    (r'(www.)?123\s?[cC]hase(\.com)?', '123Chase'),
    (r'(www.)?123\s?[pP]eppy(\.com)?', '123peppy'),
    (r'(www.)?143\s?[dD]ressup(\.com)?', '143Dressup'),
    (r'(www.)?143\s?[kK]ids\s?[gG]ames(\.com)?', '143Kidsgames'),
    (r'(www.)?1[cC]oin1[pP]lay(\.com)?', '1Coin1Play'),
    (r'(www.)?1[cC]ooking\s?[gG]ames(\.com)?', '1CookingGames'),
    (r'(www.)?1[gG]ame[sS]ite(\.com)?', '1Gamesite'),
    (r'(www.)?2[dD]\s?[pP]lay(\.com)?', '2DPlay'),
    (r'(www.)?2[gG]ames(\.com)?', '2Games'),
    (r'(www.)?2[kK]eys\s?[gG]ames(\.com)?', '2keysGames'),
    (r'(www.)?2[pP][gG]ame(\.com)?', '2PGame'),
    (r'(www.)?4399(\.com)?', '4399'),
    (r'(www.)?4\s?[kK]ids(\sTV)(\.com)?', '4Kids'),
    (r'(www.)?4[vV]4(\.com)?', '4v4'),
    (r'(www.)?5[hH]ippos(\.com)?', '5Hippos'),
    (r'(www.)?5[xX][Pp][lL][aA][yY](\.com)?', '5xPLAY'),
    (r'(www.)?7DFPS\.com', '7DFPS'),
    (r'(www.)?8Bit\.com?', '8bit.com'),
    (r'(www.)?9[bB][gG]ames(\.com)?', '9bgames'),
    (r'(www.)?9[M]ine(\.com)?', '9mine'),
    (r'(www.)?[aA]ddicting\s?[gG]ames(\.com)?', 'Addicting Games'),
    (r'(www.)?[aA]lbino\s?[bB]lack[sS]heep(\.com)?', 'Albino Blacksheep'),
    (r'(www.)?[aA]ll\s?[fF]or\s?[gG]irls(\.net)?', 'AllForGirls'),
    (r'(www.)?[aA]ll[gG]ames[aA]ll[fF]ree(\.com)?', 'AllGamesAllFree'),
    (r'(www.)?[aA]rcade\s?[bB]omb(\.com)?', 'Arcadebomb'),
    (r'(www.)?[bB]aby\s?[dD]aisy\s?[gG]ames(\.com)?', 'Baby Daisy Games'),
    (r'(www.)?[bB]ig\s?[fF]ish\s?[gG]ames(\.com)?', 'Big Fish Games'),
    (r'(www.)?[bB]ox\s?10(\.com)?', 'Box10'),
    (r'(www.)?[bB]ubble[bB]ox(\.com)?', 'Bubblebox'),
    (r'(www.)?[cC]artoon\s?[rR]ace(\.com)?', 'CartoonRace'),
    (r'(www.)?[cC]huck\s[eE]\.?\s[cC]heese\'?s?(\.com)?', 'Chuck E. Cheese\'s'),
    (r'(www.)?[cC]lick\s?[jJ]ogos(\.com)?(\.br)?', 'Click Jogos'),
    (r'(www.)?[cC]oca\s?\-?[cC]ola(\.com)?', 'Coca-Cola'),
    (r'(www.)?[cC]ooking\s?[gG]ames(\.com)?', 'Cooking Games'),
    (r'(www.)?[cC]ooking\s?[pP]ink(\.com)?', 'Cooking Pink'),
    (r'(www.)?[cC]ool\s?[bB]udd?y(\.com)?', 'Coolbuddy.com'),
    (r'(www.)?[cC]ool\s?[gG]ames\s?[bB]ox(\.com)?', 'Cool Games Box'),
    (r'(www.)?[cC]ool\s?[mM]ath[\s\-]?[gG]ames(\.com)?', 'Cool Math Games'),
    (r'(www.)?[cC]ool\s?[mM]ath(\.com)?(, Inc.)?', 'Cool Math'),
    (r'(www.)?[cC]ool\s?[tT]emple(\.com)?', 'Cool Temple'),
    (r'(www.)?[cC]razy\s?[gG]ames(\.com)?', 'Crazy Games'),
    (r'(www.)?[cC]osmictopia(\.com)?', 'Cosmictopia'),
    (r'(www.)?[cC]ute\s?[fF]lash[gG]ames(\.com)?', 'Cute Flash Games'),
    (r'(www.)?[dD]aily\s?[gG]ames(\.com)?', 'Daily Games'),
    (r'(www.)?[dD]aily\s?[bB]ike\s?[gG]ames(\.com)?', 'Daily Bike Games'),
    (r'(www.)?[dD]annyz\s?[gG]ames(\.com)?', 'DannyzGames'),
    (r'(www.)?[dD]aria\s?[gG]ames(\.com)?', 'Daria Games'),
    (r'(www.)?[dD]ark\s?[hH]orror\s?[gG]ames(\.com)?', 'Dark Horror Games'),
    (r'(www.)?[dD]ede\s?[gG]ames(\.com)?', 'Dedegames'),
    (r'(www.)?[dD]evilish\s?[fF]ree(\.com)?', 'DevilishFree'),
    (r'(www.)?[dD]ibblez(\.com)?', 'Dibblez'),
    (r'(www.)?[dD]idi\s?[gG]ames(\.com)?', 'Didi Games'),
    (r'(www.)?[dD]ifference\s?[gG]ames(\.com)?', 'DifferenceGames'),
    (r'(www.)?[dD]ili\s?[gG]ames(\.com)?', 'Diligames'),
    (r'(www.)?[dD]ino\s?[hH]ill(\.com)?', 'DinoHill'),
    (r'(www.)?[dD]iscovery\s?[kK]ids\s?([pP]lay)?([pP]lus)?(\.com)?', 'Discovery Kids'),
    (r'(www.)?[dD]isney(\.(com|ru|co\.uk))?', 'Disney'),
    (r'(www.)?[dD]isney\s?[pP]rincess\s?[gG]ames(\.com)?', 'Disney Princess Games'),
    (r'(www.)?[dD]l[sS]ite(\.com)?', 'DLsite'),
    (r'(www.)?[dD]oli\s?[dD]oli(\.com)?', 'DoliDoli'),
    (r'(www.)?[dD]oll\s?[dD]ivine(\.com)?', 'Doll Divine'),
    (r'(www.)?[dD]olly\s?[gG]als(\.com)?', 'DollyGals'),
    (r'(www.)?[dD]ona\s?[gG]ames(\.com)?', 'Donagames'),
    (r'(www.)?[dD]ouble\s?[gG]ames(\.com)?', 'DoubleGames'),
    (r'(www.)?[dD]oyu\s?[gG]ames(\.com)?', 'Doyu Games'),
    (r'(www.)?[dD]ragon\s?[gG]amez(\.com)?', 'Dragon Gamez'),
    (r'(www.)?[dD]ream[wW]orks(\s?[aA]nimation(\sLCC)?)?(\.com)?', 'DreamWorks'),
    (r'(www.)?[fF]lash\s?[gG]ames\s?247(\.com)?', 'Flash Games 247'),
    (r'(www.)?[pP][iI][xX][aA][rR](\.com)?', 'Pixar')
    ]

WAYBACK_REGEX = r'(?i)\s\(?(via\s?)?(the\s?)?\(?wayback?\s?(machine)?\)?'

# Trim spaces and break lines
strip_all = lambda value: value.strip('\r\n').strip('\n').strip('\t').strip().replace('\n\n\n', '\n\n').replace('\r\n\r\n\r\n', '\r\n\r\n')

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
                        try: html_source = requests.get("https://web.archive.org/web/2id_/"+url)
                        except: continue
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
full_query = 'SELECT id, title, alternateTitles, developer, publisher, source, launchCommand, releaseDate, originalDescription, language, tagsStr FROM game'
cursor.execute(full_query)

meta_list = ['id', 'title', 'alternateTitles', 'developer', 'publisher', 'source', 'launchCommand', 'releaseDate', 'originalDescription', 'language', 'tagsStr'] #dirty hack
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
    
    # Language
    new_lang = re.sub(r'(;)?(\s)?$', '', query_item['language'].strip().replace("  ", " ")).replace(" ;", ";")
    if query_item['language'] != new_lang:
        cursor.execute('UPDATE game SET language = (?) WHERE id = (?)', (new_lang, query_item['id']))
        changelog += "LANGUAGE - (TRIMMED TO) -> " + new_lang + '\n'
        
    # Tags
    # Adventure = all but Role-Playing
    # Arcade = all but Clicker, Runner, Variety
    # Sports = all but Archery, Cycling, Swimming, Racing
    # Puzzle = all but Maze, Matching, Stealth
    # Simulation = all but Driving, Flying, Gambling
    # Strategy = all but Turn-Based
    # Others get either specfic tags or all subtags
    tag_list = {
        'Action': ['Run \'n\' Gun'],
        'Adventure': ['Choose Your Own Adventure', 'Dating Simulator', 'Dungeon Crawler', 'Escape the Room', 'Interactive Fiction', 'Metroidvania', 'MMO', 'Point and Click', 'Survival', 'Visual Novel'],
        'Arcade': ['Balancing', 'Button Masher', 'Bounce', 'Brick Breaker', 'Claw Game', 'Catching', 'Cross the Road', 'Endless Flyer', 'Endless Jumper', 'Fixed Shooter', 'Food Chain', 'Launch', 'Pellet Maze', 'Pinball', 'Pong', 'Rhythm', 'Rock-Paper-Scissors', 'Score-Attack', 'Snake', 'Stacking', 'Tetris', 'Timing', 'Toss', 'Whack-A-Mole'],
        'Card': ['Ace Trumps', 'Blackjack', 'Collectible Card Game', 'Poker', 'Shedding', 'Solitaire'],
        'Educational': ['Computer Science', 'Science'],
        'Puzzle': ['Codebreaker', 'Connect the Dots', 'Find', 'Hangman', 'Hidden Objects', 'Jigsaw', 'Lemmings', 'Logic', 'Marble Popper', 'Match-3', 'Memory', 'Minesweeper', 'Mixing', 'Nonogram', 'Peg Solitaire', 'Pipe Connector', 'Sequential', 'Sliding', 'Sokoban', 'Spot the Difference', 'Sudoku', 'Tile Merger', 'Vertical Drop', 'Word'],
        'Simulation': ['Babysitting', 'Bingo', 'Cooking', 'Cleaning', 'Dentist', 'Dice', 'Doctor', 'Farming', 'Fishing', 'Hairdressing', 'Hunting', 'Luck Roller', 'Mahjong', 'Parking', 'Pet', 'Restaurant', 'Slot Machine', 'Spa', 'Surgery', 'Repairing', 'Tabletop', 'Tattoo Artist', 'Time Management', 'Tycoon', 'Virtual World', 'Walking Simulator'],
        'Sports': ['American Football', 'Athletics', 'Baseball', 'Basketball', 'Billiards', 'Boating', 'Bowling', 'Boxing', 'Cricket', 'Curling', 'Equestrianism', 'Golf', 'Hockey', 'Motocross', 'Skateboarding', 'Skating', 'Skiing', 'Snowboarding', 'Soccer', 'Surfing', 'Tennis', 'Volleyball'],
        'Strategy': ['Ataxx', 'Battleship', 'Checkers', 'Chess', 'Domiones', 'Lane-Based Strategy', 'Node-Based Strategy', 'Real-Time Strategy', 'Reversi', 'Tower Defense', 'Tic-Tac-Toe'],
        'Game Jam': ['7DRL Challenge', 'BC Game Jam', 'BenBonk Game Jam', 'Butterscotch ShenaniJam', 'Casual Gameplay Design Competition', 'Decade Jam', 'Game Maker\'s Toolkit Game Jam', 'Game in Ten Days', 'Global Game Jam', 'Homestuck Game Jam', 'Lisp Game Jam', 'LOWREZJAM', 'Ludum Dare', 'Make-A-Thing Jam', 'Metroidvania Month', 'Mini Jam', 'NG Game Jam', 'Nokia 3310 Jam', 'Nordic Game Jam', 'One Game a Month', 'Pastel Jam', 'Pizza Jam', 'SPJam', 'Starmen.Net Funfest', 'Stencyl Jam', 'The Boob Jam', 'Touhou Fan Game Jam', 'xkcd Game Jam'],
        'Pixel': ['GB Studio', 'PICO-8', 'LOWREZJAM', 'Nokia 3310 Jam'],
        'Sexual Content': ['Anal', 'Anal Insertion', 'Anilingus', 'Cunnilingus', 'Fellatio', 'Fingering', 'Fisting', 'Footjob', 'Frottage', 'Handjob', 'Masturbation', 'Oral', 'Paizuri', 'Sex Toys', 'Tentacles', 'Touching', 'Tribadism', 'Vaginal', 'Vaginal Insertion'],
        'Adult': ['Anal', 'Anal Insertion', 'Anilingus', 'Cunnilingus', 'Fellatio', 'Fingering', 'Fisting', 'Footjob', 'Frottage', 'Handjob', 'Masturbation', 'Oral', 'Paizuri', 'Sex Toys', 'Tentacles', 'Touching', 'Tribadism', 'Vaginal', 'Vaginal Insertion', 'Hentai', 'Cartoon Porn', 'Porn', 'BDSM', 'Bestiality', 'Breast Milking', 'Cannibalism', 'Enema', 'Gloryhole', 'Incest', 'Necrophilia', 'Oviposition', 'Podophilia', 'Quicksand', 'Vore']
    }
    for parent_tag in tag_list:
        for child_tag in tag_list[parent_tag]:
            # We want to be sure the searched tag isnt just part of another, ex. 'Shooter' may be from 'First Person Shooter'
            if re.search(r'(?<!\w )'+child_tag+r'(;|$)', query_item['tagsStr']) and not re.search(r'(?<!\w )'+parent_tag+r'(;|$)', query_item['tagsStr']):
                cursor.execute('UPDATE game SET tagsStr = (?) WHERE id = (?)', (query_item['tagsStr'] + '; ' + parent_tag, query_item['id']))
                cursor.execute('SELECT tagId FROM tag_alias where name = (?) LIMIT 1', (parent_tag,))
                tagId = cursor.fetchone()[0]
                try: # Tag may be already in its proper table and just wasnt in tagsStr
                    cursor.execute('INSERT INTO game_tags_tag (gameId, tagId) VALUES ( (?), (?) )', (query_item['id'], tagId))
                    changelog += 'TAGS - Added <' + parent_tag + '> due to <' + child_tag + '>\n'
                except: pass

    #Developer
    if query_item['developer'] != '':
        new_developer = strip_all(query_item['developer'])
        for list_publisher_regex in publisher_list:
            if re.search(list_publisher_regex[0], new_developer):
                new_developer = re.sub(list_publisher_regex[0], list_publisher_regex[1], new_developer)
        if new_developer != query_item['developer']:
            cursor.execute('UPDATE game SET developer = (?) WHERE id = (?)', (new_developer, query_item['id']))
            changelog += "DEVELOPER - " + query_item['developer'] + " -> " + new_developer + '\n'
    
    #Publisher
    if query_item['publisher'] != '':
        new_publisher = strip_all(query_item['publisher'])
        for list_publisher_regex in publisher_list:
            if re.search(list_publisher_regex[0], new_publisher):
                new_publisher = re.sub(list_publisher_regex[0], list_publisher_regex[1], new_publisher)
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
                        cursor.execute('UPDATE game SET source = (?) WHERE id = (?)', (testing_source, query_item['id']))
                        changelog += "SOURCE - " + query_item['source'] + " -> " + testing_source + '\n'
                except: pass
                break
    else:
        testing_source = re.sub(WAYBACK_REGEX, " (via Wayback Machine)", strip_all(testing_source))
        if testing_source != None and testing_source != query_item['source']:
            cursor.execute('UPDATE game SET source = (?) WHERE id = (?)', (testing_source, query_item['id']))
            changelog += "SOURCE - " + query_item['source'] + " -> " + testing_source + '\n'

    # Developer, Release Date, Original Description = online search
    no_publisher = query_item
    no_publisher.pop('publisher')
    no_publisher.pop('alternateTitles')
    no_publisher.pop('language')
    no_publisher.pop('tagsStr')
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
        
    # Change dateModified, add to changelog
    if len(changelog) > 37: #id + \n
        cursor.execute('UPDATE game SET dateModified = (?) WHERE id = (?)', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query_item['id']))
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
    print("ERROR: Could not write into the sqlite.")
    raise

print (str(changes_counter) + ' curations changed.')

# Create changelog file
if len(full_changelog) > 21:
    f = open("changelog.txt", "w", encoding="utf-8")
    f.write(full_changelog)
    f.close()
