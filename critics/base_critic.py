# critics/base_critic.py
from abc import ABC, abstractmethod

class BaseCritic(ABC):
    """
    Base interface for every reusable QA Critic.

    A Critic never generates business output.

    Its responsibility is to independently evaluate the
    output produced by another Skill and provide an
    objective governance decision.

    Every Critic must return a standardized review
    contract so the Workflow Engine can process
    every Skill consistently.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable critic name."""
        pass

    @abstractmethod
    def review(
        self,
        result: dict
    ) -> dict:
        """
        Reviews the output produced by a Skill.

        Returns
        -------
        dict
            Standard Critic Contract
        """
        pass