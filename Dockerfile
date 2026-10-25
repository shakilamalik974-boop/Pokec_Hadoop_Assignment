FROM apache/hadoop:3 AS hadoop

FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jre-headless procps sudo && \
    rm -rf /var/lib/apt/lists/*

COPY --from=hadoop /opt/hadoop /opt/hadoop
COPY --from=hadoop /usr/local/bin/dumb-init /usr/local/bin/dumb-init
COPY --from=hadoop /opt/starter.sh /opt/starter.sh
COPY --from=hadoop /opt/envtoconf.py /opt/envtoconf.py
RUN mkdir -p /data

ENV HADOOP_HOME=/opt/hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="/opt/hadoop/bin:/opt/hadoop/sbin:/usr/lib/jvm/java-21-openjdk-amd64/bin:${PATH}"

ENTRYPOINT ["/usr/local/bin/dumb-init", "--", "/opt/starter.sh"]

RUN python3 --version && java -version && hadoop version