from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ScopeType = Literal["Organization", "Chapter", "Team", "User"]


class UserAddressUpdate(BaseModel):
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class UserUpdate(BaseModel):
    phone_number: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    preferred_language: str | None = None
    chapter_id: int | None = None
    chapter_ids: list[int] | None = None
    add_chapter_ids: list[int] | None = None
    remove_chapter_ids: list[int] | None = None
    set_exclusive_chapter: bool | None = None
    second_language: str | None = None
    referred_by_user_id: int | None = None
    custom_user_properties: dict[str, str] | None = None
    address: UserAddressUpdate | None = None
    sms_permission: bool | None = None
    call_permission: bool | None = None
    email_permission: bool | None = None
    timezone: str | None = None


class UserCreate(BaseModel):
    phone_number: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    preferred_language: str | None = "en"
    second_language: str | None = None
    chapter_id: int | None = None
    chapter_ids: list[int] | None = None
    referred_by_user_id: int | None = None
    custom_user_properties: dict[str, str] | None = None
    add_tags: list[str] | None = None
    remove_tags: list[str] | None = None
    address: UserAddressUpdate | None = None
    sms_permission: bool | None = None
    call_permission: bool | None = None
    email_permission: bool | None = None
    timezone: str | None = None


class EventRsvpCreate(BaseModel):
    event_id: int
    event_session_id: int | None = None
    user_id: int
    is_attending: Literal["yes", "no", "maybe"] | None = "yes"
    is_confirmed: bool | None = False
    agent_user_id: int | None = None
    source: str | None = None
    source_system: str | None = None
    skip_email_confirmation: bool | None = False


class EventRsvpUpdate(BaseModel):
    is_attending: Literal["yes", "no", "maybe"] | None = None
    is_confirmed: bool | None = None
    agent_user_id: int | None = None
    source: str | None = None
    source_system: str | None = None


class ScheduledTaskCreate(BaseModel):
    due_at: int | None = None
    remind_at: int | None = None
    agent_user_id: int | None = None
    user_id: int
    notes: str | None = None
    marked_as_completed: bool | None = False


class UserNoteCreate(BaseModel):
    content: str
    user_id: int
    agent_user_id: int | None = None


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

    # list_date: date | None = Field(
    #    default=None, alias="list-date"
    # )

    membership_status: str | None = Field(default=None, alias="membership-status")

    ydsa_chapter: str | None = Field(default=None, alias="ydsa-chapter")

    texts: list[TextMessage] = Field(default_factory=list)
    calls: list[CallRecord] = Field(default_factory=list)
    notes: list[Note] = Field(default_factory=list)
    donations: list[Donation] = Field(default_factory=list)


class Chapter(BaseModel):
    id: int
    name: str
    logo_url: str | None = None
    organization_id: int
    chapter_phone_number: str | None = None


class Organization(BaseModel):
    id: int
    name: str
    image_url: str | None = None
    parent_organization_id: int | None = None
    default_language: str | None = None
    supported_languages: list[str] | None = None


class User(BaseModel):
    id: int
    hash_id: str | None = None
    phone_number: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    preferred_language: str
    second_language: str | None = None
    chapter_id: int | None = None
    chapter_ids: list[int] = Field(default_factory=list)
    branch_id: int | None = None
    created_at: datetime
    custom_user_properties: dict[str, str] = Field(default_factory=dict)
    address: dict[str, Any] | None = None
    sms_permission: bool = False
    call_permission: bool = False
    email_permission: bool = False


class EventSession(BaseModel):
    id: int
    event_id: int
    start_time: datetime
    end_time: datetime
    title: str | None = None
    location_name: str | None = None
    location_address: str | None = None


class Event(BaseModel):
    id: int
    title: str
    scope_id: int
    scope_type: ScopeType
    event_type: str
    location_name: str | None = None
    created_at: datetime


class Call(BaseModel):
    id: int
    user_id: int
    direction: str
    agent_user_id: int | None = None
    duration: int
    picked_up: bool
    left_voicemail: bool
    created_at: datetime


class Text(BaseModel):
    id: int
    user_id: int
    direction: str
    body: str | None = None
    media_urls: list[str] = Field(default_factory=list)
    created_at: datetime


class UserNote(BaseModel):
    id: int
    content: str
    user_id: int


class DonationCharge(BaseModel):
    id: int
    amount: int

    success: bool
    refunded: bool
    created_at: datetime
    user: dict[str, Any] | None = None


class Activity(BaseModel):
    id: int
    user_id: int
    name: str
    actionable_id: int
    actionable_type: str
    created_at: datetime


class ChapterPhoneNumber(BaseModel):
    phone_number: str
    assigned_user_count: int | None = None
    created_at: datetime
