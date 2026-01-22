"""Models of how data is represneted in the ST JSON export"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TextMessage(BaseModel):
    sent_at: int
    content: str
    direction: Literal["in", "out"] | None = None


class CallRecord(BaseModel):
    called_at: int
    duration: int
    notes: str | None = None


class Note(BaseModel):
    id: int
    content: str
    agent_user_id: int
    created_at: datetime
    updated_at: datetime


class Donation(BaseModel):
    model_config = ConfigDict(extra="allow")


class Person(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    id: int
    name: str
    first_name: str
    last_name: str

    phone_number: str | None = None
    email: str | None = None

    chapter: str | None = None
    preferred_language: str | None = None

    full_address: str | None = None
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None

    created_at: datetime
    paid_dues_since: datetime | None = None
    last_ip_address: str | None = None

    tags: list[str] = Field(default_factory=list)

    yes_rsvp_count: int | None = None
    confirmed_rsvp_count: int | None = None

    most_recent_yes_rsvp_session: str | None = None
    most_recent_confirmed_yes_rsvp_session: str | None = None

    action_interests: str | None = Field(default=None, alias="action-interests")
    cause_interests: str | None = Field(default=None, alias="cause-interests")

    # list_date: Optional[date] = Field(
    #    default=None, alias="list-date"
    # )

    membership_status: str | None = Field(default=None, alias="membership-status")

    ydsa_chapter: str | None = Field(default=None, alias="ydsa-chapter")

    texts: list[TextMessage] = Field(default_factory=list)
    calls: list[CallRecord] = Field(default_factory=list)
    notes: list[Note] = Field(default_factory=list)
    donations: list[Donation] = Field(default_factory=list)
