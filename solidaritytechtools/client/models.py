"""Representation of models represented in the ST api (requests and responses)"""

from datetime import datetime
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

ScopeType = Literal["Organization", "Chapter"]


class PaginationMeta(BaseModel):
    """
    Metadata for paginated API responses.
    """

    total_count: int | None = None
    """Total number of records matching the query in the database."""

    limit: int | None = None
    """Maximum number of items requested in this page."""

    offset: int | None = None
    """Number of items skipped from the beginning of the result set."""


class PaginatedResponse[T](BaseModel):
    """
    Generic wrapper for API responses that return a list of items with pagination metadata.
    """

    data: list[T]
    meta: PaginationMeta | None = None


# --- Shared Components ---


class Address(BaseModel):
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class CustomPropertyOption(BaseModel):
    label: dict[str, str | None]
    value: str


# --- Entity Models ---


class User(BaseModel):
    id: int
    hash_id: str | None = None
    phone_number: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    preferred_language: str | None = None
    second_language: str | None = None
    chapter_id: int | None = None
    chapter_ids: list[int] = Field(default_factory=list)
    branch_id: int | None = None
    created_at: datetime | None = None
    custom_user_properties: dict[str, Any] = Field(default_factory=dict)
    address: Address | None = None
    sms_permission: bool = False
    call_permission: bool = False
    email_permission: bool = False


class Chapter(BaseModel):
    id: int
    name: str
    logo_url: str | None = None
    organization_id: int
    chapter_phone_number: str | None = None


class Organization(BaseModel):
    id: int | None = None
    name: str
    image_url: str | None = None
    parent_organization_id: int | None = None
    default_language: str | None = None
    supported_languages: list[str] | None = None


class UserNote(BaseModel):
    id: int
    content: str
    user_id: int


class CustomUserProperty(BaseModel):
    id: int
    name: str
    key: str
    field_type: str
    options: list[CustomPropertyOption] | None = None
    scope_id: int
    scope_type: ScopeType


class Call(BaseModel):
    id: int
    user_id: int
    direction: str
    agent_user_id: int | None = None
    duration: int
    picked_up: bool
    left_voicemail: bool
    twilio_call_sid: str | None = None
    created_at: datetime
    ended_at: datetime | None = None


class Text(BaseModel):
    id: int
    user_id: int
    direction: str
    body: str | None = None
    media_urls: list[str] = Field(default_factory=list)
    segment_size: int | None = None
    chapter_phone_number_id: int | None = None
    twilio_error_code: int | None = None
    created_at: datetime


class Activity(BaseModel):
    id: int
    user_id: int
    name: str
    actionable_id: int
    actionable_type: str
    action: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class EventSession(BaseModel):
    id: int | None = None
    event_id: int
    start_time: datetime | int
    end_time: datetime | int
    title: str | None = None
    location_name: str | None = None
    location_data: dict[str, Any] | None = None
    location_address: str | None = None
    show_rsvp_bar: bool | None = None
    show_title_in_form: bool | None = None
    note: str | None = None
    max_capacity: int | None = None
    tags: list[str] | None = None


class Event(BaseModel):
    id: int
    title: str
    scope_id: int
    scope_type: ScopeType
    event_type: str
    location_name: str | None = None
    location_data: dict[str, Any] | None = None
    rsvps_count: int | None = None
    attendance_count: int | None = None
    created_at: datetime


class EventRsvp(BaseModel):
    id: int | None = None
    event_id: int
    event_session_id: int
    user_id: int
    is_attending: Literal["yes", "no", "maybe"]
    is_confirmed: bool
    agent_user_id: int | None = None
    source: str | None = None
    source_system: str | None = None


class EventAttendance(BaseModel):
    id: int | None = None
    event_id: int
    event_session_id: int
    user_id: int
    attended: bool


class ScheduledTask(BaseModel):
    id: int | None = None
    due_at: datetime | str
    remind_at: datetime | str | None = None
    agent_user_id: int | None = None
    user_id: int
    notes: str | None = None
    task_type: str | None = None
    marked_as_completed: bool | None = None


class AgentAssignment(BaseModel):
    id: int | None = None
    user_id: int
    agent_user_id: int | None = None
    is_active: bool | None = None


class Page(BaseModel):
    id: int
    type: str
    url_slug: str
    name: str
    website_id: int
    is_published: bool
    full_url: str
    scope_id: int
    scope_type: ScopeType
    supported_languages: list[str]
    requires_user: bool
    created_at: datetime
    form: list[dict[str, Any]] | None = None


class UserList(BaseModel):
    id: int | None = None
    name: str
    parameters: dict[str, Any]
    user_id: int | None = None
    scope_id: int
    scope_type: ScopeType
    event_id: int | None = None
    created_at: datetime | None = None


class ChapterPhoneNumber(BaseModel):
    phone_number: str
    assigned_user_count: int
    chapters: list[Chapter] = Field(default_factory=list)
    created_at: datetime


class EmailBlast(BaseModel):
    id: int
    name: str
    subject: dict[str, str]
    from_email: str = Field(alias="from")
    results: dict[str, int]
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)


class EmailSender(BaseModel):
    id: int
    name: str
    email: str
    from_name: str = Field(alias="from")
    default_for_scope: bool
    scope_type: str
    scope_id: int
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)


class TextBlast(BaseModel):
    id: int
    name: str
    content: dict[str, str]
    results: dict[str, int]
    created_at: datetime


class TextTemplate(BaseModel):
    id: int | None = None
    name: str
    scope_id: int
    scope_type: ScopeType
    template: dict[str, str]
    event_id: int | None = None
    created_at: datetime | None = None


class TeamMember(BaseModel):
    id: int
    user_id: int
    scope_id: int
    scope_type: ScopeType
    created_at: datetime


class TaskAgent(BaseModel):
    id: int
    user_id: int
    task_id: int
    created_at: datetime


class TaskAssignment(BaseModel):
    id: int
    user_id: int
    task_id: int
    agent_user_id: int
    created_at: datetime


class ScheduledCall(BaseModel):
    user_id: int
    agent_user_id: int | None = None
    call_time: datetime
    page_id: int
    created_at: datetime


class DonationCharge(BaseModel):
    id: int
    amount: int
    success: bool
    refunded: bool
    created_at: datetime
    user: dict[str, Any] | None = None


class Phonebank(BaseModel):
    id: int
    title: str
    medium: str
    begins_at: datetime
    ends_at: datetime | None = None
    targets: str
    mobilize_event_id: int | None = None
    created_at: datetime


class Textbank(BaseModel):
    id: int
    title: str
    medium: str
    begins_at: datetime
    ends_at: datetime | None = None
    targets: str
    mobilize_event_id: int | None = None
    created_at: datetime


class RelationshipType(BaseModel):
    id: str
    text: str


# --- Request Models (Create/Update) ---


class UserCreate(BaseModel):
    phone_number: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    preferred_language: str = "en"
    second_language: str | None = None
    chapter_id: int | None = None
    chapter_ids: list[int] | None = None
    referred_by_user_id: int | None = None
    custom_user_properties: dict[str, str] | None = None
    add_tags: list[str] | None = None
    remove_tags: list[str] | None = None
    address: Address | None = None
    sms_permission: bool | None = None
    call_permission: bool | None = None
    email_permission: bool | None = None
    timezone: str | None = None
    require_contact_info: bool | None = None
    phone_number_textable_validation: bool | None = None


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
    address: Address | None = None
    sms_permission: bool | None = None
    call_permission: bool | None = None
    email_permission: bool | None = None
    timezone: str | None = None


class AgentAssignmentCreate(BaseModel):
    user_id: int
    agent_user_id: int
    is_active: bool | None = True


class AgentAssignmentUpdate(BaseModel):
    user_id: int | None = None
    agent_user_id: int | None = None
    is_active: bool | None = None


class AutomationEnrollmentCreate(BaseModel):
    automation_id: int
    user_id: int


class CustomUserPropertyCreate(BaseModel):
    label: str
    description: str | None = None
    field_type: Literal[
        "input", "textarea", "number", "date", "checkbox", "select", "radios", "checkboxes"
    ]
    options: list[dict[str, Any]] | None = None
    scope_type: ScopeType
    scope_id: int


class CustomUserPropertyOptionCreate(BaseModel):
    label: dict[str, str]
    value: str | None = None


class EventSessionCreate(BaseModel):
    event_id: int
    start_time: int
    end_time: int
    title: str | None = None
    location_name: str | None = None
    location_address: str | None = None
    show_rsvp_bar: bool | None = None
    show_title_in_form: bool | None = None
    note: str | None = None
    max_capacity: int | None = None
    tags: list[str] | None = None


class EventSessionUpdate(BaseModel):
    start_time: int | None = None
    end_time: int | None = None
    title: str | None = None
    location_name: str | None = None
    location_address: str | None = None
    show_rsvp_bar: bool | None = None
    show_title_in_form: bool | None = None
    note: str | None = None
    max_capacity: int | None = None
    tags: list[str] | None = None


class EventRsvpCreate(BaseModel):
    event_id: int
    event_session_id: int
    user_id: int
    is_attending: Literal["yes", "no", "maybe"]
    is_confirmed: bool
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


class EventAttendanceCreate(BaseModel):
    event_id: int
    event_session_id: int
    user_id: int
    attended: bool


class ScheduledTaskCreate(BaseModel):
    due_at: str | int
    remind_at: str | int | None = None
    agent_user_id: int | None = None
    user_id: int
    notes: str | None = None
    marked_as_completed: bool | None = False


class ScheduledTaskUpdate(BaseModel):
    due_at: str | int | None = None
    remind_at: str | int | None = None
    agent_user_id: int | None = None
    user_id: int | None = None
    notes: str | None = None
    marked_as_completed: bool | None = None


class TeamMemberCreate(BaseModel):
    member_id: str | None = None
    phone_number: str | None = None
    email: str | None = None
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role_id: int
    scope_type: ScopeType
    scope_id: int
    invite_via: Literal["sms", "email"]
    task_id: int | None = None


class TeamMemberUpdate(BaseModel):
    role_id: int
    scope_type: ScopeType
    scope_id: int


class TextTemplateCreate(BaseModel):
    name: str
    scope_id: int
    scope_type: ScopeType
    template: dict[str, str]
    event_id: int | None = None


class TextTemplateUpdate(BaseModel):
    name: str | None = None
    scope_id: int | None = None
    scope_type: ScopeType | None = None
    template: dict[str, str] | None = None
    event_id: int | None = None


class UserListCreate(BaseModel):
    name: str
    scope_id: int
    scope_type: ScopeType
    event_id: int | None = None
    user_id: int | None = None
    parameters: dict[str, Any]


class UserListUpdate(BaseModel):
    name: str | None = None
    scope_id: int | None = None
    scope_type: ScopeType | None = None
    parameters: dict[str, Any] | None = None
    event_id: int | None = None


class UserNoteCreate(BaseModel):
    user_id: int
    agent_id: int | None = None
    content: str
    created_at: int | None = None


class UserActionData(BaseModel):
    phone_number: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    preferred_language: str | None = None
    second_language: str | None = None
    chapter_id: int | None = None
    address: Address | None = None
    sms_permission: bool | None = None
    call_permission: bool | None = None
    email_permission: bool | None = None
    custom_user_properties: dict[str, str] | None = None


class UserActionCreate(BaseModel):
    page_id: int
    user_id: int | None = None
    created_at: int | None = None
    data: UserActionData | None = None


class UserRelationshipCreate(BaseModel):
    user_id: int
    related_user_id: int
    relationship_type: str


class FieldSurveyUrlResponse(BaseModel):
    url: str
    expires_at: datetime
