FROM python:3
COPY skitunes/ .
RUN pip install -r requirements.txt
CMD ["python3", "wsgi.py", "--hot=0.0.0.0"]