import streamlit as st
import pandas as pd
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load the Excel file
data_path = 'datatable.xlsx'
data = pd.read_excel(data_path)

# Streamlit UI
st.title("Course List")
st.write("Explore the available courses with their details below:")

# User input for filtering
query = st.text_input("Enter keywords to filter courses (e.g., 'Python for Data Science')", "")

# Function to extract keywords using spaCy
def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
    return keywords

# Filter courses based on keywords
filtered_data = data
if query:
    keywords = extract_keywords(query)
    st.write(f"Filtering courses with keywords: {', '.join(keywords)}")

    # Filter rows where any keyword matches in Col1 (Course Name) or Col4 (Description)
    filtered_data = data[
        data['Col1'].str.contains('|'.join(keywords), case=False, na=False) |
        data['Col4'].str.contains('|'.join(keywords), case=False, na=False)
    ]

# Limit the number of courses to 50
filtered_data = filtered_data.head(50)

# Iterate through the filtered rows and create course cards
if not filtered_data.empty:
    for _, row in filtered_data.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            # Display course image
            with col1:
                st.image(
                    row['Col6_SRC'],
                    caption=row['Col1'],
                    use_container_width=True,
                )

            # Display course details
            with col2:
                st.markdown(f"### {row['Col1']}")
                st.markdown(f"**Duration:** {row['Col0']}")
                st.markdown(f"**Rating:** {row['Col2']} ⭐")
                st.markdown(f"**Learners:** {row['Col3']}")

                # Display CTA link
                st.markdown(f"[Know more]({row['Col5_HREF']})")
                
            st.markdown("---")
else:
    st.write("No courses found for the given query.")
