from threading import RLock

from Powers.database import MongoDB

INSERTION_LOCK = RLock()


class AFK(MongoDB):
    """Class to store afk users"""
    db_name = "afk"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def insert_afk(self, chat_id, user_id, time, reason, media_type, media=None):
        with INSERTION_LOCK:
            if curr := self.check_afk(chat_id=chat_id, user_id=user_id):
                if reason:
                    self.update({"chat_id": chat_id, "user_id": user_id}, {
                        "reason": reason, "time": time})
                if media:
                    self.update({"chat_id": chat_id, "user_id": user_id}, {
                        'media': media, 'media_type': media_type, "time": time})
            else:
                self.insert_one(
                    {
                        "chat_id": chat_id,
                        "user_id": user_id,
                        "reason": reason,
                        "time": time,
                        "media": media,
                        "media_type": media_type
                    }
                )
            return True

    def check_afk(self, chat_id, user_id):
        return bool(curr := self.find_one({"chat_id": chat_id, "user_id": user_id}))

    def get_afk(self, chat_id, user_id):
        if curr := self.find_one({"chat_id": chat_id, "user_id": user_id}):
            return curr
        return

    def delete_afk(self, chat_id, user_id):
        with INSERTION_LOCK:
            if curr := self.check_afk(chat_id, user_id):
                self.delete_one({"chat_id": chat_id, "user_id": user_id})
            return
