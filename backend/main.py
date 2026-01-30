from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import config
from models import (
    ClusterConfig, ClusterStatus, NotebookCreate, 
    NotebookInfo, NotebookListResponse, ApiResponse
)
from cluster_manager import ClusterManager
from notebook_manager import NotebookManager

# Initialize FastAPI app
app = FastAPI(
    title="PySpark Playground API",
    description="API for managing Spark clusters and Jupyter notebooks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
frontend_dir = Path(config.BASE_DIR / "frontend")
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Initialize managers
cluster_manager = ClusterManager()
notebook_manager = NotebookManager()

# Store logs for UI display
cluster_logs = []


@app.on_event("startup")
async def startup_event():
    """Initialize cluster with default configuration on startup"""
    from models import WorkerConfig
    
    # Create default workers
    default_workers = [
        WorkerConfig(
            memory=config.DEFAULT_WORKER_MEMORY,
            cores=config.DEFAULT_WORKER_CORES
        ) for _ in range(config.DEFAULT_WORKER_COUNT)
    ]
    
    default_config = ClusterConfig(workers=default_workers)
    cluster_manager.generate_docker_compose(default_config)


# Cluster Management Endpoints

@app.post("/api/cluster/config", response_model=ApiResponse)
async def update_cluster_config(cluster_config: ClusterConfig):
    """Update cluster configuration and restart"""
    global cluster_logs
    worker_configs = cluster_config.get_worker_configs()
    cluster_logs.append(f"Updating cluster config to {len(worker_configs)} worker(s)...")
    
    success, message = cluster_manager.update_cluster_config(cluster_config)
    cluster_logs.append(message)
    
    if success:
        return ApiResponse(
            success=True,
            message=f"Cluster configured with {len(worker_configs)} worker(s)",
            data={'workers': [{'memory': w.memory, 'cores': w.cores} for w in worker_configs]}
        )
    else:
        raise HTTPException(status_code=500, detail=message)


@app.get("/api/cluster/status", response_model=ClusterStatus)
async def get_cluster_status():
    """Get current cluster status"""
    return cluster_manager.get_cluster_status()


@app.post("/api/cluster/start", response_model=ApiResponse)
async def start_cluster():
    """Start the Spark cluster"""
    global cluster_logs
    cluster_logs.append("Starting Spark cluster...")
    
    success, message = cluster_manager.start_cluster()
    cluster_logs.append(message)
    
    if success:
        return ApiResponse(
            success=True,
            message="Cluster started successfully"
        )
    else:
        raise HTTPException(status_code=500, detail=message)


@app.post("/api/cluster/stop", response_model=ApiResponse)
async def stop_cluster():
    """Stop the Spark cluster"""
    global cluster_logs
    cluster_logs.append("Stopping Spark cluster...")
    
    success, message = cluster_manager.stop_cluster()
    cluster_logs.append(message)
    
    if success:
        return ApiResponse(
            success=True,
            message="Cluster stopped successfully"
        )
    else:
        raise HTTPException(status_code=500, detail=message)


@app.get("/api/cluster/logs")
async def get_cluster_logs():
    """Get cluster operation logs"""
    global cluster_logs
    return {"logs": cluster_logs[-20:]}  # Return last 20 log entries


@app.post("/api/cluster/logs/clear")
async def clear_cluster_logs():
    """Clear cluster logs"""
    global cluster_logs
    cluster_logs = []
    return {"message": "Logs cleared"}


# Notebook Management Endpoints

@app.post("/api/notebooks/create", response_model=NotebookInfo)
async def create_notebook(notebook_create: NotebookCreate):
    """Create a new notebook"""
    notebook_info = notebook_manager.create_notebook(notebook_create)
    
    if notebook_info:
        return notebook_info
    else:
        raise HTTPException(status_code=500, detail="Failed to create notebook")


@app.get("/api/notebooks/list", response_model=NotebookListResponse)
async def list_notebooks():
    """List all notebooks"""
    notebooks = notebook_manager.list_notebooks()
    return NotebookListResponse(notebooks=notebooks)


@app.delete("/api/notebooks/{notebook_id}", response_model=ApiResponse)
async def delete_notebook(notebook_id: str):
    """Delete a notebook"""
    success = notebook_manager.delete_notebook(notebook_id)
    
    if success:
        return ApiResponse(
            success=True,
            message=f"Notebook {notebook_id} deleted successfully"
        )
    else:
        raise HTTPException(status_code=404, detail="Notebook not found")


@app.get("/api/notebooks/{notebook_id}/url")
async def get_notebook_url(notebook_id: str):
    """Get Jupyter URL for a notebook"""
    url = notebook_manager.get_notebook_url(notebook_id)
    
    if url:
        return {"url": url}
    else:
        raise HTTPException(status_code=404, detail="Notebook not found")


# Frontend route
@app.get("/")
async def read_root():
    """Serve the frontend application"""
    frontend_file = frontend_dir / "index.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    else:
        return {"message": "PySpark Playground API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.BACKEND_HOST, port=config.BACKEND_PORT)
