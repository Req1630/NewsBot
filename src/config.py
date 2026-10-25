import json

class config:
    def __init__(self):
        self.config_path = ".config/config.json"
        self.configs = {}

    def load(self):
        with open(self.config_path, "r") as f:
            d = json.load(f)
            self.configs = d["config"]
            return True
        return False

    def get_check_interval_minutes(self):
        return int(self.configs["check_interval_minutes"])
            
