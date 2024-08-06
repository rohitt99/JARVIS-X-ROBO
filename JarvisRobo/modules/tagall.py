import asyncio
from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from JarvisRobo import telethn as client

spam_chats = []

async def is_user_admin(chat_id, user_id):
    try:
        participant = await client(GetParticipantRequest(chat_id, user_id))
        if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return True
    except UserNotParticipantError:
        pass
    return False

@client.on(events.NewMessage(pattern=r"^(@tagall|@all|/tagall|@mention) ?(.*)"))
async def mention_all(event):
    chat_id = event.chat_id

    if event.is_private:
        return await event.respond("This command can only be used in groups and channels!")

    if not await is_user_admin(event.chat_id, event.sender_id):
        return await event.respond("Only admins can mention all!")

    msg = event.pattern_match.group(2).strip() if event.pattern_match.group(2) else None

    if event.is_reply:
        msg = await event.get_reply_message()
        if msg is None:
            return await event.respond("I can't mention members for older messages!")

    if not msg:
        return await event.respond("Reply to a message or provide some text to mention others!")

    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ""

    async for user in client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        usrnum += 1
        usrtxt += f"[{user.first_name}](tg://user?id={user.id}), "
        if usrnum == 5:  # Reduce batch size to 5 to avoid message length issues
            txt = f"{msg}\n{usrtxt}" if isinstance(msg, str) else f"{usrtxt}"
            await client.send_message(chat_id, txt)
            await asyncio.sleep(2)  # Reduced sleep time to make it more responsive
            usrnum = 0
            usrtxt = ""

    # Send remaining users if any
    if usrnum > 0 and chat_id in spam_chats:
        txt = f"{msg}\n{usrtxt}" if isinstance(msg, str) else f"{usrtxt}"
        await client.send_message(chat_id, txt)

    spam_chats.remove(chat_id)

@client.on(events.NewMessage(pattern=r"^/cancel$"))
async def cancel_spam(event):
    if event.chat_id not in spam_chats:
        return await event.respond("There is no mention process going on.")

    if not await is_user_admin(event.chat_id, event.sender_id):
        return await event.respond("Only admins can execute this command!")

    spam_chats.remove(event.chat_id)
    return await event.respond("Mention process stopped.")

@client.on(events.NewMessage(pattern=r"^/help tagall$"))
async def help_tagall(event):
    help_message = """
    ──「  Only for Admins 」──

    ❍ /tagall or @all '(reply to a message or add another message) to mention all members in your group, without exception.'
    """
    await event.respond(help_message)

mod_name = "TagAll"
help = """
──「  Only for Admins 」──

❍ /tagall or @all '(reply to a message or add another message) to mention all members in your group, without exception.'
"""
