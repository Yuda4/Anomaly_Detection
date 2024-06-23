from flask import Flask, request, jsonify
import json
import os
from utils.queue.queue_utils import connect_channel, publish_event
import logging


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rabbitmq_host = os.environ['RABBITMQ_HOST']
publish_queue_name = os.environ['RABBITMQ_QUEUE_NAME']
response_queue_name = os.environ['RABBITMQ_RESPONSE_QUEUE_NAME']

channel = connect_channel(rabbitmq_host)

channel.queue_declare(publish_queue_name)
channel.queue_declare(response_queue_name)

current_correlation_id = None


# Callback function to handle responses received from worker via RabbitMQ
def on_response(ch, method, props, body):
    global response
    if props.correlation_id == current_correlation_id:
        response = json.loads(body)
        logger.info(f"Response received: {response}")
        channel.stop_consuming()


# Receives POST requests with event data, validates required keys, publishes events to publish queue,
# and waits for responses from response queue.
@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    required_keys = ['RequestID', 'EventID', 'RoleID', 'EventType', 'EventTimestamp', 'AffectedAssets']

    if not all(key in data for key in required_keys):
        return jsonify({"error": "Invalid data"}), 400

    global current_correlation_id
    try:
        current_correlation_id = publish_event(channel, data, publish_queue_name, response_queue_name)
    except Exception as e:
        err_msg = f"Failed to publish event: {e}"
        return jsonify({"error": err_msg}), 500
    # Sets up a consumer to listen to queue and process messages using a callback function
    channel.basic_consume(queue=response_queue_name, on_message_callback=on_response, auto_ack=True)
    # Starts the loop that consumes messages and delivers them to the callback function
    channel.start_consuming()
    return jsonify(response)


# A Flask application that exposes an endpoint (/ingest) for receiving events,
# publishing them to a RabbitMQ queue, and handling responses of anomalies of event data.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

