import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pydub import AudioSegment
from io import BytesIO
import instaloader
from uuid import uuid4

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_token():
    """Get token from environment variables or Streamlit secrets"""
    return os.getenv('TELEGRAM_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message"""
    await update.message.reply_text(
        "Hi! I'm your media bot. I can:\n"
        "1. Convert videos to MP3 - reply to a video with /convert\n"
        "2. Download Instagram reels - send /reel <URL>"
    )

async def convert_to_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert video to MP3 using pydub"""
    if not update.message.reply_to_message or not update.message.reply_to_message.video:
        await update.message.reply_text("Please reply to a video file with /convert")
        return
    
    try:
        video_file = await update.message.reply_to_message.video.get_file()
        unique_id = uuid4().hex
        output_filename = f"converted_{unique_id}.mp3"
        
        video_bytes = await video_file.download_as_bytearray()
        audio = AudioSegment.from_file(BytesIO(video_bytes), format="mp4")
        audio.export(output_filename, format="mp3")
        
        await update.message.reply_audio(audio=open(output_filename, 'rb'))
        
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
    except Exception as e:
        logger.error(f"Error converting video: {e}")
        await update.message.reply_text("Sorry, I couldn't convert that video. Please try again.")

async def download_reel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download Instagram reel"""
    if not context.args:
        await update.message.reply_text("Please send the Instagram reel URL after /reel command")
        return
    
    url = context.args[0]
    if "instagram.com/reel/" not in url:
        await update.message.reply_text("Please provide a valid Instagram reel URL")
        return
    
    try:
        shortcode = url.split("/reel/")[1].split("/")[0]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        unique_id = uuid4().hex
        filename = f"reel_{unique_id}.mp4"
        
        L.download_post(post, target=f"reel_{unique_id}")
        
        for file in os.listdir(f"reel_{unique_id}"):
            if file.endswith(".mp4"):
                os.rename(f"reel_{unique_id}/{file}", filename)
                break
        
        await update.message.reply_video(video=open(filename, 'rb'))
        
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(f"reel_{unique_id}"):
            os.rmdir(f"reel_{unique_id}")
        
    except Exception as e:
        logger.error(f"Error downloading reel: {e}")
        await update.message.reply_text("Sorry, I couldn't download that reel. Please check the URL and try again.")

def run_bot():
    """Run the bot in its own event loop"""
    token = get_token()
    if not token:
        logger.error("Telegram token not found!")
        return
    
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("convert", convert_to_mp3))
    application.add_handler(CommandHandler("reel", download_reel))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application.run_polling()

if __name__ == '__main__':
    run_bot()
