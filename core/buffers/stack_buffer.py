"""
Buffer implementations for data queuing and processing.
"""

from typing import Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)


class StackBuffer:
    """
    A thread-safe stack buffer for managing data items with maximum size limit.
    
    Attributes:
        maxsize: Maximum number of items the buffer can hold
        buffer: Internal deque storage
    """
    
    def __init__(self, maxsize: int = 150):
        """
        Initialize the stack buffer.
        
        Args:
            maxsize: Maximum number of items to store (default: 150)
        """
        self.maxsize = maxsize
        self.buffer = deque(maxlen=maxsize)
        logger.info(f"StackBuffer initialized with maxsize={maxsize}")
    
    def add(self, item: Any) -> bool:
        """
        Add an item to the buffer.
        
        Args:
            item: Item to add to buffer
            
        Returns:
            bool: True if item was added successfully
        """
        if len(self.buffer) >= self.maxsize:
            logger.warning(f"Buffer full ({self.maxsize}), oldest item will be removed")
        
        self.buffer.append(item)
        logger.debug(f"Item added to buffer. Current size: {len(self.buffer)}")
        return True
    
    def get(self) -> Optional[Any]:
        """
        Get and remove the most recent item from buffer (LIFO).
        
        Returns:
            The most recent item or None if buffer is empty
        """
        if not self.buffer:
            logger.warning("Attempted to get from empty buffer")
            return None
        
        item = self.buffer.pop()
        logger.debug(f"Item retrieved. Remaining size: {len(self.buffer)}")
        return item
    
    def peek(self) -> Optional[Any]:
        """
        Get the most recent item without removing it.
        
        Returns:
            The most recent item or None if buffer is empty
        """
        if not self.buffer:
            return None
        return self.buffer[-1]
    
    def clear(self) -> None:
        """Clear all items from the buffer."""
        self.buffer.clear()
        logger.info("Buffer cleared")
    
    def size(self) -> int:
        """Return current number of items in buffer."""
        return len(self.buffer)
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self.buffer) == 0
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        return len(self.buffer) >= self.maxsize
    
    def get_all(self) -> list:
        """
        Get all items and clear the buffer.
        
        Returns:
            List of all items in buffer
        """
        items = list(self.buffer)
        self.clear()
        return items
    
    def __len__(self) -> int:
        return self.size()
    
    def __bool__(self) -> bool:
        return not self.is_empty()