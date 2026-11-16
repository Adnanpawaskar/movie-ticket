import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Movie Explorer", page_icon="🎬", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RATING_CANDIDATES = ["rating", "imdb_rating", "averageRating", "vote_average", "ratings"]
POPULARITY_CANDIDATES = ["popularity", "numVotes", "votes", "vote_count"]


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_images() -> list:
    path = os.path.join(BASE_DIR, "images.txt")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip().startswith("http")]


def find_col(df: pd.DataFrame, candidates: list):
    lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


movies = load_csv("movies.csv")
bolly = load_csv("BollywoodMovieDetail.csv")

st.title("🎬 Movie Explorer")

if movies.empty:
    st.error("movies.csv nahi mila. Isse app.py ke saath same folder me rakhein.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Movie Images", "Movie Names", "Movie Ratings"])

# ---------------- Tab 1: Images ----------------
with tab1:
    st.header("Movie Images")
    images = load_images()
    if not images:
        st.info("images.txt me image URLs (ek line me ek) daalein.")
    else:
        n_cols = st.slider("Columns", 2, 6, 4)
        cols = st.columns(n_cols)
        for i, url in enumerate(images):
            with cols[i % n_cols]:
                st.image(url, use_container_width=True)

# ---------------- Tab 2: Names (merged data) ----------------
with tab2:
    st.header("Movie Names")
    if not bolly.empty and "title" in movies.columns and "title" in bolly.columns:
        merged = pd.merge(movies, bolly, on="title", how="outer")
    else:
        merged = movies
    search = st.text_input("Search by title")
    view = merged
    if search and "title" in view.columns:
        view = view[view["title"].astype(str).str.contains(search, case=False, na=False)]
    st.write(f"Total movies: {len(view)}")
    st.dataframe(view, use_container_width=True)

# ---------------- Tab 3: Recommendations ----------------
with tab3:
    st.header("Movie Ratings & Recommendations")

    data = movies.copy()
    if not bolly.empty and "title" in bolly.columns:
        data = pd.merge(movies, bolly, on="title", how="left", suffixes=("", "_b"))

    if "genres" not in data.columns:
        st.warning("movies.csv me 'genres' column nahi hai.")
    else:
        # genres like "Action|Comedy" ko alag-alag genre me todna
        all_genres = sorted(
            {g.strip() for v in data["genres"].dropna().astype(str)
             for g in v.replace(",", "|").split("|") if g.strip()}
        )
        genre = st.selectbox("Select Genre", ["All"] + all_genres)

        filtered = data
        if genre != "All":
            filtered = filtered[
                filtered["genres"].astype(str).str.contains(genre, case=False, regex=False, na=False)
            ]

        rating_col = find_col(data, RATING_CANDIDATES)
        pop_col = find_col(data, POPULARITY_CANDIDATES)

        if rating_col:
            vals = pd.to_numeric(filtered[rating_col], errors="coerce")
            max_r = float(pd.to_numeric(data[rating_col], errors="coerce").max())
            min_rating = st.slider("Minimum Rating", 0.0, max(max_r, 1.0), 0.0, 0.1)
            filtered = filtered[vals >= min_rating]
        else:
            st.caption("Rating column nahi mila, isliye rating filter off hai.")

        if pop_col:
            vals = pd.to_numeric(filtered[pop_col], errors="coerce")
            max_p = float(pd.to_numeric(data[pop_col], errors="coerce").max())
            min_pop = st.slider("Minimum Popularity", 0.0, max(max_p, 1.0), 0.0)
            filtered = filtered[vals >= min_pop]
        else:
            st.caption("Popularity column nahi mila, isliye popularity filter off hai.")

        st.write(f"Recommended Movies: {len(filtered)}")
        st.dataframe(filtered, use_container_width=True)
