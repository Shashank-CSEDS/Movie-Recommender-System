import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.stoggle import stoggle
from processing import preprocess
from processing.display import Main

# Setting the wide mode as default
st.set_page_config(layout="wide")

# Initialize session state variables if not present
if 'movie_number' not in st.session_state:
    st.session_state['movie_number'] = 0

if 'selected_movie_name' not in st.session_state:
    st.session_state['selected_movie_name'] = ""

if 'user_menu' not in st.session_state:
    st.session_state['user_menu'] = ""

if 'displayed' not in st.session_state:
    st.session_state['displayed'] = []

def main():
    # These will be assigned after bot.getter()
    new_df = None
    movies = None

    def initial_options():
        # Display menu and update session state
        st.session_state.user_menu = option_menu(
            menu_title='What are you looking for? 👀',
            options=['Recommend me a similar movie', 'Describe me a movie', 'Check all Movies'],
            icons=['film', 'film', 'film'],
            menu_icon='list',
            orientation="horizontal",
        )

        if st.session_state.user_menu == 'Recommend me a similar movie':
            recommend_display()

        elif st.session_state.user_menu == 'Describe me a movie':
            display_movie_details()

        elif st.session_state.user_menu == 'Check all Movies':
            paging_movies()

    def recommend_display():
        st.title('Movie Recommender System')

        selected_movie_name = st.selectbox(
            'Select a Movie...', new_df['title'].values
        )

        rec_button = st.button('Recommend')
        if rec_button:
            st.session_state.selected_movie_name = selected_movie_name
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_tags.pkl', "are")
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_genres.pkl', "on the basis of genres are")
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_tprduction_comp.pkl', "from the same production company are")
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_keywords.pkl', "on the basis of keywords are")
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_tcast.pkl', "on the basis of cast are")

    def recommendation_tags(df, selected_movie_name, pickle_file_path, description):
        movies_rec, posters = preprocess.recommend(df, selected_movie_name, pickle_file_path)
        st.subheader(f'Best Recommendations {description}...')

        rec_movies = []
        rec_posters = []
        cnt = 0
        # Adding only 5 unique recommendations
        for i, movie in enumerate(movies_rec):
            if cnt == 5:
                break
            if movie not in st.session_state.displayed:
                rec_movies.append(movie)
                rec_posters.append(posters[i])
                st.session_state.displayed.append(movie)
                cnt += 1

        # Check if we have at least 5 recommendations
        if len(rec_movies) < 5:
            st.warning("Less than 5 unique recommendations available.")
            return

        cols = st.columns(5)
        for idx, col in enumerate(cols):
            col.text(rec_movies[idx])
            col.image(rec_posters[idx])

    def display_movie_details():
        selected_movie_name = st.session_state.selected_movie_name
        if not selected_movie_name:
            st.info("Please select a movie first in 'Recommend me a similar movie' tab.")
            return

        info = preprocess.get_details(selected_movie_name)

        with st.container():
            image_col, text_col = st.columns((1, 2))
            with image_col:
                st.text('\n')
                st.image(info[0])

            with text_col:
                st.text('\n\n')
                st.title(selected_movie_name)
                st.text('\n')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text("Rating")
                    st.write(info[8])
                with col2:
                    st.text("No. of ratings")
                    st.write(info[9])
                with col3:
                    st.text("Runtime")
                    st.write(info[6])

                st.text('\n')
                st.write("Overview")
                st.write(info[3], wrapText=False)
                st.text('\n')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text("Release Date")
                    st.text(info[4])
                with col2:
                    st.text("Budget")
                    st.text(info[1])
                with col3:
                    st.text("Revenue")
                    st.text(info[5])

                st.text('\n')
                col1, col2, col3 = st.columns(3)
                with col1:
                    genres_str = " . ".join(info[2])
                    st.text("Genres")
                    st.write(genres_str)

                with col2:
                    available_in_str = " . ".join(info[13])
                    st.text("Available in")
                    st.write(available_in_str)
                with col3:
                    st.text("Directed by")
                    st.text(info[12][0])
                st.text('\n')

        # Displaying information of casts.
        st.header('Cast')
        cnt = 0
        urls = []
        bio = []
        for cast_member in info[14]:
            if cnt == 5:
                break
            url, biography = preprocess.fetch_person_details(cast_member)
            urls.append(url)
            bio.append(biography)
            cnt += 1

        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if idx < len(urls):
                col.image(urls[idx])
                stoggle("Show More", bio[idx])

    def paging_movies():
        max_pages = len(movies) // 10
        if max_pages == 0:
            st.info("No movies to display.")
            return

        col1, col2, col3 = st.columns([1, 9, 1])

        with col1:
            prev_btn = st.button("Prev")
            if prev_btn and st.session_state['movie_number'] >= 10:
                st.session_state['movie_number'] -= 10

        with col2:
            new_page_number = st.slider("Jump to page number", 0, max_pages, st.session_state['movie_number'] // 10)
            st.session_state['movie_number'] = new_page_number * 10

        with col3:
            next_btn = st.button("Next")
            if next_btn and st.session_state['movie_number'] + 10 < len(movies):
                st.session_state['movie_number'] += 10

        display_all_movies(st.session_state['movie_number'])

    def display_all_movies(start):
        i = start
        total_movies = len(movies)
        # Display two rows of 5 columns each (10 movies)
        for _ in range(2):
            cols = st.columns(5)
            for col in cols:
                if i >= total_movies:
                    break
                movie_id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(movie_id)
                col.image(link, caption=movies.iloc[i]['title'])
                i += 1

        st.session_state['page_number'] = i

    # Use Main context manager to get data
    with Main() as bot:
        bot.main_()
        new_df, movies, _ = bot.getter()
        initial_options()


if __name__ == '__main__':
    main()
