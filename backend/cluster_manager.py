import subprocess
import os
from pathlib import Path
from typing import Optional, List, Dict
import config
from models import ClusterConfig, ClusterStatus, WorkerConfig


class ClusterManager:
    """Manages Spark cluster configuration and lifecycle"""
    
    def __init__(self):
        self.config: Optional[ClusterConfig] = None
        self.is_running = False
        
    def generate_docker_compose(self, cluster_config: ClusterConfig) -> bool:
        """Generate docker-compose.yml from template with worker nodes"""
        try:
            # Read template
            with open(config.DOCKER_COMPOSE_TEMPLATE, 'r') as f:
                template = f.read()
            
            # Get worker configurations
            worker_configs = cluster_config.get_worker_configs()
            
            # Generate worker services
            workers_config = []
            for i, worker_cfg in enumerate(worker_configs, 1):
                port = 8080 + i
                worker_service = f"""
  spark-worker-{i}:
    build:
      context: .
      dockerfile: docker/Dockerfile.spark-worker
    container_name: spark-worker-{i}
    hostname: spark-worker-{i}
    ports:
      - "{port}:{port}"
    networks:
      - spark-network
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY={worker_cfg.memory}
      - SPARK_WORKER_CORES={worker_cfg.cores}
      - SPARK_WORKER_WEBUI_PORT={port}
      - SPARK_PUBLIC_DNS=localhost
    depends_on:
      - spark-master
"""
                workers_config.append(worker_service)
            
            # Replace placeholder with workers
            workers_yaml = "\n".join(workers_config) if workers_config else "  # No workers configured"
            final_config = template.replace("{{WORKERS}}", workers_yaml)
            
            # Write docker-compose.yml
            with open(config.DOCKER_COMPOSE_FILE, 'w') as f:
                f.write(final_config)
            
            self.config = cluster_config
            print(f"Generated docker-compose.yml with {len(worker_configs)} workers")
            for i, wcfg in enumerate(worker_configs, 1):
                print(f"  Worker-{i}: {wcfg.memory} memory, {wcfg.cores} cores")
            return True
            
        except Exception as e:
            print(f"Error generating docker-compose: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start_cluster(self) -> tuple[bool, str]:
        """Start the Spark cluster using docker-compose"""
        try:
            # Change to project directory
            os.chdir(config.BASE_DIR)
            
            # Start docker-compose with orphan cleanup
            result = subprocess.run(
                ["docker-compose", "up", "-d", "--remove-orphans"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                self.is_running = True
                print("Cluster started successfully")
                print(f"stdout: {result.stdout}")
                return True, "Cluster started successfully"
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                print(f"Error starting cluster: {error_msg}")
                return False, f"Error starting cluster: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout: Cluster took too long to start (>5 min)"
        except Exception as e:
            return False, f"Exception starting cluster: {str(e)}"
    
    def stop_cluster(self) -> tuple[bool, str]:
        """Stop the Spark cluster"""
        try:
            os.chdir(config.BASE_DIR)
            
            result = subprocess.run(
                ["docker-compose", "down"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.is_running = False
                print("Cluster stopped successfully")
                return True, "Cluster stopped successfully"
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                print(f"Error stopping cluster: {error_msg}")
                return False, f"Error stopping cluster: {error_msg}"
                
        except Exception as e:
            return False, f"Exception stopping cluster: {str(e)}"
    
    def restart_cluster(self) -> tuple[bool, str]:
        """Restart the cluster with new configuration"""
        print("Restarting cluster...")
        # Check if cluster is currently running
        status = self.get_cluster_status()
        
        if status.running:
            print("Stopping existing cluster...")
            success, msg = self.stop_cluster()
            if not success:
                return False, f"Failed to stop cluster: {msg}"
        
        print("Starting cluster with new configuration...")
        return self.start_cluster()
    
    def get_cluster_status(self) -> ClusterStatus:
        """Get current cluster status"""
        try:
            os.chdir(config.BASE_DIR)
            
            # Check if containers are running
            result = subprocess.run(
                ["docker-compose", "ps", "--services", "--filter", "status=running"],
                capture_output=True,
                text=True
            )
            
            running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
            is_running = 'spark-master' in running_services
            
            # Count workers
            worker_count = sum(1 for s in running_services if s.startswith('spark-worker'))
            
            # Build worker info
            workers = []
            for i in range(1, worker_count + 1):
                workers.append({
                    "name": f"spark-worker-{i}",
                    "ui_url": f"http://localhost:{8080 + i}"
                })
            
            return ClusterStatus(
                running=is_running,
                master_url=config.SPARK_MASTER_URL if is_running else None,
                master_ui_url=config.SPARK_MASTER_UI_URL if is_running else None,
                worker_count=worker_count,
                workers=workers
            )
            
        except Exception as e:
            print(f"Error getting cluster status: {e}")
            return ClusterStatus(running=False, worker_count=0)
    
    def update_cluster_config(self, cluster_config: ClusterConfig) -> tuple[bool, str]:
        """Update cluster configuration and restart"""
        try:
            worker_configs = cluster_config.get_worker_configs()
            print(f"Updating cluster config: {len(worker_configs)} workers")
            for i, wcfg in enumerate(worker_configs, 1):
                print(f"  Worker-{i}: {wcfg.memory} memory, {wcfg.cores} cores")
            
            # Generate new docker-compose
            if not self.generate_docker_compose(cluster_config):
                return False, "Failed to generate docker-compose configuration"
            
            # Restart cluster
            print("Regenerated docker-compose.yml, restarting cluster...")
            return self.restart_cluster()
            
        except Exception as e:
            error_msg = f"Error updating cluster config: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return False, error_msg
