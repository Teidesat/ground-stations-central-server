import asyncio
from typing import Any


class DataBuffer:
    def __init__(self, maxsize: int = 10):  # Máximo 10 elementos en buffer
        self.queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=int(maxsize))

    async def add_data(self, data: Any):
        """Agrega datos al buffer (espera si está lleno)."""
        await self.queue.put(data)

    async def get_data(self) -> Any:
        """Obtiene un dato del buffer (espera si está vacío)."""
        return await self.queue.get()

    def task_done(self):
        """Indica que el dato fue procesado."""
        self.queue.task_done()