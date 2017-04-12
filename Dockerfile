FROM tiangolo/uwsgi-nginx-flask:flask-python3.5

# Add app configuration to Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Copy sample app
COPY ./app /app

WORKDIR /app
EXPOSE 5000:5000

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
RUN echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.4 main" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list
RUN apt-get update && apt-get install -y mongodb-org
RUN mkdir -p /data/db
#RUN mongod &
#CMD ["mongod &"]
RUN pip install -r requirements.txt