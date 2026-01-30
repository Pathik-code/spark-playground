from pydantic import BaseModel
from typing import Optional, List


class WorkerConfig(BaseModel):
    """Configuration for a single worker"""
    memory: str = "1g"
    cores: int = 1


class ClusterConfig(BaseModel):
    """Configuration for Spark cluster"""
    workers: Optional[List[WorkerConfig]] = None  # Per-worker config
    # Deprecated fields for backward compatibility
    worker_memory: Optional[str] = None
    worker_cores: Optional[int] = None
    
    def get_worker_configs(self) -> List[WorkerConfig]:
        """Get list of worker configurations"""
        if self.workers:
            return self.workers
        # Fallback to old format
        count = len(self.workers) if self.workers else 2
        return [WorkerConfig(
            memory=self.worker_memory or "1g",
            cores=self.worker_cores or 1
        ) for _ in range(count)]


class ClusterStatus(BaseModel):
    """Status information for Spark cluster"""
    running: bool
    master_url: Optional[str] = None
    master_ui_url: Optional[str] = None
    worker_count: int = 0
    workers: List[dict] = []


class NotebookCreate(BaseModel):
    """Request model for creating a new notebook"""
    name: str
    template: Optional[str] = "blank"


class NotebookInfo(BaseModel):
    """Information about a notebook"""
    id: str
    name: str
    path: str
    created_at: str
    template: str


class NotebookListResponse(BaseModel):
    """Response model for listing notebooks"""
    notebooks: List[NotebookInfo]


class ApiResponse(BaseModel):
    """Generic API response"""
    success: bool
    message: str
    data: Optional[dict] = None
