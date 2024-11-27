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


# Fanout Exchange
@router.post("/fanout/tasks/", status_code=status.HTTP_201_CREATED, tags=["RabbitMQ"])
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


@router.get("/tasks/", tags=["RabbitMQ"])
async def get_tasks(queue_name: str, channel: BlockingChannel = Depends(get_channel)):
    """
    Consume tasks from RabbitMQ and return a list of processed tasks along with processing time.
    """
    global total_tasks_to_process

    # Get the number of tasks to process from the queue
    total_tasks_to_process = get_task_queue_size(channel)
    print(f"Expecting to process {total_tasks_to_process} tasks.")

    start_time = time.time()  # Record start time

    # Only receive one task at a time (improve performance)
    channel.basic_qos(prefetch_count=1)

    # Start consuming messages from the queue
    print("Start consuming tasks...")

    # Run an asynchronous task to process messages
    while total_tasks_to_process > 0:
        method_frame, header_frame, body = channel.basic_get(queue="task_queue", auto_ack=False)
        if method_frame:
            process_task(channel, method_frame, header_frame, body, queue_name)
        else:
            # If no new messages, wait a bit and check again
            await asyncio.sleep(1)

    end_time = time.time()  # Record end time
    time_consumed = end_time - start_time  # Calculate time spent

    # Return the list of processed tasks and the time consumed
    return {
        "message": "All tasks processed",
        "processed_tasks": processed_tasks,
        "time_consumed": time_consumed,
        "total_tasks": total_tasks_to_process,
    }


def process_task(ch, method, properties, body, queue_name: str):
    task_name = body.decode()
    print(f"Processing task: {task_name} (Priority: {properties.priority})")
    asyncio.sleep(2)  # Simulate processing time
    ch.basic_ack(delivery_tag=method.delivery_tag)
    processed_tasks.append(task_name)

    # Check the number of remaining tasks in the queue
    task_count = get_task_queue_size(ch, queue_name)
    print(f"Remaining tasks in queue: {task_count}")

    # Update the total number of tasks processed
    global total_tasks_to_process
    total_tasks_to_process = task_count

    # If no tasks are left in the queue, trigger the event
    if task_count == 0:
        task_processed_event.set()  # All tasks have been processed


def get_task_queue_size(channel: BlockingChannel, queue_name: str) -> int:
    """
    Check the number of tasks remaining in the RabbitMQ queue.
    """
    queue = channel.queue_declare(queue=queue_name, passive=True)
    return queue.method.message_count
