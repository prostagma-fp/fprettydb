# fprettydb

fprettydb is a fpclib powered tool to fix and get metadata for Flashpoint's curations. The basic usage is to move Flashpoint's sqlite to the script's folder and run `dbfix.py`. Most site definitions including fpcurator.py are shortened from [fpcurator](https://github.com/FlashpointProject/fpcurator).

Will scan all curation and do these fixes:
* No leading/trailing spaces and break lines from titles and original descriptions
* Fixes the release date format (YYYY-MM-DD) from dates without zeroes
* Streamlines the names of publishers
* Fixes incomplete sources based on launch command
* Fetches missing developer, release date and original description from the source
