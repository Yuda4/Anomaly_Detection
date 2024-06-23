import json
import os
import random
import sys
from utils.database import database_utils
from utils.queue.queue_utils import connect_queue, send_response

rabbitmq_host = os.environ['RABBITMQ_HOST']
queue_name = os.environ['RABBITMQ_QUEUE_NAME']


# Processes incoming messages, checks if an event exists in the database, detects anomalies & inserts anomalies to DB.
def anomaly_detection(ch, method, properties, body):
    event_data = json.loads(body)
    event_id = event_data['EventID']

    try:
        # Checking if event is already exists by event_id in database and return the anomaly in case it does exists
        anomaly_score = database_utils.check_event_exists(event_id)
        if anomaly_score is not None:
            response_msg = f"Event {event_id} already processed with anomaly score {anomaly_score}."
            print(response_msg)
            sys.stdout.flush()
            send_response(ch, method, properties, 200, response_msg)
            return

        # Calculate anomaly and insert record in case anomaly is greater than 0
        anomaly_score = random.random()
        if anomaly_score > 0:
            try:
                database_utils.insert_anomaly(event_data, anomaly_score)
            except Exception as e:
                err = f"Failed to insert event into the database: {e}"
                send_response(ch, method, properties, 500, err)
            response_msg = f"Anomaly detected: {anomaly_score} for event {event_id}"
            print(response_msg)
            sys.stdout.flush()
            send_response(ch, method, properties, 201, response_msg)
        else:
            response_msg = f"No anomaly detected for event {event_id}"
            print(response_msg)
            sys.stdout.flush()
            send_response(ch, method, properties, 204, response_msg)
    except Exception as e:
        print(f"Failed to process event: {e}")
        # Optionally, you can reject and requeue the message if processing fails
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


# Sets up RabbitMQ connection, consumes messages from the queue, and starts message processing
def main():
    channel = connect_queue(rabbitmq_host, queue_name)
    # Sets up a consumer to listen to queue and process messages using a callback function
    channel.basic_consume(queue=queue_name, on_message_callback=anomaly_detection, auto_ack=True)
    # Starts the loop that consumes messages and delivers them to the callback function
    # channel.start_consuming()
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        channel.connection.close()


if __name__ == '__main__':
    main()
