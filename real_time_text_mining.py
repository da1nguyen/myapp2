import asyncpraw
import pandas as pd
import asyncio
from datetime import datetime, timedelta
import nest_asyncio
import streamlit as st
from textblob import TextBlob

nest_asyncio.apply()

reddit = asyncpraw.Reddit(
    client_id='FvUOzRsVAyqjhPwwURAQNA',
    client_secret='etpictk0iK7NoNvEjTjovK-lXQjZRg',
    user_agent='My user agent description',
    check_for_updates=False
)

df = pd.DataFrame(columns=["Title", "Created Time (VN)", "Sentiment"])

def format_time(utc_timestamp):
    utc_time = datetime.utcfromtimestamp(utc_timestamp)
    vietnam_time = utc_time + timedelta(hours=7)
    return vietnam_time.strftime('%Y-%m-%d %H:%M:%S')

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity >= 0.6:
        return 'Very Positive'
    elif polarity >= 0.2:
        return 'Positive'
    elif polarity >= -0.2:
        return 'Neutral'
    elif polarity >= -0.6:
        return 'Negative'
    else:
        return 'Very Negative'

async def fetch_latest_posts():
    global df
    seen_submission_ids = set()
    subreddit = await reddit.subreddit('all')

    # Tạo một không gian để cập nhật bảng dữ liệu
    st.write("### Phân tích cảm xuất bình luận theo thời gian thực")
    data_placeholder = st.empty()

    while True:
        async for submission in subreddit.new(limit=10):
            if submission.id not in seen_submission_ids:
                seen_submission_ids.add(submission.id)

                sentiment = analyze_sentiment(submission.title)

                # Cập nhật DataFrame
                new_entry = {
                    "Title": submission.title,
                    "Created Time (VN)": format_time(submission.created_utc),
                    "Sentiment": sentiment
                }
                df = pd.concat([pd.DataFrame([new_entry]), df], ignore_index=True)
                df = df.sort_values(by="Created Time (VN)", ascending=False).reset_index(drop=True)

                with data_placeholder:
                    st.write(
                        f"""
                        <style>
                        .dataframe {{
                            width: 200%;
                            overflow-x: auto;
                        }}
                        .dataframe thead th {{
                            text-align: left;
                            white-space: nowrap;
                        }}
                        .dataframe td {{
                            text-align: left;
                            white-space: nowrap;
                        }}
                        .dataframe thead th:nth-child(1) {{
                            min-width: 1400px; /* Kích thước tối thiểu của cột Title */
                        }}
                        .dataframe thead th:nth-child(2) {{
                            min-width: 400px; /* Kích thước tối thiểu của cột Created Time (VN) */
                        }}
                        .dataframe thead th:nth-child(3) {{
                            min-width: 500px; /* Kích thước tối thiểu của cột Sentiment */
                        }}
                        </style>
                        """, unsafe_allow_html=True
                    )
                    st.dataframe(df, use_container_width=True)

            await asyncio.sleep(1)  # Thay đổi thời gian chờ tùy theo nhu cầu

if st.button('Thực hiện'):
    asyncio.run(fetch_latest_posts())
