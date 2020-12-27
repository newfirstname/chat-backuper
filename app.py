from telethon.sync import TelegramClient, events
from telethon.tl.patched import MessageService
from telethon import errors
from telethon.tl.types import MessageMediaPhoto
import datetime
import asyncio
import time
import sys
import os

######################
userId = None
sourceId = None
destId = None
sleep_time = 0.4
sending = False
######################

client_name = 'user'
bot_name = 'bot'
API_ID = 1945628
API_HASH = '2c96a07930fe107684ab108250886d49'
BOT_TOKEN = '1303551272:AAHwswlCSL2Fx96ceEjXcDat1Jlh5h3yixA'

client = TelegramClient(client_name, API_ID, API_HASH)
bot = TelegramClient(bot_name, API_ID, API_HASH)

client.start()
bot.start(bot_token=BOT_TOKEN)


async def sendAllMessages(first_id, last_id, message_types, dest_id, source_id):
    num = first_id

    while num <= last_id:
        try:
            message = await client.get_messages(source_id, ids=[num])
            if type(message[0]) == MessageService:
                num += 1
                continue
            if not message[0]:
                num += 1
                continue
            message = message[0]
            await sendMessage(dest_id, message)

            num += 1
            time.sleep(sleep_time)
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            break

    print('end')
    await endForward()


async def sendMessage(dest_id, message):
	await client.send_message(dest_id, message)

	print(f'sent message {message.id}')


async def sendOnePair(source_id, dest_id, year, month, day, message_types):
    if year == 0:
        msgs = await client.get_messages(source_id)

        last_message_id = msgs[0].id
        await sendAllMessages(1, last_message_id, message_types, dest_id, source_id)
    else:
        date = datetime.datetime(year, month, day)
        allMessages = client.get_messages(source_id)
        last_message_id = allMessages[0].id

        messagesOfDate = client.get_messages(source_id, offset_date=date)
        first_message_id = messagesOfDate[0].id + 1

        sendAllMessages(first_message_id, last_message_id,
                        message_types, dest_id, source_id)


@bot.on(events.NewMessage)
async def bnmh(event):
	global userId
	global sourceId
	global destId

	if event.raw_text.startswith('/setsource'):
		splittedMessage = event.raw_text.split(' ')

		if len(splittedMessage) != 2:
			await event.respond('please use thos format to set the id of the source channel:\nsend the /setsource command to this bot followed by the id of the source, Example:')
			await event.respond('/setsource @source_id')
			return

		sourceId = splittedMessage[1]
		await event.respond(f'source id set to {sourceId}')
	elif event.raw_text.startswith('/setdest'):
		splittedMessage = event.raw_text.split(' ')

		if len(splittedMessage) != 2:
			await event.respond('please use thos format to set the id of the destination channel:\nsend the /setdest command to this bot followed by the id of the destination, Example:')
			await event.respond('/setdest @destination_id')
			return

		destId = splittedMessage[1]
		await event.respond(f'destination id set to {destId}')
	elif event.raw_text.startswith('/startforward'):
		if not sending:
			if not sourceId or not destId:
				await event.respond('please set both source and destination')
				return
			userId = event.message.peer_id.user_id
			await startForward()
		else:
			await event.respond('some other operation is in progress, please wait')
	elif event.raw_text.startswith('/check'):
		if sending == True:
			await event.respond('still sending')
		else:
			await event.respond('no forward in progress')
		if sourceId:
			await event.respond(f'source: {sourceId}')
		else:
			await event.respond('source: None')
		if destId:
			await event.respond(f'destination: {destId}')
		else:
			await event.respond('destination: None')
	elif event.raw_text.startswith('/help'):
		await event.respond('Hello')
		await event.respond('in order to backup a channels data, you have to follow these steps:')
		await event.respond('1. set the id of the source channel:\nsend the /setsource command to this bot followed by the id of the source, Example:')
		await event.respond('/setsource @source_id')
		await event.respond('2. set the id of the destination channel:\nsend the /setdest command to this bot followed by the id of the destination, Example:')
		await event.respond('/setdest @dest_id')
		await event.respond('3. send the start forward command:\nsend the /startforward command to this bot, Example:')
		await event.respond('/setdest')
		await event.respond('4. you can check if the forward is complete:\nsend the /check command to this bot, Example:')
		await event.respond('/check')

async def startForward():
	global sending

	sending = True
	await sendOnePair(sourceId, destId, 0, 0, 0, [])


async def endForward():
	global sending
	global userId

	await bot.send_message(userId, 'forward complete')
	sending = False

bot.run_until_disconnected()
