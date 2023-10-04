from threading import RLock

from Powers import LOGGER
from Powers.database import MongoDB

INSERTION_LOCK = RLock()

class SUPPORTS(MongoDB):
    """
    class to store support users in database
    Dev > sudo > whitelist
    """

    db_name = "supports"
    
    def __init__(self) -> None:
        super().__init__(self.db_name)

    def insert_support_user(self, user_id, support_type):
        curr = self.is_support_user(user_id)
        if not curr:
            with INSERTION_LOCK:
                self.insert_one(
                    {
                        "user_id":user_id,
                        "support_type":support_type
                    }
                )
            return

    def update_support_user_type(self,user,new_type):
        curr = self.is_support_user(user)
        if curr:
            with INSERTION_LOCK:
                self.update(
                    {
                        "user_id":user
                    },
                    {
                        "support_type":new_type
                    }
                )
        return


    def is_support_user(self, user_id):
        curr = self.find_one({"user_id":user_id})
        if curr:
            return True
        return False

    def delete_support_user(self,user):
        curr = self.is_support_user(user)
        if curr:
            with INSERTION_LOCK:
                self.delete_one({"user_id":user})
        return

    def get_particular_support(self,support_type):
        curr = self.find_all({"support_type":support_type})
        if curr:
            return [i['user_id'] for i in curr]
        else:
            return []

    def get_support_type(self,user):
        curr = self.find_one({"user_id":user})
        if curr:
            return curr["support_type"]
        return False