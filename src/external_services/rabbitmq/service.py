import pika

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
# Tạo kết nối và kênh khi ứng dụng khởi động
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(
    queue="task_queue",
    durable=True,
    arguments={"x-max-priority": 10},  # Mức độ ưu tiên từ 0-10
)


def get_channel():
    """
    Cung cấp kênh RabbitMQ cho các endpoint mà không đóng kết nối
    """
    try:
        yield channel
    finally:
        # Không đóng kết nối ở đây vì kết nối và kênh cần sống lâu dài
        pass
