from ChatBot import ChatBot
from obspython import *
from services.CommandService import CommandService
from services.DiceService import DiceService
from services.SpotifyService import SpotifyService
from threading import Thread

DESCRIPTION = "A Twitch chat bot that interacts with OBS and other services.\n\nby kholo"

chatbot = ChatBot()

services = {
    "command": {
        "service": CommandService(),
        "enabled": False
    },
    "dice": {
        "service": DiceService(),
        "enabled": False
    },
    "spotify": {
        "service": SpotifyService(),
        "enabled": False,
        "settings": {
            "spotify_token": ""
        }
    }
}

def set_services():
    chatbot.clear_services()
    for name, service in services.items():
        if service["enabled"]:
            print(f"- Enabling service {name}")
            chatbot.add_service(service["service"])

# Callbacks -----

def start(props, prop):
    print("[--- STARTING THE BOT ---]")
    print("Setting the enabled services")
    set_services()
    print("Creating the thread and starting the bot")
    thread = Thread(target=chatbot.start)
    thread.daemon = True
    thread.start()
    print("Bot started\n[--- /STARTING THE BOT ---]")

def stop(props, prop):
    print("[--- STOPPING THE BOT ---]")
    chatbot.stop()
    print("Bot stopped\n[--- /STOPPING THE BOT ---]")

def auth_spotify(props, prop):
    print("[--- AUTHORIZING SPOTIFY ---]")
    print("This will open a new tab or window in your browser, where you will have to confirm the authorization.")
    services["spotify"]["settings"]["spotify_token"] = services["spotify"]["service"].get_authorization()
    print("You can close the browser window with the error message.\nAuthorization complete.\n[--- /AUTHORIZING SPOTIFY ---]")

# Helpers -----

def create_twitch_irc_properties():
    props = obs_properties_create()
    obs_properties_add_text(props, "irc_nickname", "Nickname", OBS_TEXT_DEFAULT)
    obs_properties_add_text(props, "irc_password", "OAuth Password", OBS_TEXT_PASSWORD)
    obs_properties_add_text(props, "irc_channel", "Channel", OBS_TEXT_DEFAULT)
    return props

def create_cmd_properties():
    props = obs_properties_create()
    obs_properties_add_path(props, "cmd_file", "Commands list", OBS_PATH_FILE, "Text file (*.txt)", None)
    return props

def create_dice_properties():
    props = obs_properties_create()
    return props

def create_spotify_properties():
    props = obs_properties_create()
    obs_properties_add_text(props, "spotify_playlist_id", "Playlist ID", OBS_TEXT_DEFAULT)
    obs_properties_add_text(props, "spotify_client_id", "Client ID", OBS_TEXT_DEFAULT)
    obs_properties_add_text(props, "spotify_client_secret", "Client Secret", OBS_TEXT_PASSWORD)
    obs_properties_add_button(props, "spotify_auth", "Authenticate", auth_spotify)
    token = obs_properties_add_text(props, "spotify_token", "Refresh Token", OBS_TEXT_DEFAULT)
    obs_property_set_visible(token, False)
    return props

# OBS functions -----

def script_description():
    return DESCRIPTION

def script_load(settings):
    for service in services.values():
        if "settings" in service:
            for key in service["settings"]:
                service["settings"][key] = obs_data_get_string(settings, key)

def script_properties():
    props = obs_properties_create()
    obs_properties_add_button(props, "start", "Start Bot", start)
    obs_properties_add_button(props, "stop", "Stop Bot", stop)
    obs_properties_add_group(props, "irc", "Twitch IRC", OBS_GROUP_NORMAL, create_twitch_irc_properties())
    obs_properties_add_group(props, "command", "Command Service", OBS_GROUP_CHECKABLE, create_cmd_properties())
    obs_properties_add_group(props, "dice", "Dice Service", OBS_GROUP_CHECKABLE, create_dice_properties())
    obs_properties_add_group(props, "spotify", "Spotify Service", OBS_GROUP_CHECKABLE, create_spotify_properties())
    return props

def script_update(settings):
    chatbot.set_twitch_irc_settings(
        obs_data_get_string(settings, "irc_nickname"),
        obs_data_get_string(settings, "irc_password"),
        obs_data_get_string(settings, "irc_channel"),
    )
    if obs_data_get_bool(settings, "command"):
        services["command"]["enabled"] = True
        services["command"]["service"].set_file(obs_data_get_string(settings, "cmd_file"))
    else:
        services["command"]["enabled"] = False
    if obs_data_get_bool(settings, "dice"):
        services["dice"]["enabled"] = True
    else:
        services["dice"]["enabled"] = False
    if obs_data_get_bool(settings, "spotify"):
        services["spotify"]["enabled"] = True
        services["spotify"]["service"].set_playlist(obs_data_get_string(settings, "spotify_playlist_id"))
        services["spotify"]["service"].set_credentials(
            obs_data_get_string(settings, "spotify_client_id"),
            obs_data_get_string(settings, "spotify_client_secret")
        )
        if obs_data_get_string(settings, "spotify_token") != "":
            services["spotify"]["service"].set_refresh_token(obs_data_get_string(settings, "spotify_token"))
    else:
        services["spotify"]["enabled"] = False

def script_save(settings):
    for service in services.values():
        if "settings" in service:
            for key, value in service["settings"].items():
                obs_data_set_string(settings, key, value)