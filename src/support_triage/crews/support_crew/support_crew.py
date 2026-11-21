from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel

@CrewBase
class SupportCrew:
    """Support Crew"""
    

