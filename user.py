import config
import pickle

users = {}

class User:
    def __init__(self, discord_id):
        self.discord_id = discord_id
        self.new_jersey_count = 0

    def save(self):
        user_f = open(config.user_save_dir + "/" + str(self.discord_id), "wb")
        pickle.dump(self, user_f)
        user_f.close()

def get_user(id):
    if not isinstance(id, int):
        return
    if id not in users:
        users[id] = User(id)
    return users[id]

