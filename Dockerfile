# # Use a Python base image
# FROM python:3.9-slim-buster

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements file and install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Install Playwright and its browsers
# RUN pip install playwright
# RUN playwright install chromium

# # Copy the Streamlit app file
# COPY *.py .

# # Expose the Streamlit port
# EXPOSE 8501

# # Run the Streamlit app
# CMD ["streamlit", "run", "game.py"] #replace your_script_name.py


FROM python:3.9-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 1 
RUN pip install playwright
RUN playwright install chromium
RUN playwright install --with-deps 
RUN playwright browsers #add this line to check install
COPY *.py .
EXPOSE 8501
CMD ["streamlit", "run", "game.py"]
