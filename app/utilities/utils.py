from datetime import datetime
import pandas as pd


def readable_date(date):
    '''
        Convert YYYY-mm-dd formatted date to (for example) Jun 1 2025
    '''
    try:
        date_clean = datetime.strptime(date, "%Y-%m-%d").strftime("%a %d %b, %Y")
        if date_clean[4] == "0":
            date_clean = date_clean[:4] + date_clean[5:]
        if datetime.strptime(date, "%Y-%m-%d").year == datetime.now().year:
            date_clean = date_clean.split(",")[0]
    except Exception as e:
        print(f"Failure prettifying date {date} - {e}")
        date_clean = date
    return(date_clean)