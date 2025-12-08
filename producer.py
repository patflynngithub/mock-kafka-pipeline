from kafka import KafkaProducer
import json

# Create a Kafka Producer instance
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # Replace with your Kafka broker address
    value_serializer=lambda v: json.dumps(v).encode('utf-8') # Serialize messages to JSON bytes
)

# Send a message to a topic
topic_name = 'my_python_topic'
message_data = {'id': 1, 'name': 'example_message'}
producer.send(topic_name, message_data)

# Flush messages to ensure delivery
producer.flush()
print(f"Message sent to topic '{topic_name}': {message_data}")
