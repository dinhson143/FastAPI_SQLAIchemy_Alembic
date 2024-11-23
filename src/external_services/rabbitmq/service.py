import pika

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
# Create a connection and channel when the application starts
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(
    queue="task_queue",
    durable=True,
    arguments={"x-max-priority": 10},  # Priority level from 0-10
)


def get_channel():
    """
    Provide a RabbitMQ channel to the endpoints without closing the connection
    """
    try:
        yield channel
    finally:
        # Do not close the connection here because the connection and channel need to live long-term
        pass
