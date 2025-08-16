from database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Workflow(Base):
    __tablename__='workflows'

    id=Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    definition = Column(Text, nullable=False)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships, to connect instances of tables already connected with foregin keys
    # behaviour changes depending on where foreign key is. 1-to-many vs 1-to-1
    instances = relationship("WorkflowInstance", back_populates="workflow")

class WorkflowRun(Base):
    __tablename__="workflow_runs"
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(String(50), default="pending", index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True),nullable=True)
    workflow=relationship("Workflow", back_populates="instances")
    logs = Column(Text, nullable=True)