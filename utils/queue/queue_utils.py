import pika
import time
import sys
import uuid
import json


#  Establish connection to RabbitMQ and returns a channel for queue operations.
def connect_queue(rabbitmq_host, queue_name):
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, heartbeat=5400))
            channel = connection.channel()
            channel.queue_declare(queue=queue_name)
            break
        except pika.exceptions.AMQPConnectionError:
            print("Getting RabbitMQ connection up and running...")
            sys.stdout.flush()
            time.sleep(5)

    return channel


# Establish channel to RabbitMQ for publishing messages & handling responses
def connect_channel(rabbitmq_host):
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, heartbeat=5400))
            channel = connection.channel()
            break
        except pika.exceptions.AMQPConnectionError:
            print("Getting RabbitMQ channel up and running...")
            sys.stdout.flush()
            time.sleep(5)

    return channel


# Making sure each event sent to the anomaly worker can be uniquely identified (correlation_id)
# and that the response to the event can be properly matched and handled.
# Publish a message to a RabbitMQ queue -
#   routing_key - directing the message to this specific queue
#   properties:
#       reply_to - specifies the queue where the anomaly worker should send the response to
#       correlation_id - correlation ID to link the request and the response
def publish_event(channel, event, publish_queue_name, response_queue_name):
    correlation_id = str(uuid.uuid4())
    channel.basic_publish(
        exchange='',
        routing_key=publish_queue_name,
        properties=pika.BasicProperties(reply_to=response_queue_name, correlation_id=correlation_id),
        body=json.dumps(event)
    )
    return correlation_id


# Publish a response message to a specified reply queue based on reply_to and correlation_id in the response properties.
def send_response(ch, method, properties, status_code, response_msg):
    response = {'status_code': status_code, 'response_msg': response_msg}
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response)
    )

