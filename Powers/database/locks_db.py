from threading import RLock

from Powers import LOGGER
from Powers.database import MongoDB

INSERTION_LOCK = RLock()

class LOCKS(MongoDB):
    """Class to store locks"""
    
    db_name = "locks"

    def __init__(self) -> None:
        super().__init__(self.db_name)