import streamlit as st
import pandas as pd
import spacy

# Load the dataset
@st.cache_data
def preprocess_courses(data):
    # Ensure the required column is present
    required_column = 'course_title'
    if required_column not in data.columns:
        st.error(f"Column '{required_column}' is missing in the dataset.")
        st.stop()  # Stop execution if the required column is missing
    
    # Use only the course title for analysis
    data['combined_text'] = data['course_title']
    return data

# Hardcoded dataset path
data_file = r"C:\Users\kmohi\Downloads\six-eyes-main\udemy_courses.csv"  # Update this path to your dataset location
df = pd.read_csv(data_file)

# Preprocess the dataset
df = preprocess_courses(df)

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    st.error("SpaCy model 'en_core_web_lg' not found. Please install it using `python -m spacy download en_core_web_lg`.")
    st.stop()

# Streamlit app
st.title("Course Recommender")
st.write("Enter a description of what you're looking for, and we'll suggest the best courses for you!")

# User input
user_input = st.text_area("What do you want to learn today?")

if st.button("Find Courses"):
    if user_input:
        # Process user input using SpaCy
        user_doc = nlp(user_input)

        # Calculate similarity scores with a progress bar
        st.write("Calculating similarity scores...")
        progress_bar = st.progress(0)
        similarity_scores = []
        for i, course_text in enumerate(df['combined_text']):
            course_doc = nlp(course_text)
            
            # Check if either document has no vectors
            if not user_doc.has_vector or not course_doc.has_vector:
                similarity_scores.append(0)  # Assign a similarity score of 0
            else:
                similarity_scores.append(user_doc.similarity(course_doc))
            
            progress_bar.progress((i + 1) / len(df))
        
        df['similarity'] = similarity_scores
        
        # Get top 5 recommendations
        top_courses = df.sort_values(by='similarity', ascending=False).head(5)

        st.subheader("Recommended Courses")
        for _, course in top_courses.iterrows():
            st.write(f"**{course['course_title']}**")
            st.write(f"URL: {course['url']}")
            st.write(f"Price: {course['price']} USD")
            st.write(f"Level: {course['level']}")
            st.write(f"Subject: {course['subject']}")
            st.write(f"Number of Lectures: {course['num_lectures']}")
            st.write(f"Content Duration: {course['content_duration']} hours")
            st.write("---")
    else:
        st.error("Please enter a description to find courses.")