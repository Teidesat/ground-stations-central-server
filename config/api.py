# config/api.py
"""Ninja API configuration and routing for the Satellite Ground Station."""

from ninja import NinjaAPI, UploadedFile

from apps.audit.api import router as audit_router
from apps.bridge.api import router as bridge_router
from apps.imaging.api import router as imaging_router
from config.auth import SimpleTokenAuth
from core.buffers.stack_buffer import StackBuffer
from core.classifiers.image_classifier import Classifier
from core.tasks.processor import BufferProcessor

# Initialize Ninja API instance
api = NinjaAPI(
    title="Satellite Ground Station API",
    version="1.0.0",
    description="API for processing satellite telemetry and commands",
    auth=SimpleTokenAuth(),
    urls_namespace="api"
)

# Initialize global components
classifier = Classifier()
stack_buffer = StackBuffer(maxsize=150)
processor = None

# Register routers from each app with consistent trailing slashes
api.add_router("/imaging/", imaging_router, tags=["Image Analysis"])
api.add_router("/bridge/", bridge_router, tags=["Data Flow"])
api.add_router("/audit/", audit_router, tags=["Log Management"])


@api.post("/upload", tags=["General"])
async def upload_data(request, files: list[UploadedFile]):
    """Primary endpoint for file reception and processing.

    Args:
        request: The HTTP request object.
        files: List of uploaded files to process.

    Returns:
        Dictionary with success status and file count.
    """
    global processor

    for file in files:
        stack_buffer.add(file)

    if processor is None:
        processor = BufferProcessor(
            buffer=stack_buffer,
            classifier=classifier,
            batch_size=10,
            delay_between_items=0.1
        )
        await processor.start()

    return {"success": True, "files_processed": len(files)}


@api.get("/health", tags=["General"])
def health_check(request):
    """Health check endpoint for monitoring.

    Args:
        request: The HTTP request object.

    Returns:
        Dictionary with health status and current buffer size.
    """
    return {"status": "healthy", "buffer_size": len(stack_buffer)}


@api.get("/processor/status", tags=["General"])
def get_processor_status(request):
    """Get the current buffer processor status.

    Args:
        request: The HTTP request object.

    Returns:
        Status dictionary from the processor or not_initialized status.
    """
    global processor
    if processor:
        return processor.get_status()
    return {"status": "not_initialized"}


@api.get("/", tags=["General"])
def api_root(request):
    """API root endpoint providing available endpoint information.

    Args:
        request: The HTTP request object.

    Returns:
        Dictionary with API metadata and endpoint URLs.
    """
    return {
        "name": "Satellite Ground Station API",
        "version": "1.0.0",
        "endpoints": {
            "imaging": "/api/imaging/",
            "audit": "/api/audit/",
            "bridge": "/api/bridge/",
            "health": "/api/health",
        }
    }