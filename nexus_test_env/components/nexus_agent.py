from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.nexus_controller import NexusController

class NexusAgent:
    def __init__(self):
        from components.nexus_controller import NexusController
        self.controller = NexusController(agent=self)

    def perform_action(self, action: str, data: dict):
        """A placeholder method for the agent to perform actions."""
        print(f"Agent performing action: {action} with data: {data}")

    def get_controller(self) -> NexusController:
        return self.controller
