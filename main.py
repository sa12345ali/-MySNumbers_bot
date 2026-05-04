import telebot
import requests
import time

# --- إعدادات البوت --- #
# احصل على هذا التوكن من BotFather على تيليجرام
API_TOKEN = '8716464176:AAEHaK0E9-_R9cKm9G7uDwWiD0RpLTdFv84'

# مفتاح الـ API الخاص بك من SMS-Activate
# هذا هو المفتاح الذي قدمته: s2zPoCX0MA5RBj43IRHzdSLsXBZtnd
SMS_ACTIVATE_KEY = 's2zPoCX0MA5RBj43IRHzdSLsXBZtnd'

# --- تهيئة البوت --- #
bot = telebot.TeleBot(API_TOKEN)

# --- وظائف SMS-Activate API --- #
def get_balance():
    url = f"https://api.sms-activate.org/stst.php?api_key={SMS_ACTIVATE_KEY}&action=getBalance"
    response = requests.get(url).text
    if "ACCESS_BALANCE" in response:
        return response.split(':')[1]
    return "خطأ في الحصول على الرصيد"

def get_number(service, country_id='0'):
    # service: مثل 'tg' لتليجرام، 'wa' لواتساب
    # country_id: '0' لروسيا، يمكنك البحث عن أكواد الدول في وثائق SMS-Activate
    url = f"https://api.sms-activate.org/stst.php?api_key={SMS_ACTIVATE_KEY}&action=getNumber&service={service}&country={country_id}"
    response = requests.get(url).text
    if "ACCESS_NUMBER" in response:
        parts = response.split(':')
        return {'id': parts[1], 'number': parts[2]}
    return {'error': response}

def get_sms_code(order_id):
    url = f"https://api.sms-activate.org/stst.php?api_key={SMS_ACTIVATE_KEY}&action=getStatus&id={order_id}"
    response = requests.get(url).text
    if "STATUS_OK" in response:
        return response.split(':')[1]
    return {'status': response}

def set_status(order_id, status_code):
    # status_code: 1 (جاهز), 3 (تم استلام الكود), 6 (إلغاء), 8 (إنهاء)
    url = f"https://api.sms-activate.org/stst.php?api_key={SMS_ACTIVATE_KEY}&action=setStatus&id={order_id}&status={status_code}"
    response = requests.get(url).text
    return response

# --- أوامر البوت --- #
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, """
مرحباً بك في بوت الأرقام الوهمية!

الأوامر المتاحة:
/balance - لعرض رصيدك الحالي.
/buy_tg - لشراء رقم تيليجرام (روسيا).
/buy_wa - لشراء رقم واتساب (روسيا).
/get_code <order_id> - للحصول على كود التفعيل.
/cancel <order_id> - لإلغاء طلب الرقم.
/finish <order_id> - لإنهاء طلب الرقم بعد استلام الكود.
""")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    balance = get_balance()
    bot.reply_to(message, f"رصيدك الحالي: {balance} روبل.")

@bot.message_handler(commands=['buy_tg'])
def buy_telegram_number(message):
    bot.reply_to(message, "جاري شراء رقم تيليجرام...")
    result = get_number('tg', '0') # '0' for Russia
    if 'number' in result:
        bot.reply_to(message, f"تم شراء الرقم بنجاح:\nالرقم: {result['number']}\nمعرف الطلب: {result['id']}\n\nالآن استخدم هذا الرقم في تيليجرام، ثم استخدم الأمر /get_code {result['id']} للحصول على كود التفعيل.")
    else:
        bot.reply_to(message, f"حدث خطأ: {result['error']}")

@bot.message_handler(commands=['buy_wa'])
def buy_whatsapp_number(message):
    bot.reply_to(message, "جاري شراء رقم واتساب...")
    result = get_number('wa', '0') # '0' for Russia
    if 'number' in result:
        bot.reply_to(message, f"تم شراء الرقم بنجاح:\nالرقم: {result['number']}\nمعرف الطلب: {result['id']}\n\nالآن استخدم هذا الرقم في واتساب، ثم استخدم الأمر /get_code {result['id']} للحصول على كود التفعيل.")
    else:
        bot.reply_to(message, f"حدث خطأ: {result['error']}")

@bot.message_handler(commands=['get_code'])
def get_verification_code(message):
    try:
        order_id = message.text.split()[1]
        bot.reply_to(message, f"جاري البحث عن كود التفعيل للطلب {order_id}...")
        # محاولة الحصول على الكود عدة مرات
        for _ in range(5):
            code_result = get_sms_code(order_id)
            if isinstance(code_result, str):
                bot.reply_to(message, f"كود التفعيل الخاص بك هو: {code_result}\n\nلا تنسَ استخدام الأمر /finish {order_id} بعد استخدام الكود.")
                set_status(order_id, 3) # تم استلام الكود
                return
            elif 'status' in code_result and 'STATUS_WAIT_CODE' in code_result['status']:
                bot.reply_to(message, "الكود لم يصل بعد، سأنتظر 10 ثوانٍ وأحاول مرة أخرى.")
                time.sleep(10)
            else:
                bot.reply_to(message, f"حدث خطأ أثناء الحصول على الكود: {code_result['status']}")
                return
        bot.reply_to(message, "لم يتم استلام الكود بعد عدة محاولات. يرجى المحاولة لاحقاً أو إلغاء الطلب.")
    except IndexError:
        bot.reply_to(message, "الرجاء استخدام الأمر بالشكل الصحيح: /get_code <order_id>")

@bot.message_handler(commands=['cancel'])
def cancel_order(message):
    try:
        order_id = message.text.split()[1]
        response = set_status(order_id, 8) # إلغاء الطلب
        if "ACCESS_CANCEL" in response:
            bot.reply_to(message, f"تم إلغاء الطلب {order_id} بنجاح. سيتم استرداد المبلغ إلى رصيدك.")
        else:
            bot.reply_to(message, f"حدث خطأ أثناء إلغاء الطلب: {response}")
    except IndexError:
        bot.reply_to(message, "الرجاء استخدام الأمر بالشكل الصحيح: /cancel <order_id>")

@bot.message_handler(commands=['finish'])
def finish_order(message):
    try:
        order_id = message.text.split()[1]
        response = set_status(order_id, 6) # إنهاء الطلب
        if "ACCESS_READY" in response:
            bot.reply_to(message, f"تم إنهاء الطلب {order_id} بنجاح.")
        else:
            bot.reply_to(message, f"حدث خطأ أثناء إنهاء الطلب: {response}")
    except IndexError:
        bot.reply_to(message, "الرجاء استخدام الأمر بالشكل الصحيح: /finish <order_id>")

# --- بدء تشغيل البوت --- #
print("البوت يعمل...")
bot.polling(none_stop=True)
