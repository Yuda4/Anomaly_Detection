## Anomaly Detection Project
***
In this project I've created a system that receives Cloudtrail events and assesses them for
anomalies by implementing workers that consumes messages from a RabbitMQ queue, processes them, and sends back responses. The worker is designed to handle database operations using SQLAlchemy and ensures proper acknowledgment of messages to avoid processing errors and data inconsistencies. The Flask framework is used for building the web application.

The system having the following high level architecture:

Cloudtrail Producer ~~->~~ Ingestion Service ~~->~~ Queue ~~->~~ Anomaly Workers ~~->~~ DB. 

Here are detailed instructions and prerequisites for setting up and running this project.

## Prerequisites
***
1. **Docker and Docker Compose**: Ensure you have Docker and Docker Compose installed on your machine.
   - [Install Docker](https://docs.docker.com/engine/install/)
   - [Install Docker Compose](https://docs.docker.com/compose/install/)

    Alternatively you can Install [Docker Desktop](https://docs.docker.com/desktop/) which include both.


2. **Python 3.9+**: Ensure you have Python 3.9 or newer installed if you plan to run parts of the project outside of Docker.
   - [Install Python](https://www.python.org/downloads/)

## Project Structure
***
~~~
project-root/
│
├── anomaly_worker/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── worker.py
├── app/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   └── init.sql
├── utils/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database_utils.py
│   │   └── init.sql
│   ├── queue/
│   │   ├── __init__.py
│   │   └── queue_utils.py
└── docker-compose.yml
└── README.md
~~~
## Setup Instructions
***
`git clone https://github.com/Yuda4/Anomaly_Detection.git`

`cd Anomaly_Detection`

## Running the Project
***
1. Build and Start the Services:
    - Open a terminal on project-root location
    - Run the build command: `docker-compose up --build`
    - Want to delete the container with all data? Run this command: `docker-compose down -v`
    - Want to stop the running of container? `docker-compose stop` or press `Ctrl-C`
2. Ingest Endpoint: Send a POST request to /ingest endpoint to add an event.
   After docker is running and all services are up run this CURL in terminal or using Postman:
      ~~~~
      curl -X POST http://localhost:5000/ingest -H "Content-Type: application/json" -d '{
      "RequestID": "8f884d95-b266-4018-8767-c4a79ecee7a6",
      "EventID": "8f884d95-b266-4018-8767-c4a79ecee7a6",
      "RoleID": "role12",
      "EventType": "type1",
      "EventTimestamp": "2023-06-23T16:23:18Z",
      "AffectedAssets": ["asset1", "asset2"]
      }'
      ~~~~
3. Logs & monitoring:
    
    Docker's logs:
    ~~~~
    1. docker-compose logs app
    2. docker-compose logs anomaly_worker
    3. docker-compose logs rabbitmq
    4. docker-compose logs db
    ~~~~
   In order to obtain docker's container name use this command:

   `docker ps`
    
    Under `NAMES` column you will find the desired container name for app, anomaly worker, DB & rabbitMQ.


4. Connecting to DB:
   
    Open terminal and use this command:
   
    `docker exec -it anomaly_detection-db-1 psql -U user -d cloudtrail` which will connect to DB named cloudtrail that is hosted in `anomaly_detection-db-1` docker container.

    `\l` - List all databases.
   
    `\dt` - List database tables.
   
    `\d <table-name>` - Describe a table.

    `SELECT * FROM anomalies;` - shows **anomalies** table's records.
   

5. Connecting to Queue:

   Open a browser and enter this URL: `http://localhost:15672/` with `guest` as Username & Password.
   
    It will open a dashboard of an overview on:
   - Queues
   - Connections
   - Channels
   - Sockets published, delivered
   - etc.

##Project Overview
***
####/anomaly_worker/worker.py
Establishing RabbitMQ connection & listens to a RabbitMQ queue, `cloudtrail_events`, for incoming events, performs anomaly detection, querying with the database & sends responses based on the anomaly detection outcome.

####/app/app.py
A Flask application that exposes an endpoint `/ingest` for receiving events, validates required keys, publishing them to a RabbitMQ queue - `cloudtrail_events`, handling & return responses from worker.py.

####utils/database/database_utils.py
Manages database connections, SQLAlchemy engine with connection pooling, session handling and database operations - `check_event_exists`, `insert_anomaly`.

####utils/database/init.sql
Initializes the `anomalies` table schema in PostgreSQL.

####utils/queue/queue_utils.py
Provides utilities to manage RabbitMQ connections queue & channel, publish messages - `publish_event`, and handle responses - `send_response`.

***
####Why use Flask?

Flask's simplicity, flexibility, and vibrant ecosystem make it an ideal choice for web development. Because Flask applications are lightweight, they remain fast and efficient, making them suitable for both small-scale projects and large, complex applications.

With Flask, developers can integrate additional functionality such as routing, templating, and session management seamlessly, while extensions and libraries such as Flask-SQLAlchemy, Flask-RESTful, and Flask-JWT make it easy to add new functionalities. As a result of its flexibility, Flask can be used to build APIs, web services, and even full-stack web applications.
***
####Why use RabbitMQ?
RabbitMQ stands out as a top choice for message queuing because of its reliability, flexibility, and rich features, making it perfect for managing communication in microservices and distributed systems.
Key features include high-throughput and low-latency messaging, message durability, and delivery guarantees, ensuring reliability even in system failures.
***
####Why use SQLAlchemy?
SQLAlchemy is a powerful and flexible SQL toolkit and Object-Relational Mapping (ORM) library for Python.

Easy to Use: SQLAlchemy provides a higher-level API for interacting with databases, making it easier to write and maintain database queries.

Connection Pooling: It includes built-in support for connection pooling, which helps manage database connections efficiently.

ORM Capabilities: The ORM allows you to work with Python objects and classes instead of writing raw SQL, which can make the code more readable and maintainable.

Flexibility: SQLAlchemy allows for the use of raw SQL when needed, giving you the flexibility to write custom queries.
***


####Choices and Considerations
- Automatic Acknowledgment: Simplifies message handling by automatically acknowledging messages upon receipt.
- SQLAlchemy ORM: Provides an efficient and maintainable way to interact with the database, abstracting away raw SQL operations.
- Session Management: Ensures that database sessions are properly managed and closed.
- Correlation ID: Used to correlate responses with the original requests, ensuring accurate communication between components.
- Flask Integration: Allows for easy handling of HTTP requests and responses, integrating seamlessly with the message processing workflow.
- Graceful Shutdown: Ensures that the worker can be stopped gracefully, avoiding abrupt terminations that might lead to message loss or corruption.
- Separation of Concerns: Different functions handle different responsibilities (e.g., callback for processing, send_response for sending responses), promoting clean and maintainable code.

By following these practices and considerations, the solution ensures efficient message processing, robust error handling, and maintainable code architecture.
