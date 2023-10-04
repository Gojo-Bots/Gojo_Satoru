from threading import RLock

from Powers import LOGGER
from Powers.database import MongoDB

INSERTION_LOCK = RLock()


class CAPTCHA(MongoDB):
    """Class to store captcha's info"""
    db_name = "captcha"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def insert_captcha(self, chat, captcha_type:str="qr", captcha_action:str = "mute"):
        with INSERTION_LOCK:
            curr = self.is_captcha(chat)
            if not curr:
                self.insert_one(
                    {
                        "chat_id":chat,
                        "captcha_type":captcha_type,
                        "captcha_action":captcha_action
                    }
                )
            return

    def is_captcha(self, chat):
        curr = self.find_one({"chat_id": chat})
        if curr:
            return True
        return False

    def update_type(self, chat, captcha_type):
        with INSERTION_LOCK:
            curr = self.is_captcha(chat)
            if curr:
                self.update({"chat_id":chat},{"captcha_type":captcha_type})
            return

    def update_action(self, chat, captcha_action):
        with INSERTION_LOCK:
            curr = self.is_captcha(chat)
            if curr:
                self.update({"chat_id":chat},{"captcha_action":captcha_action})
            return
    
    def remove_captcha(self, chat):
        with INSERTION_LOCK:
            curr = self.is_captcha(chat)
            if curr:
                self.delete_one({"chat_id":chat})
            return

    def get_captcha(self, chat):
        curr = self.find_one({"chat_id":chat})
        if curr:
            return curr
        return False

class CAPTCHA_DATA(MongoDB):
    """class to store captcha data"""
    db_name = "captcha_data"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def load_cap_data(self, chat, user, data):
        curr = self.find_one({"chat_id":chat,"user_id":user})
        if not curr:
            with INSERTION_LOCK:
                self.insert_one({"chat_id":chat,"user_id":user,"data":data})
            return True
        else:
            return

    def get_cap_data(self, chat, user):
        curr = self.find_one({"chat_id":chat,"user_id":user})
        if curr:
            return curr["data"]
        else:
            return False

    def remove_cap_data(self, chat, user):
        curr = self.find_one({"chat_id":chat,"user_id":user})
        if curr:
            with INSERTION_LOCK:
                self.delete_one({"chat_id":chat,"user_id":user})
        return

    def store_message_id(self, chat, user, message):
        curr = self.find_one({"chat_id":chat,"user_id":user})
        if not curr:
            with INSERTION_LOCK:
                self.insert_one({"chat_id":chat,"user_id":user,"message_id":message})
                return
        else:
            return 
    
    def is_already_data(self, chat, user):
        curr = self.find_one({"chat_id":chat,"user_id":user})
        if curr:
            return curr["message_id"]
        else:
            return False

    def del_message_id(self, chat, user):
        curr = self.find_one({"chat_id":chat,"user_id":user})
        if curr:
            with INSERTION_LOCK:
                self.delete_one({"chat_id":chat,"user_id":user})
        return