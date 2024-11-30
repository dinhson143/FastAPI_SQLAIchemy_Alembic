import pika

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
# Create a connection and channel when the application starts
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()
direct_is_set_up = False
topic_is_set_up = False
fanout_is_set_up = False


def setup_direct_exchange_rabbitmq(channel):
    """
    Set up exchanges, queues, and bindings for RabbitMQ.
    This function should be called once when the application starts.
    """
    global direct_is_set_up
    if direct_is_set_up:
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
    direct_is_set_up = True


def setup_topic_exchange_rabbitmq(channel):
    """
    Set up exchanges, queues, and bindings for RabbitMQ.
    This function should be called once when the application starts.
    """
    global topic_is_set_up
    if topic_is_set_up:
        return  # Skip if already setup
    # Declare a topic exchange
    channel.exchange_declare(
        exchange="topic_tasks_exchange",
        exchange_type="topic",
        durable=True,  # Exchange persists even if RabbitMQ restarts
    )

    # Declare a durable queue with priority
    channel.queue_declare(
        queue="topic_task_queue_1",
        durable=True,
        arguments={"x-max-priority": 10},  # Priority level from 0-10
    )

    # Bind the queue to the exchange with a specific routing key
    channel.queue_bind(
        exchange="topic_tasks_exchange",
        queue="topic_task_queue_1",
        routing_key="tasks.priority.*", # Matches routing keys like "tasks.priority.high"
    )
    topic_is_set_up = True


def setup_fanout_exchange_rabbitmq(channel):
    """
    Set up a fanout exchange and bind it to queues for RabbitMQ.
    This function should be called once when the application starts.
    """
    global fanout_is_set_up
    if fanout_is_set_up:
        return  # Skip if already setup

    # Declare a fanout exchange
    channel.exchange_declare(
        exchange="fanout_tasks_exchange",
        exchange_type="fanout",
        durable=True,  # Exchange persists even if RabbitMQ restarts
    )

    # Declare multiple durable queues
    channel.queue_declare(
        queue="fanout_task_queue_1",
        durable=True,
    )
    channel.queue_declare(
        queue="fanout_task_queue_2",
        durable=True,
    )

    # Bind the queues to the fanout exchange
    channel.queue_bind(
        exchange="fanout_tasks_exchange",
        queue="fanout_task_queue_1",
    )
    channel.queue_bind(
        exchange="fanout_tasks_exchange",
        queue="fanout_task_queue_2",
    )

    fanout_is_set_up = True


setup_direct_exchange_rabbitmq(channel)
setup_topic_exchange_rabbitmq(channel)
setup_fanout_exchange_rabbitmq(channel)


def get_channel():
    """
    Provide a RabbitMQ channel to the endpoints without closing the connection
    """
    try:
        yield channel
    finally:
        # Do not close the connection here because the connection and channel need to live long-term
        pass
