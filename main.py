import requests
import telebot, time
from telebot import types
from gatet import Tele
import os

token = '9176000373:AAFv7YZeoCuw2QrHIS3S7KliYBc-tD9W7EE'
bot = telebot.TeleBot(token, parse_mode="HTML")

# ==================== BIN LOOKUP (ပြင်ပြီး) ====================
def get_bin_info(card_number):
    """BIN info — binlist.net အဓိက၊ antipublic ကို timeout 5s ပဲ စမ်း"""
    bin6 = card_number[:6]
    brand = 'Unknown'
    card_type = 'Unknown'
    country = 'Unknown'
    country_flag = 'Unknown'
    bank = 'Unknown'

    # ---- ၁။ binlist.net (အဓိက) ----
    try:
        r = requests.get(f'https://lookup.binlist.net/{bin6}',
                         headers={'Accept-Version': '3'},
                         timeout=8)
        if r.status_code == 200:
            d = r.json()
            brand = (d.get('brand') or 'Unknown').upper()
            card_type = (d.get('type') or 'Unknown').capitalize()
            c = d.get('country') or {}
            country = c.get('name') or 'Unknown'
            country_flag = c.get('emoji') or 'Unknown'
            b = d.get('bank') or {}
            bank = b.get('name') or 'Unknown'
            if brand != 'Unknown' or bank != 'Unknown':
                return brand, card_type, country, country_flag, bank
    except Exception as e:
        print(f"[binlist] {e}")

    # ---- ၂။ antipublic (fallback — timeout 5s၊ fail ရင် ကျော်) ----
    try:
        r = requests.get(f'https://bins.antipublic.cc/bins/{bin6}',
                         timeout=5,
                         headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            d = r.json()
            brand = d.get('brand') or brand
            card_type = d.get('type') or card_type
            country = d.get('country_name') or country
            country_flag = d.get('country_flag') or country_flag
            bank = d.get('bank') or bank
    except Exception as e:
        print(f"[antipublic] skip: {e}")

    return brand, card_type, country, country_flag, bank


# ==================== BOT ====================
@bot.message_handler(commands=["start"])
def start(message):
    if not str(message.chat.id) == '7413757844':
        bot.reply_to(message, "You cannot use the bot to contact developers to purchase a bot subscription @strawhatchannel96")
        return
    bot.reply_to(message, "Send the file now")


@bot.message_handler(content_types=["document"])
def main(message):
    if not str(message.chat.id) == '7413757844':
        bot.reply_to(message, "You cannot use the bot to contact developers to purchase a bot subscription @strawhatchannel96")
        return

    dd = 0
    live = 0
    ch = 0
    ccn = 0
    cvv = 0
    lowfund = 0
    ko = (bot.reply_to(message, "CHECKING....⌛").message_id)

    ee = bot.download_file(bot.get_file(message.document.file_id).file_path)
    with open("combo.txt", "wb") as w:
        w.write(ee)

    try:
        with open("combo.txt", 'r') as file:
            lino = file.readlines()
            total = len(lino)

            for cc in lino:
                cc = cc.strip()
                if not cc:
                    continue

                # STOP စစ်
                current_dir = os.getcwd()
                for filename in os.listdir(current_dir):
                    if filename.endswith(".stop"):
                        bot.edit_message_text(chat_id=message.chat.id, message_id=ko,
                                              text='STOP ✅\nBOT BY ➜ @strawhatchannel96')
                        os.remove('stop.stop')
                        return

                # ★ BIN lookup ★
                brand, card_type, country, country_flag, bank = get_bin_info(cc)

                start_time = time.time()
                try:
                    last = str(Tele(cc))
                except Exception as e:
                    print(e)
                    last = 'missing payment form'
                execution_time = time.time() - start_time

                # inline keyboard
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                status = types.InlineKeyboardButton(f"• STATUS ➜ {last[:60]} •", callback_data='u8')
                cm3 = types.InlineKeyboardButton(f"• CHARGED ➜ [ {ch} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"• CCN ➜ [ {ccn} ] •", callback_data='x')
                cm5 = types.InlineKeyboardButton(f"• CVV ➜ [ {cvv} ] •", callback_data='x')
                cm6 = types.InlineKeyboardButton(f"• LOW FUNDS ➜ [ {lowfund} ] •", callback_data='x')
                cm7 = types.InlineKeyboardButton(f"• DECLINED ➜ [ {dd} ] •", callback_data='x')
                cm8 = types.InlineKeyboardButton(f"• TOTAL ➜ [ {total} ] •", callback_data='x')
                stop = types.InlineKeyboardButton(f"[ STOP ]", callback_data='stop')
                mes.add(cm1, status, cm3, cm4, cm5, cm6, cm7, cm8, stop)

                bot.edit_message_text(chat_id=message.chat.id, message_id=ko,
                                      text='Wait For Processing\nby ➜ @strawhatchannel96',
                                      reply_markup=mes)

                print(last)
                low = last.lower()

                # ---- CHARGED ----
                if 'Thank you for your donation!' in last:
                    ch += 1
                    msg = f''' 
𝐂𝐀𝐑𝐃: <code>{cc}</code>
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>Hit $1 🔥</code>

𝐁𝐢𝐧 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
𝐁𝐚𝐧𝐤: <code>{bank}</code>
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>

𝐓𝐢𝐦𝐞: <code>{execution_time:.1f} second</code> 
𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: @strawhatchannel96'''
                    bot.reply_to(message, msg)

                # ---- CVV ----
                elif 'Your card does not support this type of purchase' in last:
                    cvv += 1
                    msg = f''' 
𝐂𝐀𝐑𝐃: <code>{cc}</code>
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>Card not supported ⚠️</code>

𝐁𝐢𝐧 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
𝐁𝐚𝐧𝐤: <code>{bank}</code>
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>

𝐓𝐢𝐦𝐞: <code>{execution_time:.1f} second</code> 
𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: @strawhatchannel96'''
                    bot.reply_to(message, msg)

                # ---- CCN ----
                elif 'security code is incorrect' in last or 'security code is invalid' in last:
                    ccn += 1
                    msg = f''' 
𝐂𝐀𝐑𝐃: <code>{cc}</code>
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>CCN incorrect ❌</code>

𝐁𝐢𝐧 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
𝐁𝐚𝐧𝐤: <code>{bank}</code>
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>

𝐓𝐢𝐦𝐞: <code>{execution_time:.1f} second</code> 
𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: @strawhatchannel96'''
                    bot.reply_to(message, msg)

                # ---- LOW FUNDS ----
                elif 'insufficient funds' in low:
                    lowfund += 1
                    msg = f''' 
𝐂𝐀𝐑𝐃: <code>{cc}</code>
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>Insufficient funds 🔥</code>

𝐁𝐢𝐧 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
𝐁𝐚𝐧𝐤: <code>{bank}</code>
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>

𝐓𝐢𝐦𝐞: <code>{execution_time:.1f} second</code> 
𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: @strawhatchannel96'''
                    bot.reply_to(message, msg)

                # ---- 3DS ----
                elif 'The payment needs additional action before completion!' in last:
                    cvv += 1
                    msg = f''' 
𝐂𝐀𝐑𝐃: <code>{cc}</code>
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>3ds ✅</code>

𝐁𝐢𝐧 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
𝐁𝐚𝐧𝐤: <code>{bank}</code>
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>

𝐓𝐢𝐦𝐞: <code>{execution_time:.1f} second</code> 
𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: @strawhatchannel96'''
                    bot.reply_to(message, msg)

                # ---- အခြား (declined) ----
                else:
                    dd += 1

                # ★★ ကဒ်တစ်ခုစီကြား ၁၃ စက္ကန့် စောင့် (branch အားလုံးအတွက်) ★★
                time.sleep(13)

    except Exception as e:
        print(e)

    bot.edit_message_text(chat_id=message.chat.id, message_id=ko,
                          text='CHECKED ✅\nBOT BY ➜ @strawhatchannel96')


@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def menu_callback(call):
    with open("stop.stop", "w") as file:
        pass


bot.polling()