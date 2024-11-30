import asyncio
import time
from typing import List

import pika
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pika.adapters.blocking_connection import BlockingChannel
from starlette import status

from src.external_services.rabbitmq.service import get_channel
from src.models.rabbitmq_queue_models import TaskRequest

router = APIRouter()
processed_tasks: List[str] = []
task_processed_event = asyncio.Event()
total_tasks_to_process = 0


# Direct Exchange
@router.post("/direct/tasks/", status_code=status.HTTP_201_CREATED, tags=["RabbitMQ"])
async def add_task(task: TaskRequest, channel: BlockingChannel = Depends(get_channel)):
    if not (1 <= task.priority <= 10):
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 10.")

    # Connect to RabbitMQ and send the message to default exchange
    channel.basic_publish(
        exchange="direct_tasks_exchange",
        routing_key="direct_task_queue_1_routing_key",
        body=task.task_name,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent message
            priority=task.priority,  # Set priority level
        ),
    )
    return {"message": "Task added to queue", "task": task.task_name, "priority": task.priority}


# Topic Exchange
@router.post("/topic/tasks/", status_code=status.HTTP_201_CREATED, tags=["RabbitMQ"])
async def add_task(task: TaskRequest, channel: BlockingChannel = Depends(get_channel)):
    """
    Add a task to RabbitMQ using topic exchange.
    """
    if not (1 <= task.priority <= 10):
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 10.")

    # Define the routing key dynamically based on task attributes
    routing_key = f"tasks.priority.{task.priority}"  # Example: "tasks.priority.5"

    # Publish the task to the topic exchange
    channel.basic_publish(
        exchange="topic_tasks_exchange",  # Use topic exchange
        routing_key=routing_key,          # Routing key based on priority
        body=task.task_name,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent message
            priority=task.priority,  # Set priority level
        ),
    )
    return {
        "message": "Task added to topic queue",
        "task": task.task_name,
        "priority": task.priority,
        "routing_key": routing_key,
    }


# Fanout Exchange
@router.post("/fanout/tasks/", status_code=status.HTTP_201_CREATED, tags=["RabbitMQ"])
async def add_task(task: TaskRequest, channel: BlockingChannel = Depends(get_channel)):
    """
    Add a task to RabbitMQ using fanout exchange.
    """
    if not (1 <= task.priority <= 10):
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 10.")

    # Publish the task to the fanout exchange
    channel.basic_publish(
        exchange="fanout_tasks_exchange",  # Use fanout exchange
        routing_key="",                    # No routing key for fanout
        body=task.task_name,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent message
            priority=task.priority,  # Set priority level (if supported)
        ),
    )
    return {
        "message": "Task added to all queues in fanout exchange",
        "task": task.task_name,
        "priority": task.priority,
    }


@router.get("/tasks/", tags=["RabbitMQ"])
async def get_tasks(queue_name: str, channel: BlockingChannel = Depends(get_channel)):
    """
    Consume tasks from RabbitMQ and return a list of processed tasks along with processing time.
    """
    processed_tasks = []  # Khởi tạo danh sách các task đã xử lý

    # Lấy số lượng task từ hàng đợi
    total_tasks_to_process = get_task_queue_size(channel, queue_name)
    print(f"Expecting to process {total_tasks_to_process} tasks.")

    start_time = time.time()  # Ghi lại thời gian bắt đầu

    # Cấu hình QoS để nhận 1 tin nhắn tại 1 thời điểm
    channel.basic_qos(prefetch_count=1)

    # Bắt đầu xử lý các task
    print("Start consuming tasks...")
    while total_tasks_to_process > 0:
        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=False)
        if method_frame:
            task_name = body.decode()
            print(f"Processing task: {task_name} (Priority: {header_frame.priority})")
            time.sleep(2)  # Giả lập thời gian xử lý
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)  # Xác nhận tin nhắn đã xử lý
            processed_tasks.append(task_name)

            # Cập nhật số lượng task còn lại trong hàng đợi
            total_tasks_to_process = get_task_queue_size(channel, queue_name)
            print(f"Remaining tasks in queue: {total_tasks_to_process}")
        else:
            await asyncio.sleep(1)  # Đợi thêm nếu không có tin nhắn mới

    end_time = time.time()  # Ghi lại thời gian kết thúc
    time_consumed = end_time - start_time  # Tính toán thời gian đã xử lý

    return {
        "message": "All tasks processed",
        "processed_tasks": processed_tasks,
        "time_consumed": time_consumed,
        "total_tasks": len(processed_tasks),
    }


def get_task_queue_size(channel: BlockingChannel, queue_name: str) -> int:
    """
    Kiểm tra số lượng task còn lại trong hàng đợi RabbitMQ.
    """
    queue = channel.queue_declare(queue=queue_name, passive=True)
    return queue.method.message_count

