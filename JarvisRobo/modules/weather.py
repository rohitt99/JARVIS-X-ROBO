import aiohttp
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

    sample_url = "https://wttr.in/{}?format=%C+%t+%f+%h+%w+%m"
    input_str = event.pattern_match.group(1)
    
    async with aiohttp.ClientSession() as session:
        try:
            response_api_zero = await session.get(sample_url.format(input_str))
            response_api_zero.raise_for_status()
            response_api = await response_api_zero.text()
            
            # Extracting data from the response
            data_parts = response_api.split()
            condition = data_parts[0]
            temperature = data_parts[1]
            feels_like = data_parts[2]
            humidity = data_parts[3]
            wind_speed = data_parts[4]
            location = input_str

            # Formatting the message
            weather_report = (
                f"{location}:\n\n"
                f"ᴛᴇᴍᴘᴇʀᴀᴛᴜʀᴇ: {temperature}\n"
                f"ᴛᴇᴍᴘᴇʀᴀᴛᴜʀᴇ ғᴇᴇʟs ʟɪᴋᴇ: {feels_like}\n"
                f"ᴀɪʀ ʜᴜᴍɪᴅɪᴛʏ: {humidity}\n"
                f"ᴡɪɴᴅ sᴘᴇᴇᴅ: {wind_speed}\n"
                f"- {condition}"
            )

            await event.reply(weather_report)
        except aiohttp.ClientError as e:
            await event.reply(f"An error occurred: {e}")

__help__ = """
I can find the weather for any city.

 ❍ /weather <city>*:* Advanced weather module, usage same as /weather
 ❍ /weather moon*:* Get the current status of the moon
"""

__mod_name__ = "Weather"
