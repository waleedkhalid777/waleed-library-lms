import datetime
import streamlit as st 
import pandas as pd 
import json
import os
import time
import random
import requests
import plotly.graph_objects as go 
import plotly.express as px 

st.set_page_config(
    page_title="Library Management System",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem !important;
    color:#1e3a8a;
    font-weight:700;
    margin-bottom: 1rem;
    text-align:center;
    text-shadow:2px 2px 4px rgba(0,0,0,1);
}
.sub_header {
    font-size: 1rem !important;
    color: #3BB2f6;
    font-weight:600;
    margin-top:1rem;
    margin-bottom:1rem;
}
.success-message {
    padding: 1rem;
    background-color: #ECFDF5;
    border-left: 5px solid #108981;
    border-radius:0.375rem;
}
.warning-message {
    padding: 1rem;
    background-color: #fef3c7;
    border-left:5px solid #f59E0b;
    border-radius:0.375rem;
}
.book-card {
    background-color: #F3F4F6;
    border-radius:0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
}
.read-badge {
    background-color: #10B981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: 600;
}
.unread-badge {
    background-color: #F87171;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: 600;       
}
</style>
""", unsafe_allow_html=True)

def load_lottieur(url=None):
    try:
        if url:
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()
    except:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []

if 'search_result' not in st.session_state:
    st.session_state.search_result = []

if 'book_added' not in st.session_state:
    st.session_state.book_added = False

if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False

if 'current_view' not in st.session_state:
    st.session_state.current_view = ""

# Load library from JSON
def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# Save library to JSON
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Add book
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# Remove book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search books
def search_books(search_term, search_by):
    search_term = search_term.lower()
    result = []

    for book in st.session_state.library:
        if search_by == "title" and search_term in book['title'].lower():
            result.append(book)
        elif search_by == "author" and search_term in book['author'].lower():
            result.append(book)
        elif search_by == "genre" and 'genre' in book and search_term in book['genre'].lower():
            result.append(book)

    st.session_state.search_result = result

# Library statistics
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book.get('read_status'))
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        genre = book.get('genre', 'Unknown')
        genres[genre] = genres.get(genre, 0) + 1

        author = book.get('author', 'Unknown')
        authors[author] = authors.get(author, 0) + 1

        try:
            decade = (int(book['publication_year']) // 10) * 10
            decades[decade] = decades.get(decade, 0) + 1
        except:
            continue

    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Visualizations
def create_visualization(stats):
    if stats['total_books'] > 0:
        # Pie chart: Read vs Unread
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            marker_colors=['#10B981', '#F87171']
        )])
        fig_read_status.update_layout(title_text="Read vs Unread Books", height=400)
        st.plotly_chart(fig_read_status, use_container_width=True)

        # Bar chart: Genres
        if stats['genres']:
            genres_df = pd.DataFrame({
                'Genre': list(stats['genres'].keys()),
                'Count': list(stats['genres'].values())
            })
            fig_genres = px.bar(genres_df, x='Genre', y='Count', color='Count', color_continuous_scale='Blues')
            fig_genres.update_layout(title_text="Genres", height=400)
            st.plotly_chart(fig_genres, use_container_width=True)

        # Line chart: Decades
        if stats['decades']:
            decades_df = pd.DataFrame({
                'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
                'Count': list(stats['decades'].values())
            })
            fig_decades = px.line(decades_df, x='Decade', y='Count', markers=True)
            fig_decades.update_layout(title_text="Books by Publication Decade", height=400)
            st.plotly_chart(fig_decades, use_container_width=True)

# Load library
load_library()

# Sidebar navigation
st.sidebar.title("📚 Navigation")
nav_options = st.sidebar.radio("Go to", ["View Library", "Add Book", "Search Books", "Library Statistics"])

if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add"
elif nav_options == "Search Books":
    st.session_state.current_view = "search"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "stats"

# === ADD BOOK ===
if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub_header'>Add a New Book</h2>", unsafe_allow_html=True)

    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.datetime.now().year, step=1, value=2023)

        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Technology", "Fantasy", "Romance", "Poetry", "Self Help", "Art", "Religion", "History"])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"

        submit_button = st.form_submit_button(label="Add Book")

    if submit_button and title and author:
        add_book(title, author, publication_year, genre, read_bool)

if st.session_state.book_added:
    st.markdown("<div class='success-message'>Book added successfully!</div>", unsafe_allow_html=True)
    st.balloons()
    st.session_state.book_added = False

# === VIEW LIBRARY ===
elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub_header'>Your Library</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                        {"Read" if book["read_status"] else "Unread"}
                    </span></p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                if col1.button("Remove", key=f"remove-{i}"):
                    if remove_book(i):
                        st.rerun()
                new_status = not book['read_status']
                status_label = "Mark as Read" if not book['read_status'] else "Mark as Unread"
                if col2.button(status_label, key=f"status-{i}"):
                    st.session_state.library[i]['read_status'] = new_status
                    save_library()
                    st.rerun()

    if st.session_state.book_removed:
        st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_removed = False

# === SEARCH BOOKS ===
elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub_header'>Search Books</h2>", unsafe_allow_html=True)

    search_term = st.text_input("Enter search term")
    search_by = st.selectbox("Search by", ["title", "author", "genre"])

    if st.button("Search"):
        search_books(search_term, search_by)

    for book in st.session_state.search_result:
        st.markdown(f"""
        <div class='book-card'>
            <h3>{book['title']}</h3>
            <p><strong>Author:</strong> {book['author']}</p>
            <p><strong>Year:</strong> {book['publication_year']}</p>
            <p><strong>Genre:</strong> {book['genre']}</p>
            <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                {"Read" if book["read_status"] else "Unread"}
            </span></p>
        </div>
        """, unsafe_allow_html=True)

# === STATISTICS ===
elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub_header'>Library Statistics</h2>", unsafe_allow_html=True)
    stats = get_library_stats()
    create_visualization(stats)

