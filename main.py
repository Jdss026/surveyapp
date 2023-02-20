import streamlit as st
import boto3
import csv
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment keys
load_dotenv()
import os

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")


# Connect to S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Define the S3 bucket where the survey responses will be stored
bucket_name = 'surveyappproject-bucket'

# Define a function to create the CSV filename based on the survey name and current date/time
def create_csv_filename(survey_name):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    global unique_id
    unique_id = str(uuid.uuid4())[:8]
    return f'{survey_name}-{timestamp}-{unique_id}.csv'

# Define the survey questions and input fields
survey_name = 'Questionário'
q1 = st.text_input('Qual seu nome?')
q2 = st.selectbox('Qual sua cor favorita?', ['Vermelho', 'Verde', 'Azul'])
q3 = st.slider('Quantas horas você trabalha por dia?', min_value=0, max_value=24)

# Add a section for additional comments
st.subheader('Comentários Adicionais')
num_comments = st.number_input('Quantos comentários adicionais você têm?', min_value=0, max_value=10, step=1)
comments = []
for i in range(num_comments):
    comments.append(st.text_input(f'Comentário {i+1}'))

# Add a submit button to submit the survey
submit_button = st.button('Enviar')

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
        # unique_id = str(uuid.uuid4())[:8]
        response.insert(0, unique_id)
        writer.writerow(response)
    s3.upload_file('temp.csv', bucket_name, csv_file_name)

    # Display a confirmation message to the user
    st.write(f'Thank you for taking the survey, {q1}! Your responses have been saved.')
    st.write(f'Your unique ID is {unique_id}. Please keep this ID safe as it will allow you to retrieve your survey response later.')
