import tweepy
import openai
import os
import time
from dotenv import load_dotenv

# Load API keys từ .env
load_dotenv()

# Danh sách tài khoản X (Twitter) - Thay bằng các thông tin của bạn
ACCOUNTS = [
    {
        "API_KEY": os.getenv("API_KEY_1"),
        "API_SECRET": os.getenv("API_SECRET_1"),
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN_1"),
        "ACCESS_SECRET": os.getenv("ACCESS_SECRET_1"),
    },
    {
        "API_KEY": os.getenv("API_KEY_2"),
        "API_SECRET": os.getenv("API_SECRET_2"),
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN_2"),
        "ACCESS_SECRET": os.getenv("ACCESS_SECRET_2"),
    },
    {
        "API_KEY": os.getenv("API_KEY_3"),
        "API_SECRET": os.getenv("API_SECRET_3"),
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN_3"),
        "ACCESS_SECRET": os.getenv("ACCESS_SECRET_3"),
    },
    {
        "API_KEY": os.getenv("API_KEY_4"),
        "API_SECRET": os.getenv("API_SECRET_4"),
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN_4"),
        "ACCESS_SECRET": os.getenv("ACCESS_SECRET_4"),
    },
    {
        "API_KEY": os.getenv("API_KEY_5"),
        "API_SECRET": os.getenv("API_SECRET_5"),
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN_5"),
        "ACCESS_SECRET": os.getenv("ACCESS_SECRET_5"),
    }
]

# Tài khoản X (Twitter) mục tiêu
TARGET_USERNAME = "farmerking89"  # Thay bằng tài khoản bạn muốn theo dõi

# Hàm tạo phản hồi từ AI (GPT-4)
def generate_reply(tweet_text):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Bạn là một chatbot Twitter thông minh và hài hước."},
                  {"role": "user", "content": tweet_text}]
    )
    return response["choices"][0]["message"]["content"]

# Hàm xử lý tương tác với tweet
def interact_with_tweets(api, user_id):
    tweets = api.user_timeline(user_id=user_id, count=5, tweet_mode="extended")
    
    for tweet in tweets:
        tweet_id = tweet.id
        tweet_text = tweet.full_text
        tweet_author = tweet.user.screen_name

        try:
            # Auto-Like
            api.create_favorite(tweet_id)
            print(f"💙 [{api.auth.get_username()}] Đã like tweet của @{tweet_author}")

            # Auto-Retweet
            api.retweet(tweet_id)
            print(f"🔁 [{api.auth.get_username()}] Đã retweet tweet của @{tweet_author}")

            # Auto-Reply với AI
            ai_reply = generate_reply(tweet_text)
            api.update_status(f"@{tweet_author} {ai_reply}", in_reply_to_status_id=tweet_id)
            print(f"💬 [{api.auth.get_username()}] Đã reply tweet của @{tweet_author}")

        except Exception as e:
            print(f"⚠️ Lỗi: {e}")

# Chạy bot với nhiều tài khoản
while True:
    for account in ACCOUNTS:
        auth = tweepy.OAuth1UserHandler(
            account["API_KEY"], account["API_SECRET"],
            account["ACCESS_TOKEN"], account["ACCESS_SECRET"]
        )
        client = tweepy.client(auth, wait_on_rate_limit=True)

        # Lấy ID của tài khoản mục tiêu
        target_user = client.get_user(screen_name=TARGET_USERNAME)
        target_user_id = target_user.id

        # Chạy bot cho từng tài khoản
        interact_with_tweets(api, target_user_id)

    time.sleep(300)  # Đợi 5 phút trước khi chạy lại
