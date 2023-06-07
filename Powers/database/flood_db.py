from threading import RLock
from traceback import format_exc

from Powers import LOGGER
from Powers.database import MongoDB
from Powers.utils.msg_types import Types

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
            curr = self.find_one({"chat_id": chat_id})
            if curr:
                if not(limit == int(curr['limit']) and within == int(curr['within']) and action == str(curr['action'])):
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
            else:
                return self.insert_one(
                    {
                        "chat_id" : chat_id,
                        "limit": limit,
                        "within": within,
                        "action" : action
                    },
                )
    
    def is_chat(self, chat_id: int):
        with INSERTION_LOCK:
            curr = self.find_one({"chat_id": chat_id})
            if curr:
                action = [str(curr['limit']), str(curr['within']), str(curr['action'])]
                return action
            return False
    
    def get_action(self, chat_id: int):
        with INSERTION_LOCK:
            curr = self.find_one({"chat_id": chat_id})
            if curr:
                return curr['action']
            return "Flood haven't set"
    
    def rm_flood(self, chat_id: int):
        with INSERTION_LOCK:
            curr = self.find_one({"chat_id": chat_id})
            if curr:
                self.delete_one({"chat_id":chat_id})
                return True
            return False
            