from kafka import KafkaProducer, KafkaConsumer
import json

KAFKA_TOPIC = 'blockchain1'
KAFKA_SERVER = '127.0.0.1:9092'

producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_SERVER, value_deserializer=lambda m: json.loads(m.decode('utf-8')))