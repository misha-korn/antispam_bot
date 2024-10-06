import aiosqlite


async def create_bd():
    conn = await aiosqlite.connect("antispam_bd.db")
    await conn.execute("""CREATE TABLE IF NOT EXISTS ban_users(
                       id integer PRIMARY KEY
                       )""")
    await conn.execute("""CREATE TABLE IF NOT EXISTS penalty_users(
                       id integer PRIMARY KEY,
                       count integer
                       )""")
    await conn.commit()
    await conn.close()


async def add_user(id_tg):
    conn = await aiosqlite.connect("antispam_bd.db")
    if not await is_ban_new_member(id_tg):
        await conn.execute(f"INSERT INTO ban_users values({id_tg})")
        await conn.commit()
    await conn.close()


async def add_penalty(id_tg):
    conn = await aiosqlite.connect("antispam_bd.db")
    user = await conn.execute(f"SELECT id, count FROM penalty_users WHERE id = {id_tg}")
    user = await user.fetchone()
    if user:
        await conn.execute(
            f"UPDATE penalty_users SET count = {user[1] + 1} WHERE id = {id_tg}"
        )
        await conn.commit()
        await conn.close()
        return user[1]
    else:
        await conn.execute(f"INSERT INTO penalty_users values({id_tg}, 1)")
        await conn.commit()
        await conn.close()
        return 0


async def is_ban_new_member(id_tg):
    conn = await aiosqlite.connect("antispam_bd.db")
    users = await conn.execute(f"SELECT id from ban_users WHERE id = {id_tg}")
    users = await users.fetchone()
    await conn.close()
    if users:
        return True
    else:
        return False
