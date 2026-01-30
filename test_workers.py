import sys
sys.path.append('backend')

from cluster_manager import ClusterManager
from models import ClusterConfig, WorkerConfig

# Test per-worker configuration
workers = [
    WorkerConfig(memory='2g', cores=2),
    WorkerConfig(memory='4g', cores=4),
    WorkerConfig(memory='1g', cores=1),
]

cm = ClusterManager()
config = ClusterConfig(workers=workers)
success = cm.generate_docker_compose(config)
print(f"\nGenerated: {success}")
print(f"Worker configs: {config.get_worker_configs()}")
