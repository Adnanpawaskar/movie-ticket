# Movie Explorer (Streamlit)

## Folder me ye files honi chahiye
app.py, requirements.txt, render.yaml, images.txt, movies.csv, BollywoodMovieDetail.csv

## Render pe deploy
1. Sab files ek GitHub repo me push karein (CSV files bhi).
2. Render -> New -> Web Service -> repo select karein (ya Blueprint, render.yaml auto-detect hoga).
3. Manual settings agar chahiye:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
4. Deploy dabayein.

## Local run
pip install -r requirements.txt
streamlit run app.py
