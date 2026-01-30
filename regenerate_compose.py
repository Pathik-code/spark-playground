import sys
sys.path.append('backend')

from cluster_manager import ClusterManager
from models import ClusterConfig

# Regenerate docker-compose with 2 workers
cm = ClusterManager()
success = cm.generate_docker_compose(ClusterConfig(workers=2, worker_memory='1g', worker_cores=1))
print(f"Generated: {success}")
