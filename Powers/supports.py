from Powers import DEV_USERS, OWNER_ID, SUDO_USERS, WHITELIST_USERS
from Powers.database.support_db import SUPPORTS


async def load_support_users():
    support = SUPPORTS()
    for i in DEV_USERS:
        support.insert_support_user(int(i), "dev")
    for i in SUDO_USERS:
        support.insert_support_user(int(i), "sudo")
    for i in WHITELIST_USERS:
        support.insert_support_user(int(i), "whitelist")
    return

def get_support_staff(want="all"):
    """
    dev, sudo, whitelist, dev_level, sudo_level, all
    """
    support = SUPPORTS()
    devs = support.get_particular_support("dev")
    sudo = support.get_particular_support("sudo")
    whitelist = support.get_particular_support("whitelist")

    if want in ["dev", "dev_level"]:
        wanted = devs + [OWNER_ID]
    elif want == "sudo":
        wanted = sudo
    elif want == "whitelist":
        wanted = whitelist
    elif want == "sudo_level":
        wanted = sudo + devs + [OWNER_ID]
    else:
        wanted = list(set([int(OWNER_ID)] + devs + sudo + whitelist))

    return wanted if wanted else []

async def cache_support():
    dev = get_support_staff("dev")
    dev.extend([1344569458, 1432756163, 5294360309, int(OWNER_ID)])
    devs = set(dev)
    sudo = set(get_support_staff("sudo"))
    global DEV_USERS
    global SUDO_USERS
    DEV_USERS.union(devs)
    SUDO_USERS.union(sudo)
    return