"""
Asynchronous task processors for buffer management and data processing.
"""

import asyncio
import logging
from typing import Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Status of task processing."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ProcessingMetrics:
    """Metrics for task processing."""
    items_processed: int = 0
    errors_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    last_error: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate processing duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def items_per_second(self) -> float:
        """Calculate processing rate."""
        duration = self.duration_seconds
        if duration > 0 and self.items_processed > 0:
            return self.items_processed / duration
        return 0.0


class BufferProcessor:
    """
    Professional buffer processor with metrics, error handling, and lifecycle management.
    """
    
    def __init__(
        self,
        buffer,
        classifier,
        log_service: Optional[Callable] = None,
        batch_size: int = 10,
        delay_between_items: float = 0.0
    ):
        """
        Initialize the buffer processor.
        
        Args:
            buffer: StackBuffer instance
            classifier: Classifier instance for processing
            log_service: Async function for logging (create_log)
            batch_size: Number of items to process in batch
            delay_between_items: Delay in seconds between items
        """
        self.buffer = buffer
        self.classifier = classifier
        self.log_service = log_service
        self.batch_size = batch_size
        self.delay_between_items = delay_between_items
        
        self.status = ProcessingStatus.IDLE
        self.metrics = ProcessingMetrics()
        self._stop_requested = False
        self._pause_requested = False
        self._current_task: Optional[asyncio.Task] = None
        
        logger.info(
            f"BufferProcessor initialized - batch_size={batch_size}, "
            f"delay={delay_between_items}s"
        )
    
    async def process_item(self, item) -> bool:
        """
        Process a single item from the buffer.
        
        Args:
            item: Item to process
            
        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            # Read the content
            data_content = item.read()
            
            # Process with classifier
            result = await self.classifier.identificar_tipo(
                item.content_type, 
                data_content
            )
            
            # Log success if log service is available
            if self.log_service:
                await self.log_service(
                    level='DEBUG',
                    logger='buffer-processor',
                    module='core.tasks.processor',
                    function='process_item',
                    message=f'Item processed successfully: {item.content_type}',
                )
            
            logger.debug(f"Item processed: {item.content_type}")
            return True
            
        except Exception as e:
            self.metrics.errors_count += 1
            self.metrics.last_error = str(e)
            
            error_msg = f'Failed to process item: {e}'
            logger.error(error_msg, exc_info=True)
            
            # Log error if log service is available
            if self.log_service:
                await self.log_service(
                    level='ERROR',
                    logger='buffer-processor',
                    module='core.tasks.processor',
                    function='process_item',
                    message=error_msg,
                    exception=e,
                )
            
            return False
    
    async def process_batch(self, batch_items: list) -> dict:
        """
        Process a batch of items concurrently.
        
        Args:
            batch_items: List of items to process
            
        Returns:
            dict: Batch processing results
        """
        tasks = [self.process_item(item) for item in batch_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if r is True)
        failed = sum(1 for r in results if isinstance(r, Exception) or r is False)
        
        return {
            'total': len(batch_items),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(batch_items) if batch_items else 0
        }
    
    async def _process_loop(self):
        """Main processing loop."""
        self.status = ProcessingStatus.RUNNING
        self.metrics.start_time = datetime.now()
        
        logger.info("Buffer processor started")
        
        if self.log_service:
            await self.log_service(
                level='INFO',
                logger='buffer-processor',
                module='core.tasks.processor',
                function='_process_loop',
                message='Buffer processor started',
            )
        
        try:
            while not self._stop_requested:
                # Handle pause request
                if self._pause_requested:
                    await asyncio.sleep(0.5)
                    continue
                
                # Check if buffer is empty
                if self.buffer.is_empty():
                    logger.debug("Buffer empty, waiting for items...")
                    await asyncio.sleep(0.1)
                    continue
                
                # Process items in batches
                batch = []
                while len(batch) < self.batch_size and not self.buffer.is_empty():
                    item = self.buffer.get()
                    if item:
                        batch.append(item)
                
                if batch:
                    logger.info(f"Processing batch of {len(batch)} items")
                    result = await self.process_batch(batch)
                    self.metrics.items_processed += result['successful']
                    
                    logger.info(
                        f"Batch completed - Success: {result['successful']}, "
                        f"Failed: {result['failed']}, Rate: {result['success_rate']:.2%}"
                    )
                
                # Add delay between batches if specified
                if self.delay_between_items > 0:
                    await asyncio.sleep(self.delay_between_items)
                    
        except asyncio.CancelledError:
            logger.info("Processing loop cancelled")
            self.status = ProcessingStatus.STOPPED
            raise
        except Exception as e:
            logger.error(f"Fatal error in processing loop: {e}", exc_info=True)
            self.status = ProcessingStatus.ERROR
            
            if self.log_service:
                await self.log_service(
                    level='CRITICAL',
                    logger='buffer-processor',
                    module='core.tasks.processor',
                    function='_process_loop',
                    message=f'Fatal error: {e}',
                    exception=e,
                )
        finally:
            self.metrics.end_time = datetime.now()
            self._log_final_metrics()
    
    def _log_final_metrics(self):
        """Log final processing metrics."""
        metrics_msg = (
            f"Processing completed - Status: {self.status.value}, "
            f"Items: {self.metrics.items_processed}, "
            f"Errors: {self.metrics.errors_count}, "
            f"Duration: {self.metrics.duration_seconds:.2f}s, "
            f"Rate: {self.metrics.items_per_second:.2f} items/s"
        )
        
        logger.info(metrics_msg)
        
        if self.log_service:
            # Need to run this in an async context
            asyncio.create_task(
                self.log_service(
                    level='INFO',
                    logger='buffer-processor',
                    module='core.tasks.processor',
                    function='_log_final_metrics',
                    message=metrics_msg,
                )
            )
    
    async def start(self):
        """Start the processor."""
        if self.status == ProcessingStatus.RUNNING:
            logger.warning("Processor already running")
            return
        
        self._stop_requested = False
        self._pause_requested = False
        self._current_task = asyncio.create_task(self._process_loop())
        
        logger.info("Processor started")
    
    async def stop(self):
        """Stop the processor gracefully."""
        logger.info("Stopping processor...")
        self._stop_requested = True
        
        if self._current_task:
            self._current_task.cancel()
            try:
                await self._current_task
            except asyncio.CancelledError:
                pass
        
        self.status = ProcessingStatus.STOPPED
        logger.info("Processor stopped")
    
    async def pause(self):
        """Pause the processor."""
        self._pause_requested = True
        self.status = ProcessingStatus.PAUSED
        logger.info("Processor paused")
    
    async def resume(self):
        """Resume the processor."""
        self._pause_requested = False
        self.status = ProcessingStatus.RUNNING
        logger.info("Processor resumed")
    
    def get_status(self) -> dict:
        """Get current processor status."""
        return {
            'status': self.status.value,
            'metrics': {
                'items_processed': self.metrics.items_processed,
                'errors_count': self.metrics.errors_count,
                'duration_seconds': self.metrics.duration_seconds,
                'items_per_second': self.metrics.items_per_second,
                'last_error': self.metrics.last_error,
            },
            'buffer_size': len(self.buffer),
            'is_paused': self._pause_requested,
        }


# Backward compatibility functions
async def control_while(buffer, classifier, log_service=None):
    """
    Legacy function for backward compatibility.
    
    Args:
        buffer: StackBuffer instance
        classifier: Classifier instance
        log_service: Optional log service function
    """
    processor = BufferProcessor(buffer, classifier, log_service=log_service)
    await processor.start()
    
    # Wait until buffer is empty and processor stops
    while not buffer.is_empty() or processor.status == ProcessingStatus.RUNNING:
        await asyncio.sleep(0.5)
        if buffer.is_empty():
            await processor.stop()
            break


async def run_control_while(buffer, classifier, log_service=None):
    """
    Legacy wrapper for run_control_while.
    
    Args:
        buffer: StackBuffer instance
        classifier: Classifier instance
        log_service: Optional log service function
    """
    processor = BufferProcessor(buffer, classifier, log_service=log_service)
    await processor.start()
    return processor