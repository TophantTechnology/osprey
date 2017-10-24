FROM mappies/centos7-python3.5

WORKDIR /opt/osprey
COPY . .

RUN pip3.5 install -r web/requirements.txt \ 
      -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com && \
    ln -s /usr/local/bin/python3.5 /usr/local/bin/python3 && \
    sed -i -e 's/amqp:\/\/.*/amqp:\/\/osprey:osprey@rabbitmq"/' \
      -e 's/mongodb:\/\/.*/mongodb:\/\/mongo\/"/' \
      -e 's/use_mongo = .*/use_mongo = True/' \
      -e 's/use_sqlite = .*/use_sqlite = False/' settings.py

CMD ["docker/start-osprey.sh"]