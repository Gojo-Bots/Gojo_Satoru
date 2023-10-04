from Powers import DEV_USERS, OWNER_ID, SUDO_USERS, WHITELIST_USERS
from Powers.database.support_db import SUPPORTS


async def load_support_users():
    support = SUPPORTS()
    for i in DEV_USERS:
        support.insert_support_user(int(i),"dev")
    for i in SUDO_USERS:
        support.insert_support_user(int(i),"sudo")
    for i in WHITELIST_USERS:
        support.insert_support_user(int(i),"whitelist")
    return

def get_support_staff(want = "all"):
    """
    dev, sudo, whitelist, dev_level, sudo_level, all
    """
    support = SUPPORTS()
    devs = support.get_particular_support("dev")
    sudo = support.get_particular_support("sudo")
    whitelist = support.get_particular_support("whitelist")

    if want in ["dev","dev_level"]:
        wanted = devs
    elif want == "sudo":
        wanted = sudo
    elif want == "whitelist":
        wanted = whitelist
    elif want == "sudo_level":
        wanted = sudo + devs
    else:
        wanted = list(set([int(OWNER_ID)] + devs + sudo + whitelist))

    return wanted