FROM python:3

# Copy only the flask app files
COPY skitunes/ .

# Install Python Requirements 
RUN pip install -r requirements.txt

# Run the app
CMD ["python3", "wsgi.py", "--hot=0.0.0.0"]