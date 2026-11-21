from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel

@CrewBase
class SupportCrew:
    """Support Crew"""
    @agent
    def test_agent(self) -> Agent:       
        return Agent(
            config=self.agents_config["test_agent"],
            llm="gpt-4o-mini",
        )
    
    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_task"]
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
        )
    

if __name__ == "__main__":
    # TEMPORARY: run the crew alone, without the flow. Remove once it's connected.
    import sys
    from support_triage.utils import parse_ticket

    ticket = parse_ticket(sys.argv[1])
    result = SupportCrew().crew().kickoff(
        inputs={"ticket_id": ticket.ticket_id, "content": ticket.content}
    )
    print(result.raw)
