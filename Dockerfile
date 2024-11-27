FROM python:3
COPY . .
RUN pip install -r requirements.txt
WORKDIR /skitunes
CMD ["python3", "wsgi.py", "--hot=0.0.0.0"]