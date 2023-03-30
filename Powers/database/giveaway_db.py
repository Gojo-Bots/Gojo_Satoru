from threading import RLock
from traceback import format_exc

from Powers import LOGGER
from Powers.database import MongoDB
from Powers.utils.msg_types import Types

INSERTION_LOCK = RLock()

class GIVEAWAY(MongoDB):
    """Class to store giveaway info of the chat"""
    db_name = "giveaway"

    def __init__(self):
        super().__init__(self.db_name)
    
    def save_give(
        self,
        chat_id:int, # Chat id for in which user want to do giveaway
        group_id:int, # entries chat id
        user_id: int, # User id of the person who have started the giveaway
        is_new:int=0, # Can old user vote? 0 for yes 1 for no
        entries:int=1, # Entries are allowed? 0 for no 1 for yes
        give:int = 1, # Giveaway is on or not? 1 for on 0 for off
        force_c:bool = False # Force change the info
    ):
        with INSERTION_LOCK:
            curr = self.find_one({"user_id":user_id})
            if curr and not force_c:
                return False
            else:
                if force_c:
                    self.delete_one({"user_id":user_id,})
                    self.insert_one(
                        {
                            "chat_id":chat_id,
                            "where":group_id,
                            "user_id":user_id,
                            "is_new":is_new,
                            "entries":entries,
                            "is_give":give
                        }
                    )
                    return True
    
    def give_info(self,group_id = 0, u_id = 0):
        with INSERTION_LOCK:
            if u_id and group_id:
                curr = self.find_one({"where":group_id, "user_id":u_id})
                if curr:
                    return curr
                else:
                    curr = self.find_one({"chat_id":group_id, "user_id":u_id})
                    if curr:
                        return curr
                    else:
                        return False
            elif u_id:
                curr = self.find_one({"user_id":u_id})
                if curr:
                    return curr
            elif group_id:
                curr = self.find_one({"where":group_id})
                if curr:
                    return curr
                else:
                    curr = self.find_one({"chat_id":group_id})
                    if curr:
                        return curr
                    else:
                        return False
    
    def is_vote(self, group_id):
        with INSERTION_LOCK:
            curr = self.find_one({"where": group_id})
            if curr:
                return True
            return False

    def start_vote(self,user_id, start=1):
        with INSERTION_LOCK:
            curr = self.find_one({"user_id":user_id})
            if curr:
                self.update({"user_id":user_id},{"is_give":start})
                return True
            return False

    def stop_entries(self,user_id,entries=0):
        with INSERTION_LOCK:
            curr = self.find_one({"user_id":user_id})
            if curr:
                self.update({"user_id":user_id},{"entries":entries})
                return True
            return False

    def update_is_old(self,user_id,old):
        with INSERTION_LOCK:
            curr = self.find_one({"user_id":user_id})
            if curr:
                self.update({"user_id":user_id},{"is_new":old})
                return True
            return False

    def stop_give(self, user_id, is_give=0):
        with INSERTION_LOCK:
            curr = self.find_one({"user_id":user_id})
            if curr:
                self.update({"user_id":user_id},{"is_give":is_give})
                return True
            return True