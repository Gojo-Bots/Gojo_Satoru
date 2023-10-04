from threading import RLock
from time import time

from Powers import LOGGER
from Powers.database import MongoDB

INSERTION_LOCK = RLock()


class AUTOJOIN(MongoDB):
    """class to store auto join requests"""

    db_name = "autojoin"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def load_autojoin(self, chat,mode="auto"):
        """
        type = auto or notify
        auto to auto accept join requests
        notify to notify the admins about the join requests
        """
        curr = self.find_one({"chat_id":chat,})
        if not curr:
            with INSERTION_LOCK:
                self.insert_one({"chat_id":chat,"type":mode})
            return True
        return False

    def get_autojoin(self,chat):
        curr = self.find_one({"chat_id":chat})
        if not curr:
            return False
        else:
            return curr["type"]

    def update_join_type(self,chat,mode):
        curr = self.find_one({"chat_id":chat})
        if curr:
            self.update({"chat_id":chat},{"type":mode})
            return 
        else:
            return

    def remove_autojoin(self,chat):
        curr = self.find_one({"chat_id":chat})
        if curr:
            self.delete_one({"chat_id":chat})
        return