FROM apache/kafka:4.1.1
WORKDIR /pipeline

# Install the application dependencies
USER root
RUN apk add python3 && \
    apk add py3-pip && \
    pip install kafka-python --break-system-packages

# Copy in the source code
COPY producer.py consumer.py ./
EXPOSE 9092


