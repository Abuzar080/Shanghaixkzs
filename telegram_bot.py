import os
import requests
import zipfile
import telebot
from bs4 import BeautifulSoup
from telebot import types

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token
API_TOKEN = '8040452579:AAG_U-s1h5MrDQ2ZtXBvRc7A2vQbLqYd3Nw'
bot = telebot.TeleBot(API_TOKEN)

# Channel username (replace with your actual channel username)
CHANNEL_USERNAME = '@AzR_projects'
CHANNELL_USERNAME = 'AzR_projects'

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNELL_USERNAME}")
    markup.add(button)
    
    photo_url = "https://t.me/botposters/25"
    caption = "𝗛𝗶 𝘄𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗼𝘂𝗿 𝗫 𝘄𝗲𝗯𝘀𝗶𝘁𝗲 𝗰𝗹𝗼𝗻𝗲𝗿\n\n𝗦𝗲𝗻𝗱 𝗺𝗲 𝗮𝗻𝘆 𝗹𝗶𝗻𝗸 𝗜 𝘄𝗶𝗹𝗹 𝗴𝗶𝘃𝗲 𝘀𝗼𝘂𝗿𝗰𝗲 𝗳𝗶𝗹𝗲\n\n𝗠𝗮𝗱𝗲 𝗯𝘆 @AzR080"
    
    bot.send_photo(message.chat.id, photo_url, caption=caption, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def fetch_source_code(message):
    chat_id = message.chat.id
    
    # Check if user is subscribed to the channel
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, chat_id)
        if member.status not in ['member', 'administrator', 'creator']:
            bot.reply_to(message, f"Please join our channel @{CHANNEL_USERNAME} to use this bot.")
            return
    except Exception as e:
        bot.reply_to(message, f"Error checking channel subscription: {e}")
        return
    
    bot.reply_to(message, "Processing... This may take a few moments.") #Processing message

    url = message.text.strip()
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Create a directory to store files
        os.makedirs('website_files', exist_ok=True)

        # Save the HTML file
        with open('website_files/index.html', 'w', encoding='utf-8') as html_file:
            html_file.write(soup.prettify())

        # Find and download CSS and JS files
        for link in soup.find_all('link'):
            href = link.get('href')
            if href and href.endswith('.css'):
                href = requests.compat.urljoin(url, href) if not href.startswith('http') else href
                css_response = requests.get(href)
                css_response.raise_for_status()
                css_file_name = os.path.join('website_files', os.path.basename(href))
                with open(css_file_name, 'wb') as css_file:
                    css_file.write(css_response.content)

        for script in soup.find_all('script'):
            src = script.get('src')
            if src and src.endswith('.js'):
                src = requests.compat.urljoin(url, src) if not src.startswith('http') else src
                js_response = requests.get(src)
                js_response.raise_for_status()
                js_file_name = os.path.join('website_files', os.path.basename(src))
                with open(js_file_name, 'wb') as js_file:
                    js_file.write(js_response.content)

        # Create a ZIP file
        zip_file_name = 'website_files.zip'
        with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
            for foldername, subfolders, filenames in os.walk('website_files'):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    zip_file.write(file_path, os.path.relpath(file_path, 'website_files'))

        # Send the ZIP file to the user
        with open(zip_file_name, 'rb') as zip_file:
            bot.send_document(message.chat.id, zip_file)

        # Clean up
        os.remove(zip_file_name)
        for root, _, files in os.walk('website_files'):
            for file in files:
                os.remove(os.path.join(root,file))
        os.rmdir('website_files')

    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Error fetching the URL: {e}")
    except Exception as e:
        bot.reply_to(message, f"An unexpected error occurred: {e}")


# Start polling
bot.polling()
                
