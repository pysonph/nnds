import sqlite3
import telebot
import time
import random

# သင့်ရဲ့ Bot Token ကို အောက်မှာ ထည့်ပါ
BOT_TOKEN = '8444763470:AAHsqVB4ihrMeVRrxumwW6FEY76lulLvqvc'

# သင့်ရဲ့ Channel Username သို့မဟုတ် ID ကို ထည့်ပါ
CHANNEL_ID = '-1003881399284' 

bot = telebot.TeleBot(BOT_TOKEN)

def luhn_checksum(partial_cc):
    """Luhn Algorithm ဖြင့် နောက်ဆုံး Checksum ဂဏန်းကို တွက်ချက်ခြင်း"""
    s = 0
    for i, d in enumerate(reversed(partial_cc)):
        n = int(d)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        s += n
    return (10 - (s % 10)) % 10

def generate_fake_cc(bin_num):
    bin_num = str(bin_num).strip()
    
    # Amex (34 သို့မဟုတ် 37 ဖြင့်စလျှင်) ဖြစ်မဖြစ် စစ်ဆေးခြင်း
    is_amex = bin_num.startswith(('34', '37'))
    
    # Amex ဆိုလျှင် ၁၅ လုံး၊ ကျန်ကတ်များဆိုလျှင် ၁၆ လုံး သတ်မှတ်ခြင်း
    total_length = 15 if is_amex else 16
    
    # BIN နှင့် နောက်ဆုံး Checksum ဂဏန်း ၁ လုံး အနုတ် ကျန်သော လိုအပ်သည့် ဂဏန်းများကို Random ယူခြင်း
    length_to_generate = total_length - len(bin_num) - 1
    random_digits = ''.join([str(random.randint(0, 9)) for _ in range(length_to_generate)])
    
    # Checksum မပါသေးသော ကတ်နံပါတ်
    partial_cc = f"{bin_num}{random_digits}"
    
    # Luhn Algorithm ဖြင့် မှန်ကန်သော နောက်ဆုံးဂဏန်းကို တွက်ယူ၍ ပေါင်းထည့်ခြင်း
    check_digit = luhn_checksum(partial_cc)
    cc_number = f"{partial_cc}{check_digit}"
    
    # သက်တမ်းကုန်ဆုံးမည့် လ/နှစ်ကို လက်ရှိအချိန်မှ ရှေ့ ၃-၄ နှစ်အတွင်း အဖြစ်နိုင်ဆုံး ဖန်တီးခြင်း
    month = f"{random.randint(1, 12):02d}"
    year = str(random.randint(2026, 2030))
    
    # Amex ဆိုလျှင် CVV ၄ လုံး၊ ကျန်ကတ်များဆိုလျှင် CVV ၃ လုံး ဖန်တီးခြင်း
    if is_amex:
        cvv = f"{random.randint(1000, 9999)}"
    else:
        cvv = f"{random.randint(100, 999):03d}"
        
    return f"{cc_number}|{month}|{year}|{cvv}"

def auto_post_scrape():
    print("🚀 Scrape Format ဖြင့် Channel သို့ စတင် ပို့ဆောင်နေပါပြီ...")
    
    conn = sqlite3.connect('bin_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT bin, brand, type, level, bank, country FROM bins")
    rows = cursor.fetchall()
    
    for row in rows:
        bin_num = row[0]
        brand = row[1]
        card_type = row[2]
        level = row[3] if row[3] else "N/A"
        bank = row[4] if row[4] else "N/A"
        country = row[5] if row[5] else "N/A"
        
        # Scrape Data ဖန်တီးခြင်း
        scrape_data = generate_fake_cc(bin_num)
        
        # Channel သို့ပို့မည့် Message ပုံစံ
        msg = (
            f"🔥 <b>Live Scrape Drop</b>\n\n"
            f"💳 <code>{scrape_data}</code>\n"
            f"🏦 <b>Info:</b> {brand} - {card_type} ({level})\n"
            f"🏛 <b>Bank:</b> {bank}\n"
            f"🌍 <b>Country:</b> {country}"
        )
        
        try:
            bot.send_message(CHANNEL_ID, msg, parse_mode='HTML')
            print(f"✅ ပို့ပြီးပါပြီ: {scrape_data}")
        except Exception as e:
            print(f"❌ Error ဖြစ်နေပါသည်: {e}")
        
        # ၁၀ စက္ကန့် စောင့်ဆိုင်းခြင်း
        time.sleep(10)
        
    conn.close()
    print("🎉 Database ထဲရှိ အချက်အလက်အားလုံးကို ပို့ပြီးသွားပါပြီ။")

if __name__ == '__main__':
    auto_post_scrape()
