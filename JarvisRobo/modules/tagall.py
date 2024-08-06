import asyncio
from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from JarvisRobo import telethn as client

spam_chats = {}  # Use a dictionary to track active tagging processes

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

    msg_text = event.pattern_match.group(2).strip() if event.pattern_match.group(2) else None

    if event.is_reply:
        msg = await event.get_reply_message()
        if msg is None:
            return await event.respond("I can't mention members for older messages!")
        if not msg_text:
            msg_text = msg.text

    if not msg_text:
        return await event.respond("Reply to a message or provide some text to mention others!")

    if chat_id in spam_chats and spam_chats[chat_id]['active']:
        return await event.respond("A mention process is already ongoing. Use `/cancel` to stop it.")

    spam_chats[chat_id] = {'active': True, 'msg_id': msg.id if event.is_reply else None}

    usrnum = 0
    usrtxt = ""

    try:
        async for user in client.iter_participants(chat_id):
            if chat_id not in spam_chats or not spam_chats[chat_id]['active']:
                await event.respond("Mention process stopped.")
                return

            usrnum += 1
            usrtxt += f"🦋 [{user.first_name}](tg://user?id={user.id})\n"  # Add a newline after each tag

            if usrnum == 5:  # Batch size is 5
                txt = f"{msg_text}\n\n{usrtxt.strip()}"
                await client.send_message(chat_id, txt)
                usrtxt = ""  # Clear the text after sending
                usrnum = 0
                await asyncio.sleep(2)  # Sleep to avoid spamming

                # Send an empty message to ensure a 2-line space
                await client.send_message(chat_id, "\n\n")

        # Send remaining users if any
        if usrnum > 0 and chat_id in spam_chats and spam_chats[chat_id]['active']:
            txt = f"{msg_text}\n\n{usrtxt.strip()}"
            await client.send_message(chat_id, txt)
    finally:
        if chat_id in spam_chats:
            del spam_chats[chat_id]  # Ensure chat is removed from active processes even if an error occurs

@client.on(events.NewMessage(pattern=r"^/cancel$"))
async def cancel_spam(event):
    chat_id = event.chat_id

    if chat_id not in spam_chats:
        return await event.respond("There is no mention process going on.")

    if not await is_user_admin(chat_id, event.sender_id):
        return await event.respond("Bsdk Pahle Admin Se Permission Le 🤫")

    spam_chats[chat_id]['active'] = False
    return await event.respond("I stop tagging, sir 🫡")

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
