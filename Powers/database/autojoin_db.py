from threading import RLock

from Powers.database import MongoDB

INSERTION_LOCK = RLock()


class AUTOJOIN(MongoDB):
    """class to store auto join requests"""

    db_name = "autojoin"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def load_autojoin(self, chat, mode="auto"):
        """
        type = auto or notify
        auto to auto accept join requests
        notify to notify the admins about the join requests
        """
        curr = self.find_one({"chat_id": chat, })
        if not curr:
            with INSERTION_LOCK:
                self.insert_one({"chat_id": chat, "type": mode})
            return True
        return False

    def get_autojoin(self, chat):
        curr = self.find_one({"chat_id": chat})
        return curr["type"] if curr else False

    def update_join_type(self, chat, mode):
        if curr := self.find_one({"chat_id": chat}):
            self.update({"chat_id": chat}, {"type": mode})
        return

    def remove_autojoin(self, chat):
        if curr := self.find_one({"chat_id": chat}):
            self.delete_one({"chat_id": chat})
        return
