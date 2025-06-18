from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Project, Technology, ProjectMetadata
from app.services.logging_service import LoggingService
import time

logger = LoggingService()

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_project(self, project_data: Dict[str, Any]) -> Project:
        """
        Create a new project with its technologies and metadata.
        """
        try:
            start_time = time.time()
            
            # Create project
            project = Project(
                name=project_data['name'],
                description=project_data['description'],
                source=project_data['source'],
                source_id=project_data['source_id'],
                stars=project_data.get('stars', 0),
                forks=project_data.get('forks', 0)
            )
            self.db.add(project)
            self.db.flush()  # Get project ID
            
            # Add technologies
            if 'technologies' in project_data:
                for tech_name in project_data['technologies']:
                    tech = self._get_or_create_technology(tech_name)
                    project.technologies.append(tech)
            
            # Add metadata
            if 'metadata' in project_data:
                metadata = ProjectMetadata(
                    project_id=project.id,
                    data=project_data['metadata']
                )
                self.db.add(metadata)
            
            self.db.commit()
            
            duration = (time.time() - start_time) * 1000
            logger.info(
                "Project created successfully",
                extra_data={
                    'project_id': project.id,
                    'duration_ms': duration
                }
            )
            
            return project
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Error creating project",
                error=e,
                extra_data={'project_data': project_data}
            )
            raise
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """
        Get a project by ID with its technologies and metadata.
        """
        try:
            return self.db.query(Project).filter(Project.id == project_id).first()
        except Exception as e:
            logger.error(
                "Error getting project",
                error=e,
                extra_data={'project_id': project_id}
            )
            raise
    
    def get_projects(
        self,
        skip: int = 0,
        limit: int = 10,
        source: Optional[str] = None
    ) -> List[Project]:
        """
        Get a list of projects with optional filtering.
        """
        try:
            query = self.db.query(Project)
            
            if source:
                query = query.filter(Project.source == source)
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(
                "Error getting projects",
                error=e,
                extra_data={
                    'skip': skip,
                    'limit': limit,
                    'source': source
                }
            )
            raise
    
    def get_projects_by_technologies(
        self,
        technologies: List[str],
        skip: int = 0,
        limit: int = 10
    ) -> List[Project]:
        """
        Get projects that use specific technologies.
        """
        try:
            return (
                self.db.query(Project)
                .join(Project.technologies)
                .filter(Technology.name.in_(technologies))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(
                "Error getting projects by technologies",
                error=e,
                extra_data={
                    'technologies': technologies,
                    'skip': skip,
                    'limit': limit
                }
            )
            raise
    
    def update_project(self, project_id: int, project_data: Dict[str, Any]) -> Optional[Project]:
        """
        Update a project's information.
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return None
            
            # Update basic info
            for key, value in project_data.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            # Update technologies
            if 'technologies' in project_data:
                project.technologies = []
                for tech_name in project_data['technologies']:
                    tech = self._get_or_create_technology(tech_name)
                    project.technologies.append(tech)
            
            # Update metadata
            if 'metadata' in project_data:
                if project.metadata:
                    project.metadata.data = project_data['metadata']
                else:
                    metadata = ProjectMetadata(
                        project_id=project.id,
                        data=project_data['metadata']
                    )
                    self.db.add(metadata)
            
            self.db.commit()
            return project
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Error updating project",
                error=e,
                extra_data={
                    'project_id': project_id,
                    'project_data': project_data
                }
            )
            raise
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project and its related data.
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return False
            
            self.db.delete(project)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Error deleting project",
                error=e,
                extra_data={'project_id': project_id}
            )
            raise
    
    def _get_or_create_technology(self, name: str) -> Technology:
        """
        Get an existing technology or create a new one.
        """
        try:
            tech = self.db.query(Technology).filter(Technology.name == name).first()
            if not tech:
                tech = Technology(name=name)
                self.db.add(tech)
                self.db.flush()
            return tech
        except Exception as e:
            logger.error(
                "Error getting/creating technology",
                error=e,
                extra_data={'technology_name': name}
            )
            raise 