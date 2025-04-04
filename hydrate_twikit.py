import asyncio
import pandas as pd
from twikit import Client
from configparser import ConfigParser
import os
import time
import random
import sys
import argparse
import logging

# Increase recursion limit if necessary
sys.setrecursionlimit(2000)

# ---------------------------
# Logging Configuration Block
# ---------------------------

# Create a global logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Capture all levels internally

# File handler: log all messages to "fail_log_verbose.txt"
file_handler = logging.FileHandler("fail_log_verbose.txt", mode='a')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler: display only INFO level and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console_handler.setFormatter(console_formatter)

# Filter to remove HTTP request details from console output
class NoHTTPRequestFilter(logging.Filter):
    def filter(self, record):
        return "HTTP Request:" not in record.getMessage()

console_handler.addFilter(NoHTTPRequestFilter())
logger.addHandler(console_handler)

# ---------------------------
# End Logging Configuration
# ---------------------------

# Parse configuration from config.ini with interpolation disabled (to avoid issues with '%' in passwords)
config = ConfigParser(interpolation=None)
config.read('config.ini')
USERNAME = config.get("X", "username")
EMAIL = config.get("X", "email")
PASSWORD = config.get("X", "password")

# Parse command-line arguments for flexibility
def parse_arguments():
    parser = argparse.ArgumentParser(description="Hydrate Tweets by tweet IDs")
    parser.add_argument('--input', type=str, default="ISCRAM18_datasets/Maria_tweet_ids.txt",
                        help="Input file with tweet IDs")
    parser.add_argument('--output', type=str, default="hydrated_tweets.csv",
                        help="Output CSV file for hydrated tweets")
    parser.add_argument('--failed', type=str, default="failed_ids.txt",
                        help="File to log failed tweet IDs")
    parser.add_argument('--batch-size', type=int, default=25,
                        help="Batch size for saving results")
    parser.add_argument('--limit', type=int, default=150,
                        help="Total limit for tweets to hydrate")
    return parser.parse_args()

args = parse_arguments()
INPUT_FILE = args.input
OUTPUT_FILE = args.output
FAILED_IDS_FILE = args.failed
BATCH_SIZE = args.batch_size
TOTAL_LIMIT = args.limit

client = Client("en-US")

# Async function to hydrate a tweet by ID with retry mechanism
async def hydrate_by_id(tweet_id, retries=3):
    for attempt in range(1, retries + 1):
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
            logger.error(f"Attempt {attempt}: Error with tweet {tweet_id}: {e}")
            if attempt < retries:
                await asyncio.sleep(2)  # Delay before retrying
            else:
                return None

async def main():
    # Authenticate using cookies if available
    if os.path.exists("cookies.json"):
        client.load_cookies("cookies.json")
    else:
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD,
            cookies_file="cookies.json",
        )

    # Load tweet IDs from the input file
    try:
        with open(INPUT_FILE, "r") as f:
            all_ids = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error reading input file {INPUT_FILE}: {e}")
        return

    # Load already hydrated IDs from existing output file, if available
    hydrated_ids = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = pd.read_csv(OUTPUT_FILE, usecols=["id"])
            hydrated_ids = set(str(x) for x in df_existing["id"].unique())
        except Exception as e:
            logger.warning(f"Could not read {OUTPUT_FILE}: {e}")

    # Load previously failed tweet IDs
    failed_ids = set()
    if os.path.exists(FAILED_IDS_FILE):
        try:
            with open(FAILED_IDS_FILE, "r") as f:
                failed_ids = set(line.strip() for line in f if line.strip())
        except Exception as e:
            logger.warning(f"Could not read {FAILED_IDS_FILE}: {e}")

    # Filter tweet IDs to process only new ones
    tweet_ids = [tid for tid in all_ids if tid not in hydrated_ids and tid not in failed_ids]
    tweet_ids = tweet_ids[:TOTAL_LIMIT]
    logger.info(f"Tweets to hydrate this run: {len(tweet_ids)}")

    results = []
    success_count = 0
    failure_count = 0
    start_time = time.time()

    for index, tweet_id in enumerate(tweet_ids, start=1):
        data = await hydrate_by_id(tweet_id)
        if data:
            results.append(data)
            success_count += 1
        else:
            failure_count += 1
            with open(FAILED_IDS_FILE, "a") as fail_log:
                fail_log.write(f"{tweet_id}\n")

        # Save results in batches
        if index % BATCH_SIZE == 0:
            try:
                df = pd.DataFrame(results)
                if os.path.exists(OUTPUT_FILE):
                    df.to_csv(OUTPUT_FILE, mode="a", index=False, header=False)
                else:
                    df.to_csv(OUTPUT_FILE, index=False)
                logger.info(f"Batch saved: {index}/{len(tweet_ids)}")
            except Exception as e:
                logger.error(f"Error saving batch at index {index}: {e}")
            results = []

        # Random delay to mimic human behavior and avoid rate limits
        delay = random.uniform(1.0, 2.5)
        await asyncio.sleep(delay)

    # Save any remaining results
    if results:
        try:
            df = pd.DataFrame(results)
            if os.path.exists(OUTPUT_FILE):
                df.to_csv(OUTPUT_FILE, mode="a", index=False, header=False)
            else:
                df.to_csv(OUTPUT_FILE, index=False)
        except Exception as e:
            logger.error(f"Error saving final batch: {e}")

    elapsed = time.time() - start_time
    logger.info(f"Done: {success_count} succeeded, {failure_count} failed")
    logger.info(f"Time elapsed: {elapsed / 60:.2f} minutes")
    logger.info(f"Results saved in: {OUTPUT_FILE}")

if __name__ == '__main__':
    asyncio.run(main())
