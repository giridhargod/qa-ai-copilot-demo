from services import OpenAIService
from agents import UIAnalysisAgent

service = OpenAIService()

agent = UIAnalysisAgent(service)

print(agent.name)