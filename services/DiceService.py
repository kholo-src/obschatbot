from services.Service import Service
import random
import re

KNOWN_COMMANDS = ["last_rolls", "clear_rolls"]
USER_KEY = "last_dice_roll"

MSG_CLEARED = "Les résultats ont été effacés"

PATTERN_DICE = "^([0-9]+)d([0-9]+)$"

class DiceService(Service):

    # Service -----

    def knows(self, command):
        return command in KNOWN_COMMANDS or re.match(PATTERN_DICE, command)

    def eval(self, command, response, users):
        if command == "last_rolls":
            return self.get_last_rolls(users)
        elif command == "clear_rolls":
            return self.clear_rolls(users) + f", @{response['username']}"
        else :
            m = re.match(PATTERN_DICE, command)
            dices = self.roll_dices(int(m.group(1)), int(m.group(2)))
            self.save_last_roll(users, response["username"], dices)
            return f"🎲 {response['username']} a obtenu {' + '.join(dices)} 🎲"

    def list_commands(self):
        return ["<n>d<f> (n=nombre de dés, f=nombre de faces"] + KNOWN_COMMANDS

    # Commands -----

    def get_last_rolls(self, users):
        results = []
        for user in users:
            if USER_KEY in users[user]:
                results.append(f"{user} : {users[user][USER_KEY]}")
        return " 🎲 ".join(results)

    def clear_rolls(self, users):
        for user in users:
            if USER_KEY in users[user]:
                users[user].pop(USER_KEY)
        return MSG_CLEARED

    def roll_dices(self, number, faces):
        dices = []
        for i in range(0, number):
            dices.append(str(random.randint(1, faces)))
        return (dices)

    def save_last_roll(self, users, username, dices):
        if username not in users:
            users[username] = {}
        users[username][USER_KEY] = dices