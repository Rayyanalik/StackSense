from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

# Association table for project technologies
project_technologies = Table(
    'project_technologies',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('technology_id', Integer, ForeignKey('technologies.id'))
)

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    source = Column(String)  # 'github' or 'stackoverflow'
    source_id = Column(String, index=True)  # Original ID from source
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    technologies = relationship("Technology", secondary=project_technologies, back_populates="projects")
    recommendations = relationship("Recommendation", back_populates="project")
    project_metadata = relationship("ProjectMetadata", back_populates="project", uselist=False)

class Technology(Base):
    __tablename__ = 'technologies'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)  # 'frontend', 'backend', 'database', 'devops'
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    projects = relationship("Project", secondary=project_technologies, back_populates="technologies")
    recommendations = relationship("RecommendationTechnology", back_populates="technology")

class ProjectMetadata(Base):
    __tablename__ = 'project_metadata'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    data = Column(JSON)  # Store additional metadata as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="project_metadata")

class Recommendation(Base):
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    description = Column(String)
    requirements = Column(JSON)  # List of requirements
    constraints = Column(JSON)  # List of constraints
    confidence_level = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="recommendations")
    technologies = relationship("RecommendationTechnology", back_populates="recommendation")

class RecommendationTechnology(Base):
    __tablename__ = 'recommendation_technologies'
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey('recommendations.id'))
    technology_id = Column(Integer, ForeignKey('technologies.id'))
    is_primary = Column(Boolean, default=False)  # Whether it's part of primary stack
    confidence = Column(Float)  # Individual confidence for this technology
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="technologies")
    technology = relationship("Technology", back_populates="recommendations") 