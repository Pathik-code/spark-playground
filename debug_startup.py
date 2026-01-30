
import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend import config
    print("Config imported")
    from backend.models import ClusterConfig, WorkerConfig
    print("Models imported")
    from backend.cluster_manager import ClusterManager
    print("ClusterManager imported")
    
    # Simulate startup event logic
    print("Simulating startup...")
    
    default_workers = [
        WorkerConfig(
            memory=config.DEFAULT_WORKER_MEMORY,
            cores=config.DEFAULT_WORKER_CORES
        ) for _ in range(config.DEFAULT_WORKER_COUNT)
    ]
    
    default_config = ClusterConfig(workers=default_workers)
    print(f"Created config with {len(default_workers)} workers")
    
    cm = ClusterManager()
    cm.generate_docker_compose(default_config)
    print("Startup simulation successful!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
