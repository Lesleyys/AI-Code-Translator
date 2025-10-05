import base64
import streamlit as st
import os
import zipfile
import tempfile
import urllib.request
import pandas as pd
import shutil 

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

from google.cloud import storage

PROJECT_ID = "your_project_id" # # Replace by your own project id
vertexai.init(project=PROJECT_ID, location="your_location") # Replace by your own GCP location

model = GenerativeModel("gemini-2.5-pro")  # Replace by your own Vertex AI LLM Model

chat_session = model.start_chat()

# code generator
def code_generator(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

# optimzations function
def optimizations_generator(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

# test generator
def test_generator(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

# testscript generator
def testscript_generator(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

def create_zipfile(new_code, new_optimizations, new_test, new_testscript, code_name, test_name):
    # Create a temporary directory to hold files
    temp_dir = tempfile.mkdtemp()

    # Define the filename for the zip archive with .zip extension
    zip_filename = f"{os.path.splitext(code_name)[0]}.zip"  # Extracts the filename without extension
    zip_path = os.path.join(temp_dir, zip_filename)  # Full path to the zip file

    # Concatenate code, optimizations, tests, and test scripts into a single file content
    combined_content = f"{new_code}\n\n"
    if new_optimizations:
        combined_content += f"Optimizations:\n{new_optimizations}\n\n"
    if new_test:
        combined_content += f"Tests:\n{new_test}\n\n"
    if new_testscript:
        combined_content += f"Test Scripts:\n{new_testscript}\n\n"

    # Specify the exact path of the text file to include in the zip archive
    code_file_path = os.path.join(temp_dir, code_name)
    
    # Ensure `code_file_path` points to a file, not a directory
    if not os.path.splitext(code_file_path)[1]:  # Adds a default extension if none
        code_file_path += ".txt"

    with open(code_file_path, "w") as file:
        file.write(combined_content)

    # Create the zip archive and add the text file to it
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(code_file_path, arcname=code_name)  # Add the file with a specific name

    # Provide a download link for the zip file
    st.markdown(get_download_link(zip_path, zip_filename), unsafe_allow_html=True)

    # Clean up: remove the temporary directory after zipping
    shutil.rmtree(temp_dir)

def get_download_link(file_path, file_name):
    # Generate a download link for the zip file
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    b64_data = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:application/zip;base64,{b64_data}" download="{file_name}">Download {file_name}</a>'
    return href

# save file into GCP bucket
def save_file_into_gcpbucket(bucket_name, new_code, new_optimizations, new_test, new_testscript, file_text, opt_name, test_name, script_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob1 = bucket.blob(file_text)
    blob2 = bucket.blob(opt_name)
    blob3 = bucket.blob(test_name)
    blob4 = bucket.blob(script_name)

    with blob1.open("w") as f:
        f.write(str(new_code))

    with blob1.open("r") as f:
        print(f.read())

    if new_optimizations:
        with blob2.open("w") as f:
            f.write(str(new_optimizations))

        with blob2.open("r") as f:
            print(f.read())

    if new_test:
        with blob3.open("w") as f:
            f.write(str(new_test))

        with blob3.open("r") as f:
            print(f.read())

        with blob4.open("w") as f:
            f.write(str(new_testscript))

        with blob4.open("r") as f:
            print(f.read())

    st.write("Files uploaded to GCP bucket successfully.")

#save file function
def save_code_to_file(code, filename):
    with open(filename, 'w') as file:
        file.write(code)

#state of the download button so it appears after pressing preview
st.session_state.disabled=True

#GitHub file reader function
def gitreader(url):
    response = urllib.request.urlopen(url)
    data = response.readlines()

def main():
    st.title("AI Code Translator") 

    uploaded_file = None
    github_link = ""
    new_code = None
    new_optimizations = None
    uploaded_testscript = None
    run_button = False
    script = None
    new_test = None
    new_testscript = None

    st.sidebar.image("vertex_ai.png", width=200)
    st.sidebar.write("Please select what features you would like:")

    st.sidebar.subheader("Code Translation",divider='rainbow')
    file = st.sidebar.checkbox("Upload your code file",value= True)
    git = st.sidebar.checkbox("Browse file via GitHub file link",help = "Please input the raw link here not permalink")
    st.sidebar.subheader("Code Optimization",divider='rainbow')
    optimisation = st.sidebar.checkbox("Code Optimization Suggestions")

    st.sidebar.subheader("Test Case Generator",divider='rainbow')
    tests = st.sidebar.checkbox("Create Test Cases")

    if file:
        uploaded_file = st.file_uploader("Upload your code file:")
    
    if git:
        github_link = st.text_input("Enter your raw GitHub file link:", "" , key = "fileLink", help = "Please input the raw link here not permalink")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        source_text = st.text_input("Source language:", "", key="sourceInput")
    with col2:
        target_text = st.text_input("Target language:", "", key="targetInput")
    with col3:
        file_text = st.text_input("Target File Name:", "", key="fileInput", help="Include file extension")

    test_name = "test_" + file_text
    opt_name = "opt_" + file_text

    basic_prompt = """Add all non code items to the top as comments along with explanation of the code. """
    task = 'write an efficient code by following the coding best practices'
    file_name = f"File Name:{file_text}"
    source_language = f"Source Language: {source_text}"
    target_language = f"Target Language:{target_text}"

    if tests:
        uploaded_testscript = st.file_uploader("Upload your sample test script file:")
        num_tests = st.sidebar.number_input("Enter a number for the amount of test scripts you wish to generate:", step=1)
    
    st.sidebar.subheader("Download & Upload output files",divider='rainbow')
    zipfile = st.sidebar.checkbox("Download output as a Zipfile")
    gcp_download = st.sidebar.checkbox("Upload output into the GCP bucket")

    if gcp_download:
        bucket_name = st.sidebar.text_input("Bucket Name:", "", key="bucketInput")

    run_button = st.sidebar.button("Run Program")
    if uploaded_file is not None:
        bytes_data = uploaded_file.readlines()
        legacy_code = [line.decode().strip() for line in bytes_data]
        st.write(legacy_code)
    elif len(github_link) > 0:
        url = github_link
        code = gitreader(url)
        legacy_code = [line.decode().strip() for line in code]
        st.write(legacy_code) 

    if uploaded_testscript is not None:
        script = pd.read_excel(uploaded_testscript, header=0)
        st.write(script)

    if run_button:
        with st.spinner('Generating...'):
            prompt1 = f"Here is the source language: {source_language}. Here is target language: {target_language}. Here is the {source_language} code: {legacy_code}. You need to convert {source_language} code to highly efficient {target_language} code. {basic_prompt}. Second, Here is the {source_language} code: {legacy_code}, complete the task {task} and make sure the {target_language} code generated has the same function as the {source_language} code: {legacy_code}. If the {target_language} is java, please pay attention that the class name should be the same as {file_name}"
            new_code = code_generator(chat_session, prompt1) 
            # if translation:
            st.code(new_code)  
            if optimisation:
                prompt2 = f"#suggest optimzations for below code as comments. Do not write code.\n {new_code}"
                new_optimizations = optimizations_generator(chat_session, prompt2)
                st.code(new_optimizations)
            if tests:
                prompt3 = f"""Create {num_tests} unit tests to verify:\n{new_code} \n has all same functionality as \n{legacy_code} and return the results in table format with the test name as key and pass or fail as value.  Do not create any more or any less tests than the number provided. Please also show the test scripts (code) you used to make the verification for me to replicate. Use the necessary imports needed. The name of the new code file is {file} so import the function from the new code file and create the tests for a new file. If you cannot test or create tests then return `There are no tests to apply`."""
                new_test = test_generator(chat_session,prompt3)
                st.code(new_test)
                prompt4 = f"""Create {num_tests} User Acceptance Testing (UAT) scripts step by step for manual testing with following 4 requirements:
                    1. Provide specific description of how to do the test (E.g., Enter which number, click which button)
                    2. State the expected results. 
                    3. Do not create any more or any less tests than the number provided.
                    4. Do the mannual UAT test automatically and provide test output and the test result Pass/Fail. 
                    Legacy code is {legacy_code}, new code is {new_code}.
                    The name of the new code file is {file}. 
                    Please refer the \n {script} \n as the test script template. If you cannot test script then return `There are no test script to apply`.
                    The output should be in completely correct JSON format. 
                    Do this step by step. Only return the test cases and not any code.
                    You will always return the output with the following JSON schema. This should be done for every single one of the tests:
                        "test_id:"","
                        "category:"","
                        "description:"","
                        "steps:"","
                        "expected_result:"","
                        "test_output:"","
                        "result:"","
                    """
                new_testscript = testscript_generator(chat_session,prompt4)
                st.code(new_testscript)
            if zipfile:
                create_zipfile(new_code, new_optimizations, new_test, new_testscript, file_text, test_name)
            if gcp_download:
                script_name = "script_" + file_text
                save_file_into_gcpbucket(bucket_name, new_code, new_optimizations, new_test, new_testscript, file_text, opt_name, test_name, script_name)
        st.session_state.disabled = False

if __name__ == "__main__":
    main()

