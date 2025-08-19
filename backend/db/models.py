from db.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
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
    instances = relationship("WorkflowRun", back_populates="workflow",cascade="all, delete-orphan")

class WorkflowRun(Base):
    __tablename__="workflow_runs"
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(String(50), default="pending", index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True),nullable=True)
    workflow=relationship("Workflow", back_populates="instances")
    logs = Column(Text, nullable=True)
    steps = relationship("StepInstance", back_populates="run", cascade="all, delete-orphan")

class StepInstance(Base):
    __tablename__ = "step_instances"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(String(128), nullable=False)   # id of the step in definition (string)
    name = Column(String(255), nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, running, success, failed
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    logs = Column(Text, nullable=True)
    output = Column(JSON, nullable=True)

    run = relationship("WorkflowRun", back_populates="steps")