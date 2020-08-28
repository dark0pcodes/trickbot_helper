# TrickbotHelper

Easy-to-use Python library to interact with the Trickbot Botnet. 

This work is based on:

* https://github.com/MalwareTech/TrickBot-Toolkit
* https://gist.github.com/hasherezade/88837ea728d3950c7c38160d016ea6cf 

## How to install it?

To install it just copy and paste the following line.

````
pip install git+ssh://git@github.com/dark0pcodes/trickbot_helper.git
````


## How to use it?

To use this library you first need at least an active trickbot server that will be contacted to fetch additional content. 
Below an example is provided.

````
from trickbot_helper.bot import Bot

bot = Bot('CONFIG_VER')

########################################################################################################################
# The following commands MUST be run against trickbot config servers found in the "<mcconf>" XML

# Register the bot in a server and fetch list of servers used to download additional files
module_servers = bot.register(server, port)

# Get updated configuration, works only after bot has been registered into a C2C
server_list, ver, gtag = bot.get_updated_config(server, port)

# Get list of exfiltration servers
dpost = bot.get_dpost(server, port)

# Get list of servers to send harvested email list to
mailconf = bot.get_mailconf(server, port)

# Get list of targets and web-injects-related servers 
dinj = bot.get_dinj(server, port)

# Get update link
update_link = bot.get_update_link(server, port)

########################################################################################################################
# To download modules using the "get_file" command you MUST use one of the servers returned by the command
"register" 

# Download module
file_buffer = bot.get_file(server, port, 'module_name')
````

Note: Additional modules can only be downloaded from the list of servers provided by the botnet after register the bot.

Available modules are:

* importDll32 / importDll64
* injectDll32 / injectDll64
* mshareDll32 / mshareDll64
* mwormDll32 / mwormDll64
* networkDll32 / networkDll64
* pwgrabDll32 / pwgrabDll64
* tabDll32 / tabDll64
* mailsearcher32 / mailsearcher64
* cookiesDll32 / cookiesDll64
* NewBCtestDll32 / NewBCtestDll64
* psfin32 / psfin64
* vncDll32 / vncDll64
* outlookDll32 / outlookDll64
* domainDll32 / domainDll64
