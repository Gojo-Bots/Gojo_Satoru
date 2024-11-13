from threading import RLock

from Powers.database import MongoDB

INSERTION_LOCK = RLock()


class Floods(MongoDB):
    """Class to store flood limit and action of a chat"""
    db_name = "flood"

    def __init__(self):
        super().__init__(self.db_name)

    def save_flood(
            self,
            chat_id: int,
            limit: int,
            within: int,
            action: str,
    ):
        with INSERTION_LOCK:
            if not (curr := self.find_one({"chat_id": chat_id})):
                return self.insert_one(
                    {
                        "chat_id": chat_id,
                        "limit": limit,
                        "within": within,
                        "action": action
                    },
                )
            if (
                    limit != int(curr['limit'])
                    or within != int(curr['within'])
                    or action != str(curr['action'])
            ):
                return self.update(
                    {
                        "chat_id": chat_id
                    },
                    {
                        "limit": limit,
                        "within": within,
                        "action": action,
                    }
                )
            else:
                return

    def is_chat(self, chat_id: int):
        with INSERTION_LOCK:
            if curr := self.find_one({"chat_id": chat_id}):
                return [
                    str(curr['limit']),
                    str(curr['within']),
                    str(curr['action']),
                ]
            return False

    def get_action(self, chat_id: int):
        with INSERTION_LOCK:
            if curr := self.find_one({"chat_id": chat_id}):
                return curr['action']
            return "Flood haven't set"

    def rm_flood(self, chat_id: int):
        with INSERTION_LOCK:
            if curr := self.find_one({"chat_id": chat_id}):
                self.delete_one({"chat_id": chat_id})
                return True
            return False
