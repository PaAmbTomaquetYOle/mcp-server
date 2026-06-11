"""
This module defines the domain models for the collaboration task jerarchy, including the base CollaborationTask and specific implementations like JiraTask. These models represent the core business concepts related to collaboration tool integration and are independent of any technology or framework.
"""

from .collaboration_task import CollaborationTask
from .jira_task import JiraTask
from .trello_task import TrelloTask

__all__ = [
    "CollaborationTask",
    "JiraTask",
    "TrelloTask",
]