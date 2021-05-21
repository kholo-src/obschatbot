# OBS Chat Bot (obschatbot)
A Twitch chat-bot that could directly interact with OBS Studio and Spotify


## Requirements
- python >= 3.6
- requests


## Usage


### Installation
Extract to your working directory, and import obschatbot.py in OBS-Studio Scripts window.


### Configuration

#### Greeting messages (optional)
You can set greeting messages in "Welcome message" (at bot start) and "Farewell message" (at bot stop) fields.

#### Twitch IRC (mandatory)
"Nickname" is the bot's username (existing Twitch account).  
"Password" is the bot's OAuth generated password for Twitch (https://twitchapps.com/tmi/ - you must be logged in with your bot account if different from yours to confirm this step)  
"Channel" is your Twitch streaming channel name.

#### Services (optional)
Services are optional sets of commands for your bot, you can enable them by ticking the checkbox for each of them.

##### Command Service
This service allows your bot to receive custom commands. Only moderators and broadcasters can define them.  
The custom commands are stored in a text file, defined in "Commands list" field.
###### adding a command
```!cmd add <command name> <printed text>```
"add", "edit" and "update" have the same results.  
"\<command name\>" with or without the "!" (exclamation mark) character will have the same result. Custom commands are always used with the "!" prefix.  
"\<printed text\>" is the text returned by the custom command. It can support multiple arguments, for instance:  
- ```!cmd add !so Shout out to {1} for being an awesome person, please visit https://twitch.tv/{1}``` where {1} will be replaced by the first argument following the custom command, like in "!so kholo" will result in "Shout out to kholo for being an awesome person, please visit https://twitch.tv/kholo" (I'm kholo by the way :D ) (and I... may... be that awesome! Who knows?)
- ```!cmd add !vs Hey look out, {1} and {2} are fighting! Taking the bets!``` where {1} will be replaced by the first argument, {2} by the second argument, and so on. "!vs kholo anonlogics" will result in "Hey look out, kholo and anonlogics are fighting! Taking the bets!" (anonlogics is my bot, powered by the very current script) (and I think it will beat the hell out of me)

It also supports multiple responses, separated with "||" (two vertical bars), that will be returned randomly when invoking the custom command, for instance:  
```!cmd add !dance (_\_) (_|_) (_/_)||\o\ |o| /o/``` will make the "!dance" command returns either "(\_\\\_) (\_|\_) (\_/\_)" or "\o\ |o| /o/"
###### removing a command
```!cmd del <command name>```
"del", "delete" and "remove" have the same results.
###### custom commands
Added commands are triggered by calling their name prefixed with a "!" (exclamation mark) character, and can receive arguments if defined in the <printed text>.

##### Dice Service
This service allows your viewers to roll dices in your chat room.
###### rolling a dice
```!<n>d<f>```
where <n> is the number of dices to roll, and <f> the number of faces per dice. For instance: ```!5d6``` will roll five dices with six faces each.
###### getting the last roll resuls
```!lastrolls```
This command prints the last rolls for every viewer in the chat room who has rolled dices.
###### clearing the last roll results
```!clearlast```
This command clears the last rolls for every viewer in the chat room.

##### Spotify Service
This service allows your viewers to add or remove song from a given playlist. This will requires you to have a developer account (you can create one at https://developer.spotify.com/) and to create an application in your dashboard.  
"Playlist ID" is the ID of the playlist you want to give your viewers controls to. You can get this information by right-clicking your playlist in Spotify, "Share">"Copy Playlist Link", pasting the URL in any notepad application, and keeping the part between ".../playlist/" and "?si=..." from the URL. For instance: in "https://open.spotify.com/playlist/1a1ABC2DE34FghIJKlmno5?si=1a2b34c5defa6b7c", keep the "1a1ABC2DE34FghIJKlmno5" part.  
"Client ID" is your application Client ID (found in Spotify developer dashboard)  
"Client Secret" is your application Client Secret (found in Spotify developer dashboard)  
Once "Client ID" and "Client Secret" is set, you will have to click the "Authenticate" button to create an authorization token. This will open a new browser window or tab where you will have to confirm the access to the application. This step has to be done only once, not every time you start the bot.
###### adding a song to the playlist
```!addsong <query>```
This will search for a track with \<query\> keywords, and add the track to the playlist if found.
###### removing the last added song
```!dellast```
Each viewer can remove the last song they added to the playlist during the current bot session using this command.
###### displaying the playlist
```!playlist```
The bot will print the playlist URL.

  
### Start and stop
Simply use the "Start Bot" and "Stop Bot" buttons!

## Current status
The bot is fully working as is, however no error or exception are currently catched. Interaction with OBS is yet to come (probably a new service, like "OBSService"). It should allow to enable/disable sources tagged as interactive in the configuration window, and change scenes tagged as interactive, using chat commands. Maybe some text replacements, or color changes can be done as well.  
Please be cautious using the Spotify Service will streaming: Live DMCA strike is a thing, and it's coming. I'll keep the SpotifyService there because rules can change, and I learnt to request Web API using OAuth writing this one, but it's usability may be a problem for legal reasons.
