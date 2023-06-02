FROM python:3
COPY . .
RUN pip install -r requirements.txt
WORKDIR /skitunes
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]