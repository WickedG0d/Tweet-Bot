import tweepy
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Setup Twitter Auth
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET
)

twitter_api = tweepy.API(auth)

# Try verifying credentials
print("\n🔍 Verifying Twitter credentials...")
try:
    user = twitter_api.verify_credentials()
    if user:
        print(f"✅ Authenticated as: @{user.screen_name}")
        print("✔️ You are authenticated. Now testing write access...")

        test_status = "This is a test tweet from my bot. If you're seeing this, the API works! 🧪 #TwitterBotTest"
        twitter_api.update_status(test_status)
        print("✅ Tweet posted successfully.")
    else:
        print("❌ Could not verify credentials.")
except tweepy.TweepyException as e:
    print("❌ Error verifying credentials or posting tweet:", e)
