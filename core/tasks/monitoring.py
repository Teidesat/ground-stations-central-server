"""
Health monitoring and metrics collection tasks.
"""

import psutil
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor system resources and health."""
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Collect current system metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def check_health() -> Dict[str, Any]:
        """Perform health check."""
        metrics = SystemMonitor.get_system_metrics()
        is_healthy = all([
            metrics['cpu_percent'] < 90,
            metrics['memory_percent'] < 90,
            metrics['disk_usage'] < 90
        ])
        
        return {
            'healthy': is_healthy,
            'metrics': metrics,
            'status': 'OK' if is_healthy else 'WARNING'
        }