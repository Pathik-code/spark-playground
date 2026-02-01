import sys
sys.path.append('backend')

from cluster_manager import ClusterManager
from models import ClusterConfig, WorkerConfig

# Regenerate docker-compose with 2 workers
cm = ClusterManager()
success = cm.generate_docker_compose(ClusterConfig(
    workers=[
        WorkerConfig(memory='1g', cores=1),
        WorkerConfig(memory='1g', cores=1)
    ]
))
print(f"Generated: {success}")
