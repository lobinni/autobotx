import tweepy
import openai
import os
import time
import random
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# Twitter accounts configuration
ACCOUNTS = []
for i in range(1, 6):  # 5 accounts
    ACCOUNTS.append({
        "API_KEY": os.getenv(f"API_KEY_{i}"),
        "API_SECRET": os.getenv(f"API_SECRET_{i}"),
        "ACCESS_TOKEN": os.getenv(f"ACCESS_TOKEN_{i}"),
        "ACCESS_SECRET": os.getenv(f"ACCESS_SECRET_{i}"),
    })

# Target account ID
TARGET_USER_ID = os.getenv("TARGET_USER_ID")

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Generate AI reply
def generate_reply(tweet_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a witty and engaging Twitter chatbot."},
                {"role": "user", "content": tweet_text}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return "I can't respond right now, please try again later!"

# Reply to target account tweets
def reply_to_tweets(api, account_number):
    try:
        tweets = api.user_timeline(user_id=TARGET_USER_ID, count=5, tweet_mode="extended")
        if not tweets:
            print(f"❌ No tweets found for target ID: {TARGET_USER_ID}")
            return
        
        for tweet in tweets:
            tweet_id = tweet.id
            tweet_text = tweet.full_text
            print(f"🟢 [Account {account_number}] Processing Tweet {tweet_id}: {tweet_text}")
            
            # Generate AI response
            reply_text = generate_reply(tweet_text)
            
            try:
                api.update_status(f"@{tweet.user.screen_name} {reply_text}", in_reply_to_status_id=tweet_id)
                print(f"💬 [Account {account_number}] Replied: {reply_text}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Reply Error: {e}")
            
            time.sleep(random.randint(15, 45))  # Random delay to avoid spam
    except Exception as e:
        print(f"⚠️ Error processing target account: {e}")

# Run bot for all accounts
while True:
    for i, account in enumerate(ACCOUNTS):
        try:
            auth = tweepy.OAuthHandler(account["API_KEY"], account["API_SECRET"])
            auth.set_access_token(account["ACCESS_TOKEN"], account["ACCESS_SECRET"])
            api = tweepy.API(auth, wait_on_rate_limit=True)
            
            print(f"🚀 Running bot for account {i+1}...")
            reply_to_tweets(api, i + 1)
        except Exception as e:
            print(f"⚠️ Error running bot for account {i+1}: {e}")
    
    print("⏳ Waiting 5 minutes before running again...")
    time.sleep(300)  # Wait 5 minutes
