import tweepy
import openai
import os
import time
import random
from dotenv import load_dotenv

# Load API keys từ file .env
load_dotenv()

# Danh sách 5 tài khoản bot
ACCOUNTS = []
for i in range(1, 6):  # 5 tài khoản
    ACCOUNTS.append({
        "API_KEY": os.getenv(f"API_KEY_{i}"),
        "API_SECRET": os.getenv(f"API_SECRET_{i}"),
        "ACCESS_TOKEN": os.getenv(f"ACCESS_TOKEN_{i}"),
        "ACCESS_SECRET": os.getenv(f"ACCESS_SECRET_{i}"),
    })

# ID tài khoản mục tiêu
TARGET_USER_ID = os.getenv("TARGET_USER_ID")

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Hàm tạo phản hồi bằng OpenAI GPT-4
def generate_reply(tweet_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Bạn là một chatbot Twitter thông minh, hài hước và tự nhiên."},
                {"role": "user", "content": tweet_text}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return "Xin lỗi, tôi không thể trả lời ngay bây giờ!"

# Hàm xử lý tweet (Like, Retweet, Reply)
def interact_with_tweets(api, account_number):
    try:
        print(f"✅ [Account {account_number}] Fetching tweets from target ID: {TARGET_USER_ID}")
        tweets = api.user_timeline(user_id=TARGET_USER_ID, count=5, tweet_mode="extended")

        if not tweets:
            print(f"❌ [Account {account_number}] No tweets found for target ID: {TARGET_USER_ID}")
            return

        for tweet in tweets:
            tweet_id = tweet.id
            tweet_text = tweet.full_text
            print(f"🟢 [Account {account_number}] Processing Tweet {tweet_id}: {tweet_text}")

            # Like Tweet
            try:
                api.create_favorite(tweet_id)
                print(f"✅ [Account {account_number}] Liked Tweet {tweet_id}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Like Error: {e}")

            # Retweet
            try:
                api.retweet(tweet_id)
                print(f"🔁 [Account {account_number}] Retweeted Tweet {tweet_id}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Retweet Error: {e}")

            # Reply với AI-generated content
            try:
                reply_text = generate_reply(tweet_text)
                api.update_status(f"@{tweet.user.screen_name} {reply_text}", in_reply_to_status_id=tweet_id)
                print(f"💬 [Account {account_number}] Replied: {reply_text}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Reply Error: {e}")

            time.sleep(random.randint(15, 45))  # Delay ngẫu nhiên để tránh spam

    except Exception as e:
        print(f"⚠️ [Account {account_number}] Error processing target account: {e}")

# Chạy bot cho tất cả các tài khoản
while True:
    for i, account in enumerate(ACCOUNTS):
        try:
            auth = tweepy.OAuthHandler(account["API_KEY"], account["API_SECRET"])
            auth.set_access_token(account["ACCESS_TOKEN"], account["ACCESS_SECRET"])
            api = tweepy.API(auth, wait_on_rate_limit=True)

            print(f"🚀 Running bot for account {i+1}...")
            interact_with_tweets(api, i + 1)
        except Exception as e:
            print(f"⚠️ Error running bot for account {i+1}: {e}")

    print("⏳ Waiting 5 minutes before running again...")
    time.sleep(300)  # Chờ 5 phút trước khi chạy lại
