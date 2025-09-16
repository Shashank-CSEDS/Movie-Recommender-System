def main():
    with Main() as bot:
        bot.main_()
        new_df, movies, movies2 = bot.getter()

    def recommend_display(new_df):
        st.title('Movie Recommender System')
        selected_movie_name = st.selectbox('Select a Movie...', new_df['title'].values)
        rec_button = st.button('Recommend')
        if rec_button:
            st.session_state.selected_movie_name = selected_movie_name
            # call recommendation_tags with new_df, etc.

    def paging_movies(movies):
        # paging logic here

    def initial_options(new_df, movies):
        st.session_state.user_menu = streamlit_option_menu.option_menu(
            menu_title='What are you looking for? 👀',
            options=['Recommend me a similar movie', 'Describe me a movie', 'Check all Movies'],
            icons=['film', 'film', 'film'],
            menu_icon='list',
            orientation="horizontal",
        )

        if st.session_state.user_menu == 'Recommend me a similar movie':
            recommend_display(new_df)
        elif st.session_state.user_menu == 'Describe me a movie':
            display_movie_details()
        elif st.session_state.user_menu == 'Check all Movies':
            paging_movies(movies)

    initial_options(new_df, movies)
