import os.path

class CommandManager:

    file = ""
    commands = {}

    def set_file(self, file):
        self.file = file

    def load(self):
        if self.file == "" or not os.path.isfile(self.file):
            return
        with open(self.file) as file:
            content = file.read().splitlines()
        for line in content:
            self.load_command(line)

    def load_command(self, line):
        components = line.split(";")
        self.commands[components[0]] = components[1].replace("..,,", ";")

    def add_command(self, name, message):
        self.commands[name] = message
        self.write()

    def del_command(self, name):
        self.commands.pop(name)
        self.write()

    def write(self):
        with open(self.file, "w") as file:
            for name in self.commands:
                file.write(name + ";" + self.commands[name].replace(";", "..,,") + "\n")

    def has(self, name):
        return name in self.commands

    def list(self):
        return self.commands.keys()

    def get(self, name):
        return self.commands[name]
