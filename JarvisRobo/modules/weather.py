import io
import aiohttp
from telethon.tl import functions, types
from JarvisRobo import telethn as tbot
from JarvisRobo.events import register


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@register(pattern="^/weather (.*)")
async def _(event):
    if event.fwd_from:
        return

    sample_url = "https://wttr.in/{}.png"
    input_str = event.pattern_match.group(1)
    
    async with aiohttp.ClientSession() as session:
        try:
            response_api_zero = await session.get(sample_url.format(input_str))
            response_api_zero.raise_for_status()
            response_api = await response_api_zero.read()
            with io.BytesIO(response_api) as out_file:
                await event.reply(file=out_file)
        except aiohttp.ClientError as e:
            await event.reply(f"An error occurred: {e}")

__help__ = """
I can find the weather for any city.

 ❍ /weather <city>*:* Advanced weather module, usage same as /weather
 ❍ /weather moon*:* Get the current status of the moon
"""

__mod_name__ = "Weather"
