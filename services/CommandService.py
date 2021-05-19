from services.Service import Service
import os.path
import re

KNOWN_COMMANDS = ["cmd"]

MSG_CANT_MANAGE = "Il faut être modérateur pour faire ça"
MSG_UNKNOWN = "Je ne connais pas cette commande"
MSG_WRONG_ARG_COUNT = "La commande est mal utilisée."

SEPARATOR = ";"
SUBST_SEP = ".,"
PATTERN_ARGS = "\{[0-9]+\}"

class CommandService(Service):

    file = ""
    commands = {}

    # Service -----

    def knows(self, command):
        return command in self.list_commands()

    def eval(self, command, response, users):
        if command == "cmd":
            return self.manage(response)
        else:
            return self.custom(response["message"])

    def list_commands(self):
        return KNOWN_COMMANDS + list(self.commands.keys())

    def start(self):
        if self.file == "" or not os.path.isfile(self.file):
            return
        with open(self.file) as file:
            content = file.read().splitlines()
        for line in content:
            self.load_command(line)

    def load_command(self, line):
        components = line.split(SEPARATOR)
        self.commands[components[0]] = components[1].replace(SUBST_SEP, SEPARATOR)

    # Settings -----

    def set_file(self, file):
        self.file = file

    # Commands -----

    def manage(self, response):
        can_manage = False
        for badge in response["tags"]["badges"]:
            if badge["name"] in ["broadcaster", "moderator"]:
                can_manage = True
        if not can_manage:
            return f"{MSG_CANT_MANAGE}, @{response['username']}"
        command, action, target_command, args = response["message"].split(" ", 3)
        if action in ["add", "edit", "update"]:
            return self.add_command(target_command, args) + f" ,@{response['username']}"
        elif action in ["del", "delete", "remove"]:
            return self.del_command(target_command) + f" ,@{response['username']}"
        else:
            return f"{MSG_UNKNOWN}, @{response['username']}"

    def add_command(self, command, args):
        self.commands[command.lstrip("!")] = args
        self.write()
        return f"La commande '!{command}' a été ajoutée"

    def del_command(self, command):
        if command not in self.commands:
            return f"La commande '!{command}' n'existe pas"
        self.commands.pop(command)
        self.write()
        return f"La commande '!{command}' a été supprimée"

    def write(self):
        with open(self.file, "w") as file:
            for name in self.commands:
                file.write(f"{name}{SEPARATOR}{self.commands[name].replace(SEPARATOR, SUBST_SEP)}\n")

    def custom(self, message):
        components = message.split(" ", 1)
        command = self.commands.get(components[0][1:])
        args = list(dict.fromkeys(re.findall(PATTERN_ARGS, command)))
        args.sort()
        count = len(args)
        if count >= 1:
            msg_components = []
            if len(components) > 1:
                msg_components = components[1].split(" ")
            if len(msg_components) != count:
                return MSG_WRONG_ARG_COUNT
            for i in range(0, count):
                command = command.replace(args[i], msg_components[i].lstrip("@"))
        return command
