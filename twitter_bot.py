import tweepy
import openai
import os
import time
import random
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# List of bot accounts
ACCOUNTS = []
for i in range(1, 6):  # 5 accounts
    ACCOUNTS.append({
        "API_KEY": os.getenv(f"API_KEY_{i}"),
        "API_SECRET": os.getenv(f"API_SECRET_{i}"),
        "ACCESS_TOKEN": os.getenv(f"ACCESS_TOKEN_{i}"),
        "ACCESS_SECRET": os.getenv(f"ACCESS_SECRET_{i}"),
    })

# Target Twitter User ID
TARGET_USER_ID = os.getenv("TARGET_USER_ID")

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Generate AI-based replies using GPT-4
def generate_reply(tweet_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a smart and humorous Twitter chatbot."},
                      {"role": "user", "content": tweet_text}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return "I can't reply right now. Try again later!"

# Function to interact with tweets
def interact_with_tweets(api, client, account_number):
    try:
        print(f"✅ Fetching tweets from target account ID: {TARGET_USER_ID}")

        # Retrieve recent tweets from the target account
        tweets = client.get_users_tweets(id=TARGET_USER_ID, max_results=5, tweet_fields=["id", "text"])
        if not tweets or not tweets.data:
            print(f"❌ No tweets found for account ID {TARGET_USER_ID}")
            return

        for tweet in tweets.data:
            tweet_id = tweet.id
            tweet_text = tweet.text
            print(f"🟢 [Account {account_number}] Processing Tweet {tweet_id}: {tweet_text}")

            # Like Tweet
            try:
                client.like(tweet_id)
                print(f"✅ [Account {account_number}] Liked Tweet {tweet_id}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Like Error: {e}")

            # Retweet Tweet
            try:
                client.retweet(tweet_id)
                print(f"🔁 [Account {account_number}] Retweeted Tweet {tweet_id}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Retweet Error: {e}")

            # Reply with AI-generated message
            try:
                reply_text = generate_reply(tweet_text)
                api.update_status(f"@{TARGET_USER_ID} {reply_text}", in_reply_to_status_id=tweet_id)
                print(f"💬 [Account {account_number}] Replied: {reply_text}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Reply Error: {e}")

            time.sleep(random.randint(15, 45))  # Random delay to avoid spam

    except Exception as e:
        print(f"⚠️ Error processing target account: {e}")

# Run the bot for all accounts
while True:
    for i, account in enumerate(ACCOUNTS):
        try:
            auth = tweepy.OAuth2UserHandler(
                client_id=account["API_KEY"],
                client_secret=account["API_SECRET"],
                access_token=account["ACCESS_TOKEN"],
                access_token_secret=account["ACCESS_SECRET"]
            )
            client = tweepy.Client(
                bearer_token=os.getenv("BEARER_TOKEN"),
                consumer_key=account["API_KEY"],
                consumer_secret=account["API_SECRET"],
                access_token=account["ACCESS_TOKEN"],
                access_token_secret=account["ACCESS_SECRET"]
            )

            print(f"🚀 Running bot for account {i+1}...")
            interact_with_tweets(api, client, i + 1)

        except Exception as e:
            print(f"⚠️ Error running bot for account {i+1}: {e}")

    print("⏳ Waiting 5 minutes before running again...")
    time.sleep(300)  # 5 minutes
