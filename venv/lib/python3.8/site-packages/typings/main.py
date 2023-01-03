import datetime
import logging
import os
import time
from .database import db
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from info import *



async def paid(bot, update):
    user_id = update.from_user.id
    user_name = update.from_user.username
    user_first = update.from_user.first_name
    logger.info(
        f"👉 {update.text} 👈 Sent by User {user_first} {str(user_id)} @{user_name}"
    )
    SUB_BUTTONS = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Pay Now", url=f"https://t.me/{PAID_USERNAME}")],
        ]
    )
    if PAID_BOT.upper() == "YES":
        try:
            paid_status = await db.get_paid_status(user_id)
        except Exception as e:
            await update.reply(f"⚠️ First Click on /start, Then try again\n\nError: {e}")
            return True
        if paid_status["is_paid"]:
            current_date = datetime.datetime.now()
            paid_duration = paid_status["paid_duration"]
            paid_on = paid_status["paid_on"]
            paid_reason = paid_status["paid_reason"]
            integer_paid_duration = int(paid_duration)
            will_expire = paid_on + datetime.timedelta(days=integer_paid_duration)
            if will_expire < current_date:
                try:
                    await db.remove_paid(user_id)
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")
                try:
                    await bot.send_message(
                        update.chat.id,
                        f"👋 Your paid plan has Expired on {will_expire}\n\nIf you want to use the bot, You can do so by Paying.",
                    )
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")
                for i in ADMINS:
                    try:
                        await bot.send_message(
                            i,
                            f"🌟 **Plan Expired:** \n\n**User Id:** `{update.from_user.id}`\n\n**User Name:** @{update.from_user.username}\n\n**Plan Validity:** {paid_duration} Days\n\n**Joined On** : {paid_on}\n\n**Discription** : {paid_reason}",
                        )
                    except Exception:
                        logger.info(f"⚠️ Not found id {i}")
                return True

            else:
                pass

        else:
            await update.reply_text(
                text=f"{PAID_TEXT}",
                reply_markup=SUB_BUTTONS,
                disable_web_page_preview=True,
                quote=True,
            )
            return True

        
        
        
        
        
async def paid_user(c, m):

    if len(m.command) == 1:
        await m.reply_text(
            "Use this command to add a user in paid bot.\n\nUsage:\n\n`/paid_user user_id user_name duration discription` ",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        paid_username = m.command[2]
        paid_duration = int(m.command[3])
        paid_reason = " ".join(m.command[4:])
        paid_log_text = f"**User Id:** {user_id}\n**User Name:** {paid_username} \n**Plan Validity:** {paid_duration} Days"  #
        try:
            await c.send_message(
                user_id,
                f"🙂 Your paid subscription started for **{paid_duration}** Days",
            )
            paid_log_text += "\n\nUser notified successfully ✅"
        except Exception as e:
            log.debug(e, exc_info=True)
            paid_log_text += f"\n\nUser notification failed !!!{e}"
        await db.paid_user(user_id, paid_username, paid_duration, paid_reason)
        log.debug(paid_log_text)
        await m.reply_text(paid_log_text, quote=True)
    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(
            f"Error occoured!! {e}",
            quote=True,
        )

async def all_paid_users(c, m):
    all_paid_users = await db.get_all_paid_users()
    paid_usr_count = 0
    text = ""
    async for paid_user in all_paid_users:
        user_id = paid_user["id"]
        paid_duration = paid_user["paid_status"]["paid_duration"]
        paid_on = paid_user["paid_status"]["paid_on"]
        paid_username = paid_user["paid_status"]["paid_username"]
        paid_reason = paid_user["paid_status"]["paid_reason"]
        paid_usr_count += 1
        text += f"✶ **User Id** : `{user_id}`\n\n✶ **User Name** : `{paid_username}`\n\n➩ **Plan Validity** : `{paid_duration}` Days\n\n➩ **Joined On** : {paid_on} \n\n➩ **Discription** : `{paid_reason}` \n--------------------------------------------------------------\n\n"
    reply_text = f"Total Paid Users : `{paid_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        paid_usrs = io.BytesIO()
        paid_usrs.name = "paid-users.txt"
        paid_usrs.write(reply_text.encode())
        await m.reply_document(paid_usrs, True)
        return
    await m.reply_text(reply_text, True)

async def rm_paid(c, m):
    if len(m.command) == 1:
        await m.reply_text(
            "Use this command to kick plan_expired user.\n\nUsage:\n\n`/plan_expired user_id`\n\n",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        plan_ex_log_text = f"Plan Validity Expired User {user_id}"

        try:
            await c.send_message(
                user_id,
                "👋 Your plan has Expired.\n\nIf you want to use the bot, You can do so by Paying.",
            )
            plan_ex_log_text += "\n\nUser notified successfully ✅"
        except Exception as e:
            log.debug(e, exc_info=True)
            plan_ex_log_text += f"\n\nUser notification failed !! {e}"
        await db.remove_paid(user_id)
        log.debug(plan_ex_log_text)
        await m.reply_text(plan_ex_log_text, quote=True)
    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(
            f"Error occoured! {e}",
            quote=True,
        )
