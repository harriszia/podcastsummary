import streamlit as st
import modal
import json
import os

def main():
    st.title("Newsletter Dashboard")

    available_podcast_info = create_dict_from_json_files('.')

    # Left section - Input fields
    st.sidebar.header("Podcast RSS Feeds")

    # Dropdown box
    st.sidebar.subheader("Available Podcasts Feeds")
    podcast_options = list(available_podcast_info.keys())
    
    selected_index = st.sidebar.selectbox("Select Podcast", options=podcast_options, index=0, format_func=lambda x: "Select Podcast")
    
    # Placeholder for displaying podcast info
    podcast_placeholder = st.empty()

    # If an actual podcast is selected
    if selected_index != 0:
        selected_podcast = podcast_options[selected_index - 1]  # Adjust the index
        display_podcast_info(podcast_placeholder, available_podcast_info[selected_podcast])

    # User Input box
    st.sidebar.subheader("Add and Process New Podcast Feed")
    url = st.sidebar.text_input("Link to RSS Feed")

    process_button = st.sidebar.button("Process Podcast Feed")
    st.sidebar.markdown("**Note**: Podcast processing can take up to 5 mins, please be patient.")

    if process_button:
        podcast_info = process_podcast_info(url)
        podcast_title = podcast_info['podcast_details']['podcast_title']
        available_podcast_info[podcast_title] = podcast_info
        podcast_options.append(podcast_title)  # Add to dropdown options
        selected_index = podcast_options.index(podcast_title) + 1  # Update the selected index
        st.sidebar.selectbox("Select Podcast", options=podcast_options, index=selected_index, format_func=lambda x: "Select Podcast")
        display_podcast_info(podcast_placeholder, podcast_info)

def display_podcast_info(podcast_placeholder, podcast_info):
    podcast_placeholder.header("Newsletter Content")

    # Display the podcast title
    podcast_placeholder.subheader("Episode Title")
    podcast_placeholder.write(podcast_info['podcast_details']['episode_title'])

    # Display the podcast summary and the cover image in a side-by-side layout
    col1, col2 = podcast_placeholder.columns([7, 3])

    with col1:
        # Display the podcast episode summary
        podcast_placeholder.subheader("Podcast Episode Summary")
        podcast_placeholder.write(podcast_info['podcast_summary'])

    with col2:
        podcast_placeholder.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)

    # Display the five key moments
    podcast_placeholder.subheader("Key Moments")
    key_moments = podcast_info['podcast_highlights']
    for moment in key_moments.split('\n'):
        podcast_placeholder.markdown(f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)

def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info['podcast_details']['podcast_title']
            data_dict[podcast_name] = podcast_info

    return data_dict

def process_podcast_info(url):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call(url, '/content/podcast/')
    return output

if __name__ == '__main__':
    main()
