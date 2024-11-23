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


@router.post("/tasks/", status_code=status.HTTP_201_CREATED, tags=["RabbitMQ"])
async def add_task(task: TaskRequest, channel: BlockingChannel = Depends(get_channel)):
    if not (1 <= task.priority <= 10):
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 10.")

    # Kết nối RabbitMQ và gửi tin nhắn
    channel.basic_publish(
        exchange="",
        routing_key="task_queue",
        body=task.task_name,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Tin nhắn bền vững
            priority=task.priority,  # Đặt mức độ ưu tiên
        ),
    )
    return {"message": "Task added to queue", "task": task.task_name, "priority": task.priority}


@router.get("/tasks/", tags=["RabbitMQ"])
async def get_tasks(channel: BlockingChannel = Depends(get_channel)):
    """
    Tiêu thụ các task từ RabbitMQ và trả về danh sách task đã xử lý, kèm theo thời gian tiêu thụ.
    """
    global total_tasks_to_process

    # Lấy số lượng task cần xử lý từ hàng đợi
    total_tasks_to_process = get_task_queue_size(channel)
    print(f"Expecting to process {total_tasks_to_process} tasks.")

    start_time = time.time()  # Lưu thời gian bắt đầu

    # Chỉ nhận 1 task tại một thời điểm (cải thiện hiệu suất)
    channel.basic_qos(prefetch_count=1)

    # Bắt đầu tiêu thụ message từ queue
    print("Start consuming tasks...")

    # Chạy một task bất đồng bộ để xử lý các message
    while total_tasks_to_process > 0:
        method_frame, header_frame, body = channel.basic_get(queue="task_queue", auto_ack=False)
        if method_frame:
            process_task(channel, method_frame, header_frame, body)
        else:
            # Nếu không có message mới, chờ một chút rồi kiểm tra lại
            await asyncio.sleep(1)

    end_time = time.time()  # Lưu thời gian kết thúc
    time_consumed = end_time - start_time  # Tính toán thời gian tiêu thụ

    # Trả về danh sách các task đã xử lý và thời gian tiêu thụ
    return {
        "message": "All tasks processed",
        "processed_tasks": processed_tasks,
        "time_consumed": time_consumed,
        "total_tasks": total_tasks_to_process,
    }


def process_task(ch, method, properties, body):
    task_name = body.decode()
    print(f"Processing task: {task_name} (Priority: {properties.priority})")
    asyncio.sleep(2)  # Mô phỏng thời gian xử lý
    ch.basic_ack(delivery_tag=method.delivery_tag)
    processed_tasks.append(task_name)

    # Kiểm tra số lượng task còn lại trong hàng đợi
    task_count = get_task_queue_size(ch)
    print(f"Remaining tasks in queue: {task_count}")

    # Cập nhật tổng số task đã xử lý
    global total_tasks_to_process
    total_tasks_to_process = task_count

    # Nếu không còn task nào trong hàng đợi, kích hoạt sự kiện
    if task_count == 0:
        task_processed_event.set()  # Tất cả task đã được xử lý


def get_task_queue_size(channel: BlockingChannel) -> int:
    """
    Kiểm tra số lượng task còn lại trong hàng đợi RabbitMQ.
    """
    queue = channel.queue_declare(queue="task_queue", passive=True)
    return queue.method.message_count
