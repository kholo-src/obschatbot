from ChatBot import *
from obspython import *
from threading import Thread

DESCRIPTION = "Twitch chat bot thats interacts with OBS\n\nby kholo"

chatbot = ChatBot()
thread = Thread()

# Callable functions -----

def start(props, prop):
    global chatbot
    global thread
    thread = Thread(target=chatbot.start)
    thread.daemon = True
    thread.start()

def stop(props, prop):
    global chatbot
    global thread
    chatbot.stop()
    thread.join()

def get_spotify_code(props, prop):
    global chatbot
    print("TO GET AN AUTHORIZATION CODE FOR YOUR BOT (to do once)")
    print("Go to the following URL and validate")
    print(chatbot.get_spotify_code_url)
    print("You will get a ?code=<...> in your browser URL bar, copy that code in the 'Spotify Authorization Code'.")
    print("Then you can press the 'Authorize Spotify' button")

def auth_spotify(props, prop):
    global chatbot
    print("Now you will have to copy the following string in the 'Spotify refresh token'")
    print(chatbot.authorize_spotify())
    print("And you're done!")

# Helpers -----

def create_twitch_properties():
    twitch = obs_properties_create()
    obs_properties_add_text(twitch, "channel", "Twitch channel", OBS_TEXT_DEFAULT)
    obs_properties_add_text(twitch, "username", "Bot username", OBS_TEXT_DEFAULT)
    obs_properties_add_text(twitch, "password", "Bot oauth password", OBS_TEXT_PASSWORD)
    obs_properties_add_text(twitch, "msg_hi", "Greetings message", OBS_TEXT_DEFAULT)
    obs_properties_add_text(twitch, "msg_bye", "Farewell message", OBS_TEXT_DEFAULT)
    return twitch

def create_spotify_properties():
    spotify = obs_properties_create()
    obs_properties_add_text(spotify, "playlist_id", "Spotify playlist ID", OBS_TEXT_DEFAULT)
    obs_properties_add_text(spotify, "client_id", "Spotify client ID", OBS_TEXT_DEFAULT)
    obs_properties_add_text(spotify, "client_secret", "Spotify client secret", OBS_TEXT_PASSWORD)
    obs_properties_add_button(spotify, "get_spotify_code", "Get Spotify code", get_spotify_code)
    obs_properties_add_text(spotify, "spotify_code", "Spotify authorization code", OBS_TEXT_DEFAULT)
    obs_properties_add_button(spotify, "auth_spotify", "Authorize Spotify", auth_spotify)
    obs_properties_add_text(spotify, "spotify_refresh_token", "Spotify refresh token", OBS_TEXT_DEFAULT)
    return spotify

# OBS functions -----

def script_description():
    return DESCRIPTION

def script_defaults(settings):
    obs_data_set_default_string(settings, "msg_hi", "Bonjour, je suis à votre service. !aide ou !help pour en savoir plus.")
    obs_data_set_default_string(settings, "msg_bye", "Merci pour votre compagnie, au revoir.")

def script_properties():
    props = obs_properties_create()
    obs_properties_add_path(props, "cmd_file", "Commands list", OBS_PATH_FILE, "Text file (*.txt)", None)
    obs_properties_add_group(props, "twitch", "Twitch IRC settings", OBS_GROUP_NORMAL, create_twitch_properties())
    obs_properties_add_group(props, "spotify", "Spotify API settings", OBS_GROUP_NORMAL, create_spotify_properties())
    obs_properties_add_button(props, "start", "Start bot", start)
    obs_properties_add_button(props, "stop", "Stop bot", stop)
    return props

def script_update(settings):
    global chatbot
    chatbot.set_command_file(
        obs_data_get_string(settings, "cmd_file")
    )
    chatbot.set_messages(
        obs_data_get_string(settings, "msg_hi"),
        obs_data_get_string(settings, "msg_bye")
    )
    chatbot.set_twitch_settings(
        obs_data_get_string(settings, "channel"),
        obs_data_get_string(settings, "username"),
        obs_data_get_string(settings, "password")
    )
    chatbot.set_spotify_settings(
        obs_data_get_string(settings, "playlist_id"),
        obs_data_get_string(settings, "client_id"),
        obs_data_get_string(settings, "client_secret")
    )
    chatbot.set_spotify_code(obs_data_get_string(settings, "spotify_code"))
    chatbot.set_spotify_refresh_token(obs_data_get_string(settings, "spotify_refresh_token"))
