import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Any

from aio_pika.abc import AbstractIncomingMessage
from msgpack import packb


@dataclass
class MockMessage:
    body: bytes
    correlation_id: str

    async def ack(self, multiple: bool = False) -> None:
        pass

    async def reject(self, multiple: bool = False) -> None:
        pass

class MockRMQManager:
    queues: dict[str, deque] = {}

    def __init__(self, pool: Any):
        ...

    async def init_queue(self, queue_name: str) -> None:
        if queue_name in self.queues:
            return
        self.queues[queue_name] = deque()

    async def publish_message(self, message: dict, queue_name: str, correlation_id: Any | None) -> None:

        self.queues[queue_name].append(MockMessage(packb(message), correlation_id=correlation_id))

    async def purge_queue(self, queue_name: str) -> None:
        self.queues[queue_name].clear()

    async def await_objects(self, queue_name: str) -> bool:
        for _ in range(3):
            messages_count: int = len(self.queues[queue_name])
            if messages_count > 0:
                return True
            await asyncio.sleep(0.1)
        return False

    async def get_obj(self, queue_name: str) -> AbstractIncomingMessage:
            queue = self.queues[queue_name]
            obj = await queue.popleft()
            await obj.ack()
            return obj

    async def quantity_messages(self, queue_name: str) -> int | None:
            return len(self.queues[queue_name])