import config
import pickle

users = {}


class User:
    def __init__(self, discord_id):
        self.discord_id = discord_id
        self.new_jersey_count = 0
        self.last_song_skip = 0
        self.skip_count = 0
        self.jersey_coins = 0

    def save(self):
        user_f = open(f"{config.user_save_dir}/{self.discord_id}", "wb")
        pickle.dump(self, user_f)
        user_f.close()


def get_user(id: int) -> User:
    if not isinstance(id, int):
        raise TypeError("User id must be type int")
    if id not in users:
        users[id] = User(id)
    return users[id]


def increment_user(id: int) -> int:
    user = get_user(id)
    user.new_jersey_count += 1
    user.save()
    return user.new_jersey_count
