from threading import RLock

from Powers import LOGGER
from Powers.database import MongoDB

INSERTION_LOCK = RLock()

lock_t = ["bot", "anti_c_send", "anti_fwd",
          "anti_fwd_u", "anti_fwd_c", "anti_links"]


class LOCKS(MongoDB):
    """Class to store locks"""

    db_name = "locks"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def insert_lock_channel(self, chat: int, locktype: str):
        """
        locktypes: all, bot, anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        if locktype == "all":
            for i in lock_t:
                curr = self.find_one({"chat_id": chat, "locktype": i})
                if curr:
                    continue
                if i in ["anti_fwd_u", "anti_fwd_c"]:
                    continue
                self.insert_one({"chat_id": chat, "locktype": i})
            return True
        curr = self.find_one({"chat_id": chat, "locktype": locktype})
        if curr:
            return False
        else:
            with INSERTION_LOCK:
                hmm = self.merge_u_and_c(chat, locktype)
                if not hmm:
                    self.insert_one({"chat_id": chat, "locktype": locktype})
            return True

    def remove_lock_channel(self, chat: int, locktype: str):
        """
        locktypes: all, bot, anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        if locktype == "all":
            for i in lock_t:
                curr = self.find_one({"chat_id": chat, "locktype": i})
                if curr:
                    self.delete_one({"chat_id": chat, "locktype": i})
            return True
        curr = self.find_one({"chat_id": chat, "locktype": locktype})
        if curr:
            with INSERTION_LOCK:
                self.delete_one({"chat_id": chat, "locktype": locktype})
            return True
        else:
            return False

    def get_lock_channel(self, locktype: str = "all", chat: int = 0):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links, bot
        """
        if locktype not in ["anti_c_send", "anti_fwd", "anti_fwd_u", "anti_fwd_c", "anti_links", "bot", "all"]:
            return False
        else:
            if locktype == "all":
                find = {}
            else:
                find = {"locktype": locktype}
            if chat:
                if find:
                    curr = self.find_one(
                        {"chat_id": chat, "locktype": locktype})
                    return bool(curr)
                else:
                    to_return = []
                    for i in lock_t:
                        curr = self.find_one({"chat_id": chat, "locktype": i})
                        to_return.append(bool(curr))
                    return all(to_return)
            else:
                curr = self.find_all(find)
                if not curr:
                    list_ = []
                else:
                    list_ = [i["chat_id"] for i in curr]
                return list_

    def merge_u_and_c(self, chat: int, locktype: str):
        if locktype == "anti_fwd_u":
            curr = self.find_one({"chat_id": chat, "locktype": "anti_fwd_c"})
        elif locktype == "anti_fwd_c":
            curr = self.find_one({"chat_id": chat, "locktype": "anti_fwd_u"})
        else:
            return False

        if curr:
            self.delete_one({"chat_id": chat, "locktype": locktype})
            self.insert_one({"chat_id": chat, "locktype": "anti_fwd"})
            return True
        else:
            return False

    def is_particular_lock(self, chat: int, locktype: str):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        curr = self.find_one({"chat_id": chat, "locktype": locktype})
        if curr:
            return True
        else:
            return False
