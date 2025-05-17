import cohere
import tweepy
import random
import re
import os
from dotenv import load_dotenv

# -------- LOAD ENV -------- #
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
WOEID = int(os.getenv("WOEID", 23424848))  # Default to India

# -------- INIT -------- #
co = cohere.Client(COHERE_API_KEY)

auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)
twitter_api = tweepy.API(auth)

USED_TWEETS_FILE = "used_tweets.txt"

# -------- PROMPTS -------- #
prompt_templates = [
    "Write a tweet about the latest global political development.",
    "What's a witty, engaging tweet about a major event in tech news today?",
    "Summarize an important world news event in a tweet with a strong opinion.",
    "Generate a viral-style tweet based on current global affairs.",
    "Write a short, punchy tweet about something trending in world politics or economics."
]

keyword_hashtag_map = {
    "election": "#Election2025",
    "ai": "#ArtificialIntelligence",
    "tech": "#TechNews",
    "startup": "#Startups",
    "modi": "#Modi",
    "india": "#India",
    "bjp": "#BJP",
    "congress": "#Congress",
    "war": "#Conflict",
    "bitcoin": "#Crypto",
    "stock": "#StockMarket",
    "israel": "#Israel",
    "palestine": "#Palestine",
    "russia": "#Russia",
    "china": "#China",
    "usa": "#USA",
    "uk": "#UK",
    "inflation": "#Economy",
    "unemployment": "#Jobs",
}

# -------- FUNCTIONS -------- #

def load_used_tweets():
    if not os.path.exists(USED_TWEETS_FILE):
        return set()
    with open(USED_TWEETS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_used_tweet(tweet):
    with open(USED_TWEETS_FILE, "a", encoding="utf-8") as f:
        f.write(tweet.strip() + "\n")

def get_trending_hashtags():
    try:
        trends = twitter_api.get_place_trends(WOEID)
        hashtags = [
            t["name"] for t in trends[0]["trends"]
            if t["name"].startswith("#") and len(t["name"]) <= 30
        ]
        return hashtags[:5]
    except Exception as e:
        print("Error fetching trending hashtags:", e)
        return []

def auto_add_hashtags(tweet, trending):
    """Add hashtags based on content + live trends."""
    tags = set()

    for keyword, hashtag in keyword_hashtag_map.items():
        if re.search(rf"\b{keyword}\b", tweet, re.IGNORECASE):
            tags.add(hashtag)

    tags.update(trending)
    full_tweet = f"{tweet} {' '.join(tags)}"
    return full_tweet[:280]

def clean_tweet(text):
    tweet = re.sub(r'\s+', ' ', text).strip()
    return tweet[:280]

def generate_tweets(n=5):
    prompt = random.choice(prompt_templates)
    print(f"\nPrompt used: {prompt}\n")

    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        max_tokens=100,
        temperature=0.9,
        num_generations=n
    )

    seen = set()
    tweets = []
    used = load_used_tweets()
    for gen in response.generations:
        tweet = clean_tweet(gen.text)
        if tweet and tweet not in seen and tweet not in used:
            seen.add(tweet)
            tweets.append(tweet)
    return tweets

def choose_tweet(tweets, trending_tags):
    print("\nChoose a tweet to post:\n")
    for i, t in enumerate(tweets, 1):
        preview = auto_add_hashtags(t, trending_tags)
        print(f"{i}. {preview}\n")

    while True:
        try:
            choice = int(input(f"Enter 1-{len(tweets)} to post or 0 to cancel: "))
            if choice == 0:
                return None
            if 1 <= choice <= len(tweets):
                return auto_add_hashtags(tweets[choice - 1], trending_tags), tweets[choice - 1]
        except ValueError:
            pass
        print("Invalid choice. Try again.")

def post_tweet(tweet):
    try:
        twitter_api.update_status(tweet)
        print("\n✅ Tweet posted successfully!")
    except tweepy.TweepyException as e:
        print("\n❌ Failed to post tweet:", e)

# -------- RUN -------- #

if __name__ == "__main__":
    tweets = generate_tweets()
    if not tweets:
        print("No new valid tweets generated.")
    else:
        trending = get_trending_hashtags()
        chosen, original = choose_tweet(tweets, trending)
        if chosen:
            print(f"\nFinal tweet:\n{chosen}\n")
            confirm = input("Post this tweet? (y/n): ").lower()
            if confirm == 'y':
                post_tweet(chosen)
                save_used_tweet(original)
            else:
                print("Tweet cancelled.")
