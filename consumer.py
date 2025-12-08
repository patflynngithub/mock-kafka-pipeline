from kafka import KafkaConsumer
import json

# Create a Kafka Consumer instance
consumer = KafkaConsumer(
    'my_python_topic',  # Topic to consume from
    group_id='my_consumer_group', # Consumer group for offset management
    bootstrap_servers=['localhost:9092'], # Replace with your Kafka broker address
    auto_offset_reset='earliest', # Start consuming from the beginning if no offset is found
    enable_auto_commit=True, # Automatically commit offsets
    value_deserializer=lambda v: json.loads(v.decode('utf-8')) # Deserialize messages from JSON bytes
)

print("Starting consumer...")
for message in consumer:
    print(f"Received message: Topic={message.topic}, Partition={message.partition}, Offset={message.offset}, Key={message.key}, Value={message.value}")
