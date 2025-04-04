import asyncio
import pandas as pd
from twikit import Client
from dotenv import load_dotenv
import os
import time
import random
import sys
sys.setrecursionlimit(2000)

# Load environment variables
load_dotenv()

USERNAME = os.getenv("USERNAME")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

INPUT_FILE = "ISCRAM18_datasets/Maria_tweet_ids.txt"
OUTPUT_FILE = "hydrated_tweets.csv"
COOKIES_FILE = "cookies.json"
FAILED_IDS_FILE = "failed_ids.txt"

# Configurable limits
TOTAL_LIMIT = 150
BATCH_SIZE = 25

client = Client("en-US")


async def hydrate_by_id(tweet_id):
    try:
        tweet = await client.get_tweet_by_id(tweet_id)
        if tweet is None or tweet.user is None:
            raise ValueError("Tweet or user not available")
        return {
            "id": tweet.id,
            "text": tweet.text,
            "created_at": tweet.created_at,
            "like_count": tweet.favorite_count,
            "retweet_count": tweet.retweet_count,
            "lang": tweet.lang,
            "username": getattr(tweet.user, "screen_name", "unknown"),
        }
    except Exception as e:
        print(f"❌ Error with tweet {tweet_id}: {e}")
        return None

async def main():
    # Authenticate
    if os.path.exists(COOKIES_FILE):
        client.load_cookies(COOKIES_FILE)
    else:
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD,
            cookies_file=COOKIES_FILE,
        )

    # Load tweet IDs from source
    with open(INPUT_FILE, "r") as f:
        all_ids = [line.strip() for line in f if line.strip()]

    # Load hydrated IDs
    hydrated_ids = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = pd.read_csv(OUTPUT_FILE, usecols=["id"])
            hydrated_ids = set(str(x) for x in df_existing["id"].unique())
        except Exception as e:
            print(f"⚠️ Could not read {OUTPUT_FILE}: {e}")

    # Load failed IDs
    failed_ids = set()
    if os.path.exists(FAILED_IDS_FILE):
        with open(FAILED_IDS_FILE, "r") as f:
            failed_ids = set(line.strip() for line in f if line.strip())

    # Filter IDs
    tweet_ids = [tid for tid in all_ids if tid not in hydrated_ids and tid not in failed_ids]
    tweet_ids = tweet_ids[:TOTAL_LIMIT]
    total_ids = len(tweet_ids)
    print(f"🔎 Tweets to hydrate this run: {total_ids}")

    results = []
    success_count = 0
    failure_count = 0
    start_time = time.time()

    for index, tweet_id in enumerate(tweet_ids, 1):
        data = await hydrate_by_id(tweet_id)
        if data:
            results.append(data)
            success_count += 1
        else:
            failure_count += 1
            with open(FAILED_IDS_FILE, "a") as fail_log:
                fail_log.write(f"{tweet_id}\n")

        # Save in batches
        if index % BATCH_SIZE == 0:
            df = pd.DataFrame(results)
            if os.path.exists(OUTPUT_FILE):
                df.to_csv(OUTPUT_FILE, mode="a", index=False, header=False)
            else:
                df.to_csv(OUTPUT_FILE, index=False)
            print(f"✅ Batch saved: {index}/{total_ids}")
            results = []

        # Random delay
        delay = random.uniform(1.0, 2.5)
        await asyncio.sleep(delay)

    # Save final batch
    if results:
        df = pd.DataFrame(results)
        if os.path.exists(OUTPUT_FILE):
            df.to_csv(OUTPUT_FILE, mode="a", index=False, header=False)
        else:
            df.to_csv(OUTPUT_FILE, index=False)

    elapsed = time.time() - start_time
    print(f"\n✅ Done: {success_count} succeeded, {failure_count} failed")
    print(f"🕒 Time: {elapsed / 60:.2f} minutes")
    print(f"📁 Saved in: {OUTPUT_FILE}")

asyncio.run(main())
