import streamlit as st
import boto3
import csv
import uuid
from datetime import datetime

# Connect to S3
s3 = boto3.client('s3', aws_access_key_id='<your_access_key>', aws_secret_access_key='<your_secret_key>')

# Define the S3 bucket where the survey responses will be stored
bucket_name = '<your_bucket_name>'

# Define a function to create the CSV filename based on the survey name and current date/time
def create_csv_filename(survey_name):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f'{survey_name}-{timestamp}-{unique_id}.csv'

# Define the survey questions and input fields
survey_name = 'My Survey'
q1 = st.text_input('What is your name?')
q2 = st.selectbox('What is your favorite color?', ['Red', 'Green', 'Blue'])
q3 = st.slider('How many hours do you work in a day?', min_value=0, max_value=24)

# Add a section for additional comments
st.subheader('Additional Comments')
num_comments = st.number_input('How many additional comments do you have?', min_value=0, max_value=10, step=1)
comments = []
for i in range(num_comments):
    comments.append(st.text_input(f'Comment {i+1}'))

# Add a submit button to submit the survey
submit_button = st.button('Submit')

# Process the survey when the submit button is clicked
if submit_button:
    # Create the CSV filename for this survey
    csv_file_name = create_csv_filename(survey_name)
    
    # Store the survey responses in a CSV file in S3
    response = [q1, q2, q3] + comments
    try:
        # Check if the CSV file already exists in S3
        s3.head_object(Bucket=bucket_name, Key=csv_file_name)
    except:
        # If the CSV file doesn't exist, create a new file with a header row
        header = ['ID', 'Name', 'Favorite Color', 'Hours Worked'] + [f'Comment {i+1}' for i in range(num_comments)]
        with open('temp.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        s3.upload_file('temp.csv', bucket_name, csv_file_name)
    
    # Append the survey response to the CSV file
    with open('temp.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        unique_id = str(uuid.uuid4())[:8]
        response.insert(0, unique_id)
        writer.writerow(response)
    s3.upload_file('temp.csv', bucket_name, csv_file_name)

    # Display a confirmation message to the user
    st.write(f'Thank you for taking the survey, {q1}! Your responses have been saved.')
    st.write(f'Your unique ID is {unique_id}. Please keep this ID safe as it will allow you to retrieve your survey response later.')
