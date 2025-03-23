import tweepy
import openai
import os
import time
import random
from dotenv import load_dotenv

# Load API keys từ .env
load_dotenv()

# Danh sách tài khoản Twitter
ACCOUNTS = []
for i in range(1, 6):  # 5 accounts
    ACCOUNTS.append({
        "API_KEY": os.getenv(f"API_KEY_{i}"),
        "API_SECRET": os.getenv(f"API_SECRET_{i}"),
        "ACCESS_TOKEN": os.getenv(f"ACCESS_TOKEN_{i}"),
        "ACCESS_SECRET": os.getenv(f"ACCESS_SECRET_{i}"),
    })

# Tài khoản X (Twitter) mục tiêu
TARGET_USERNAME = os.getenv("TARGET_USERNAME")

# Khởi tạo OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Hàm tạo phản hồi từ AI (GPT-4)
def generate_reply(tweet_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Bạn là một chatbot Twitter thông minh và hài hước."},
                      {"role": "user", "content": tweet_text}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ Lỗi AI: {e}")
        return "Tôi chưa thể trả lời lúc này, hãy thử lại sau!"

# Hàm xử lý tương tác với tweet
def interact_with_tweets(api, client, account_number):
    try:
        target_user = client.get_user(username=TARGET_USERNAME).data
        target_user_id = target_user.id
        print(f"✅ Đã tìm thấy tài khoản mục tiêu: {target_user.username} (ID: {target_user_id})")

        # Lấy danh sách tweet gần đây của target
        tweets = client.get_users_tweets(id=target_user_id, max_results=5, tweet_fields=["id", "text"])
        if not tweets or not tweets.data:
            print(f"❌ Không tìm thấy tweet nào của @{TARGET_USERNAME}")
            return

        for tweet in tweets.data:
            tweet_id = tweet.id
            tweet_text = tweet.text
            print(f"🟢 [Account {account_number}] Xử lý Tweet {tweet_id}: {tweet_text}")

            # Like Tweet
            try:
                client.like(tweet_id)
                print(f"✅ [Account {account_number}] Đã Like Tweet {tweet_id}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Lỗi Like: {e}")

            # Retweet Tweet
            try:
                client.retweet(tweet_id)
                print(f"🔁 [Account {account_number}] Đã Retweet Tweet {tweet_id}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Lỗi Retweet: {e}")

            # Reply với AI-generated message
            try:
                reply_text = generate_reply(tweet_text)
                api.update_status(f"@{TARGET_USERNAME} {reply_text}", in_reply_to_status_id=tweet_id)
                print(f"💬 [Account {account_number}] Đã Reply: {reply_text}")
            except Exception as e:
                print(f"⚠️ [Account {account_number}] Lỗi Reply: {e}")

            time.sleep(random.randint(15, 45))  # Random delay để tránh spam

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý tài khoản mục tiêu: {e}")

# Chạy bot với tất cả tài khoản
while True:
    for i, account in enumerate(ACCOUNTS):
        try:
            auth = tweepy.OAuth1UserHandler(
                account["API_KEY"], account["API_SECRET"],
                account["ACCESS_TOKEN"], account["ACCESS_SECRET"]
            )
            api = tweepy.API(auth, wait_on_rate_limit=True)
            client = tweepy.Client(bearer_token=account["ACCESS_TOKEN"])

            print(f"🚀 Đang chạy bot cho tài khoản {i+1}...")
            interact_with_tweets(api, client, i + 1)

        except Exception as e:
            print(f"⚠️ Lỗi khi chạy bot cho tài khoản {i+1}: {e}")

    print("⏳ Đợi 5 phút trước khi chạy lại...")
    time.sleep(300)  # 5 phút
