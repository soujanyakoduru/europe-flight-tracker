# Flight Tracker (Europe trip — Jul 30 to Aug 17)

Tracks EY239, EY153, EY156, EY232. Dashboard has a **Refresh now** button —
click it to pull live status for the selected flight and see its last 7
days (status, scheduled/actual departure & arrival, delays).

## Why there's still a tiny background job

SkyLink's free tier gives rich live status but only reaches a few days of
history — no free API guarantees a full 7-day lookback for a specific
flight number. So a lightweight job runs **once a day** (not continuously)
purely to make sure no day goes unrecorded if you don't happen to open the
dashboard that day. Your manual refresh is still the only thing that
fetches "right now" data.

## Setup

1. **Get a free SkyLink API key**: sign up at https://rapidapi.com/ → search
   "SkyLink API" → subscribe to the free plan (1,000 req/month, no card).
2. **Push this folder to a GitHub repo.**
3. **Add the key as a repo secret** (for the daily snapshot job):
   Settings → Secrets and variables → Actions → New repository secret →
   name it `RAPIDAPI_KEY`.
4. **Deploy the dashboard for free** on https://share.streamlit.io:
   - Connect your GitHub repo, set the entrypoint to `app.py`.
   - In the app's Settings → Secrets, add:
     ```
     RAPIDAPI_KEY = "your_key_here"
     ```
   - You'll get a URL you can open from your phone or laptop any time —
     click Refresh whenever you want the latest.

## Running locally instead

```bash
pip install -r requirements.txt
mkdir -p .streamlit && echo 'RAPIDAPI_KEY = "your_key_here"' > .streamlit/secrets.toml
streamlit run app.py
```

## Files

- `app.py` — the dashboard (Streamlit).
- `skylink_client.py` — talks to the SkyLink API.
- `history_store.py` — reads/writes `data/flight_history.csv`.
- `daily_snapshot.py` + `.github/workflows/track_flights.yml` — the
  once-daily insurance snapshot, runs automatically via GitHub Actions.

## After the trip

Just stop the GitHub Actions workflow (or delete the repo) — this was
built to be disposable for a 3-week window, nothing to unwind.
