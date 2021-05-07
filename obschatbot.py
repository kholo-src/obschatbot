from ChatBot import *
from threading import Thread
import obspython as obs

chatbot = ChatBot()

def start_bot():
    global chatbot
    chatbot.start()

def stop_bot():
    global chatbot
    chatbot.stop()

def start(props, prop):
    global thread
    thread.start()

def stop(props, prop):
    global thread
    stop_bot()
    thread.join()

thread = Thread(target=start_bot)
thread.daemon = True

# OBS functions -----

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "channel", "#channel")

def script_description():
    return "Twitch chat bot that could directly interact with OBS Studio.\n\nBy kholo"

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "channel", "Channel name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "nickname", "IRC username", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "password", "IRC password", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_button(props, "start", "Start", start)
    obs.obs_properties_add_button(props, "stop", "Stop", stop)
    return props

def script_update(settings):
    global chatbot
    chatbot.set_channel(obs.obs_data_get_string(settings, "channel"))
    chatbot.set_user(obs.obs_data_get_string(settings, "nickname"), obs.obs_data_get_string(settings, "password"))
