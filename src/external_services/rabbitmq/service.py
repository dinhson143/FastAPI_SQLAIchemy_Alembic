import pika

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
# Create a connection and channel when the application starts
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()
is_set_up = False


def setup_direct_exchange_rabbitmq(channel):
    """
    Set up exchanges, queues, and bindings for RabbitMQ.
    This function should be called once when the application starts.
    """
    global is_set_up
    if is_set_up:
        return  # Skip if already setup
    # Declare a direct exchange
    channel.exchange_declare(
        exchange="direct_tasks_exchange",
        exchange_type="direct",
        durable=True,  # Exchange persists even if RabbitMQ restarts
    )

    # Declare a durable queue with priority
    channel.queue_declare(
        queue="direct_task_queue_1",
        durable=True,
        arguments={"x-max-priority": 10},  # Priority level from 0-10
    )

    # Bind the queue to the exchange with a specific routing key
    channel.queue_bind(
        exchange="direct_tasks_exchange",
        queue="direct_task_queue_1",
        routing_key="direct_task_queue_1_routing_key",
    )
    is_set_up = True


setup_direct_exchange_rabbitmq(channel)


def get_channel():
    """
    Provide a RabbitMQ channel to the endpoints without closing the connection
    """
    try:
        yield channel
    finally:
        # Do not close the connection here because the connection and channel need to live long-term
        pass
