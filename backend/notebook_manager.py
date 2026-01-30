import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import config
from models import NotebookCreate, NotebookInfo


class NotebookManager:
    """Manages Jupyter notebooks"""
    
    def __init__(self):
        self.notebooks_dir = config.USER_NOTEBOOKS_DIR
        self.templates_dir = config.TEMPLATES_DIR
        
    def create_notebook(self, notebook_create: NotebookCreate) -> Optional[NotebookInfo]:
        """Create a new notebook from template or blank"""
        try:
            # Generate unique ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            notebook_id = f"{notebook_create.name.replace(' ', '_')}_{timestamp}"
            notebook_filename = f"{notebook_id}.ipynb"
            notebook_path = self.notebooks_dir / notebook_filename
            
            # Check if template exists
            template_name = notebook_create.template
            if template_name and template_name != "blank":
                template_path = self.templates_dir / f"{template_name}.ipynb"
                if template_path.exists():
                    # Copy template
                    shutil.copy(template_path, notebook_path)
                else:
                    # Create blank if template not found
                    self._create_blank_notebook(notebook_path)
            else:
                # Create blank notebook
                self._create_blank_notebook(notebook_path)
            
            return NotebookInfo(
                id=notebook_id,
                name=notebook_create.name,
                path=str(notebook_path.relative_to(config.BASE_DIR)),
                created_at=datetime.now().isoformat(),
                template=template_name or "blank"
            )
            
        except Exception as e:
            print(f"Error creating notebook: {e}")
            return None
    
    def _create_blank_notebook(self, path: Path):
        """Create a blank Jupyter notebook with Spark initialization"""
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# PySpark Notebook\n",
                        "\n",
                        "This notebook is connected to the Spark cluster."
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Initialize Spark Session\n",
                        "from pyspark.sql import SparkSession\n",
                        "\n",
                        "spark = SparkSession.builder \\\n",
                        "    .appName('PySpark Playground') \\\n",
                        "    .master('spark://spark-master:7077') \\\n",
                        "    .getOrCreate()\n",
                        "\n",
                        "print(f'Spark Version: {spark.version}')\n",
                        "print(f'Spark Master: {spark.sparkContext.master}')"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Your code here\n"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(path, 'w') as f:
            json.dump(notebook_content, f, indent=2)
    
    def list_notebooks(self) -> List[NotebookInfo]:
        """List all user notebooks"""
        notebooks = []
        
        try:
            for notebook_file in self.notebooks_dir.glob("*.ipynb"):
                stat = notebook_file.stat()
                created_at = datetime.fromtimestamp(stat.st_ctime)
                
                notebooks.append(NotebookInfo(
                    id=notebook_file.stem,
                    name=notebook_file.stem.split('_')[0].replace('_', ' '),
                    path=str(notebook_file.relative_to(config.BASE_DIR)),
                    created_at=created_at.isoformat(),
                    template="unknown"
                ))
            
            # Sort by creation time (newest first)
            notebooks.sort(key=lambda x: x.created_at, reverse=True)
            
        except Exception as e:
            print(f"Error listing notebooks: {e}")
        
        return notebooks
    
    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a notebook by ID"""
        try:
            notebook_path = self.notebooks_dir / f"{notebook_id}.ipynb"
            if notebook_path.exists():
                notebook_path.unlink()
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting notebook: {e}")
            return False
    
    def get_notebook_url(self, notebook_id: str) -> Optional[str]:
        """Get Jupyter URL for a specific notebook"""
        try:
            notebook_path = self.notebooks_dir / f"{notebook_id}.ipynb"
            if notebook_path.exists():
                # Relative path from notebooks directory
                relative_path = f"user/{notebook_id}.ipynb"
                return f"{config.JUPYTER_URL}/notebooks/{relative_path}"
            return None
            
        except Exception as e:
            print(f"Error getting notebook URL: {e}")
            return None
