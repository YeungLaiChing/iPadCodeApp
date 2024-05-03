#The Flask application container will use python:3.10-alpine as the base image
FROM python:3.10.12

#This command will create the working directory for our Python Flask application Docker image
WORKDIR /code

#This command will copy the dependancies and libaries in the requirements.txt to the working directory
COPY requirements.txt /code

#This command will install the dependencies in the requirements.txt to the Docker image
RUN pip install -r requirements.txt --no-cache-dir

#This command will copy the files and source code required to run the application
COPY . /code

#This command will start the Python Flask application Docker container
CMD python app.py config.json
