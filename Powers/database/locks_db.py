from threading import RLock

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
        if curr := self.find_one({"chat_id": chat, "locktype": locktype}):
            return False
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
                if curr := self.find_one({"chat_id": chat, "locktype": i}):
                    self.delete_one({"chat_id": chat, "locktype": i})
            return True
        if curr := self.find_one({"chat_id": chat, "locktype": locktype}):
            with INSERTION_LOCK:
                self.delete_one({"chat_id": chat, "locktype": locktype})
            return True
        else:
            return False

    def get_lock_channel(self, chat: int, locktype: str = "all"):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links, bot
        """
        if locktype not in [
            "anti_c_send",
            "anti_fwd",
            "anti_fwd_u",
            "anti_fwd_c",
            "anti_links",
            "bot",
            "all",
        ]:
            return False
        if locktype != "all":
            curr = self.find_one(
                {"chat_id": chat, "locktype": locktype})
            return bool(curr)
        else:
            if not (curr := self.find_all({"chat_id": chat})):
                return None
            to_return = {
                "anti_channel": False,
                "anti_fwd": {
                    "user": False,
                    "chat": False
                },
                "anti_links": False,
                "bot": False
            }
            for i in list(curr):
                if i["locktype"] == "anti_c_send":
                    to_return["anti_channel"] = True
                elif i["locktype"] == "anti_fwd":
                    to_return["anti_fwd"]["user"] = to_return["anti_fwd"]["chat"] = True
                elif i["locktype"] == "anti_fwd_u":
                    to_return["anti_fwd"]["user"] = True
                elif i["locktype"] == "anti_fwd_c":
                    to_return["anti_fwd"]["chat"] = True
                elif i["locktype"] == "anti_links":
                    to_return["anti_links"] = True
                elif i["locktype"] == "bot":
                    to_return["bot"] = True
                else:
                    continue
            return to_return

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
        return bool(curr := self.find_one({"chat_id": chat, "locktype": locktype}))
