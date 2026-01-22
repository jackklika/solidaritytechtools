from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from solidaritytechtools.client.models import (
    Activity,
    AgentAssignment,
    AgentAssignmentCreate,
    AgentAssignmentUpdate,
    AutomationEnrollmentCreate,
    Call,
    Chapter,
    ChapterPhoneNumber,
    CustomUserProperty,
    CustomUserPropertyCreate,
    CustomUserPropertyOptionCreate,
    DonationCharge,
    EmailBlast,
    EmailSender,
    Event,
    EventAttendance,
    EventAttendanceCreate,
    EventRsvp,
    EventRsvpCreate,
    EventRsvpUpdate,
    EventSession,
    EventSessionCreate,
    EventSessionUpdate,
    FieldSurveyUrlResponse,
    Organization,
    Page,
    PaginatedResponse,
    Phonebank,
    RelationshipType,
    ScheduledCall,
    ScheduledTask,
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    TaskAgent,
    TaskAssignment,
    TeamMember,
    TeamMemberCreate,
    TeamMemberUpdate,
    Text,
    Textbank,
    TextBlast,
    TextTemplate,
    TextTemplateCreate,
    TextTemplateUpdate,
    User,
    UserActionCreate,
    UserCreate,
    UserList,
    UserListCreate,
    UserListUpdate,
    UserNoteCreate,
    UserRelationshipCreate,
    UserUpdate,
)

T = TypeVar("T", bound=BaseModel)


class STError(Exception):
    """Base exception for Solidarity Tech API errors."""

    def __init__(self, message: str, status_code: int | None = None, details: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class STAuthError(STError):
    """Raised when authentication fails (401)."""

    pass


class STNotFoundError(STError):
    """Raised when a resource is not found (404)."""

    pass


class STValidationError(STError):
    """Raised when request validation fails (422)."""

    pass


class STRateLimitError(STError):
    """Raised when rate limit is exceeded (429)."""

    pass


class STClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.solidarity.tech/v1",
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.client.close()

    def _handle_response(self, response: httpx.Response):
        if response.is_success:
            return response

        status = response.status_code
        try:
            error_data = response.json()
            message = error_data.get("error") or error_data.get("message") or response.text
            details = error_data.get("details")
        except Exception:
            message = response.text
            details = None

        if status == 401:
            raise STAuthError(f"Authentication failed: {message}", status, details)
        elif status == 404:
            raise STNotFoundError(f"Resource not found: {message}", status, details)
        elif status == 422:
            raise STValidationError(f"Validation error: {message}", status, details)
        elif status == 429:
            raise STRateLimitError(f"Rate limit exceeded: {message}", status, details)
        else:
            raise STError(f"API request failed ({status}): {message}", status, details)

    def _get(self, path: str, params: dict | None = None) -> httpx.Response:
        response = self.client.get(path, params=params)
        return self._handle_response(response)

    def _post(
        self,
        path: str,
        json: dict | BaseModel | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        if isinstance(json, BaseModel):
            json = json.model_dump(exclude_unset=True, mode="json")
        response = self.client.post(path, json=json, params=params)
        return self._handle_response(response)

    def _put(self, path: str, json: dict | BaseModel | None = None) -> httpx.Response:
        if isinstance(json, BaseModel):
            json = json.model_dump(exclude_unset=True, mode="json")
        response = self.client.put(path, json=json)
        return self._handle_response(response)

    def _delete(self, path: str, params: dict | None = None) -> httpx.Response:
        response = self.client.delete(path, params=params)
        return self._handle_response(response)

    def _parse_item(self, response: httpx.Response, model_class: type[T]) -> T:
        data = response.json()
        item = data.get("data") if "data" in data and isinstance(data["data"], dict) else data
        return model_class.model_validate(item)

    def _parse_paginated(
        self, response: httpx.Response, item_class: type[T]
    ) -> PaginatedResponse[T]:
        return PaginatedResponse[item_class].model_validate(response.json())  # type: ignore

    # --- Users ---

    def get_users(
        self, limit: int = 20, offset: int = 0, since: int = 0, user_list_ids: str | None = None
    ) -> PaginatedResponse[User]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if user_list_ids:
            params["user_list_ids"] = user_list_ids
        return self._parse_paginated(self._get("/users", params=params), User)

    def get_user(self, user_id: int) -> User:
        return self._parse_item(self._get(f"/users/{user_id}"), User)

    def create_user(self, data: UserCreate | dict) -> User:
        return self._parse_item(self._post("/users", json=data), User)

    def update_user(self, user_id: int, data: UserUpdate | dict) -> User:
        return self._parse_item(self._put(f"/users/{user_id}", json=data), User)

    # --- Activities ---

    def get_activities(
        self, limit: int = 20, offset: int = 0, since: int = 0, user_id: int | None = None
    ) -> PaginatedResponse[Activity]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if user_id:
            params["user_id"] = user_id
        return self._parse_paginated(self._get("/activities", params=params), Activity)

    # --- Agent Assignments ---

    def get_agent_assignments(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> PaginatedResponse[AgentAssignment]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if user_id:
            params["user_id"] = user_id
        if agent_user_id:
            params["agent_user_id"] = agent_user_id
        return self._parse_paginated(
            self._get("/agent_assignments", params=params), AgentAssignment
        )

    def get_agent_assignment(self, assignment_id: int) -> AgentAssignment:
        return self._parse_item(self._get(f"/agent_assignments/{assignment_id}"), AgentAssignment)

    def create_agent_assignment(self, data: AgentAssignmentCreate | dict) -> AgentAssignment:
        return self._parse_item(self._post("/agent_assignments", json=data), AgentAssignment)

    def update_agent_assignment(
        self, assignment_id: int, data: AgentAssignmentUpdate | dict
    ) -> AgentAssignment:
        return self._parse_item(
            self._put(f"/agent_assignments/{assignment_id}", json=data), AgentAssignment
        )

    def delete_agent_assignment(self, assignment_id: int):
        self._delete(f"/agent_assignments/{assignment_id}")

    # --- Calls ---

    def get_calls(
        self, limit: int = 20, offset: int = 0, since: int = 0, user_id: int | None = None
    ) -> PaginatedResponse[Call]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if user_id:
            params["user_id"] = user_id
        return self._parse_paginated(self._get("/calls", params=params), Call)

    # --- Chapters ---

    def get_chapters(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> PaginatedResponse[Chapter]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        return self._parse_paginated(self._get("/chapters", params=params), Chapter)

    def get_chapter_phone_numbers(
        self, limit: int = 20, offset: int = 0, since: int = 0, chapter_id: int | None = None
    ) -> PaginatedResponse[ChapterPhoneNumber]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if chapter_id:
            params["chapter_id"] = chapter_id
        return self._parse_paginated(
            self._get("/chapter_phone_numbers", params=params), ChapterPhoneNumber
        )

    # --- Custom User Properties ---

    def get_custom_user_properties(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        scope_id: int | None = None,
        scope_type: str | None = None,
    ) -> PaginatedResponse[CustomUserProperty]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if scope_id:
            params["scope_id"] = scope_id
        if scope_type:
            params["scope_type"] = scope_type
        return self._parse_paginated(
            self._get("/custom_user_properties", params=params), CustomUserProperty
        )

    def create_custom_user_property(
        self, data: CustomUserPropertyCreate | dict
    ) -> CustomUserProperty:
        return self._parse_item(
            self._post("/custom_user_properties", json=data), CustomUserProperty
        )

    def create_custom_user_property_option(
        self, property_id: int, data: CustomUserPropertyOptionCreate | dict
    ) -> CustomUserProperty:
        return self._parse_item(
            self._post(f"/custom_user_properties/{property_id}/options", json=data),
            CustomUserProperty,
        )

    def delete_custom_user_property_option(
        self, property_id: int, option_value: str
    ) -> CustomUserProperty:
        return self._parse_item(
            self._delete(f"/custom_user_properties/{property_id}/options/{option_value}"),
            CustomUserProperty,
        )

    # --- Donation Charges ---

    def get_donation_charges(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> PaginatedResponse[DonationCharge]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        return self._parse_paginated(self._get("/donation_charges", params=params), DonationCharge)

    def get_donation_charge(self, charge_id: int) -> DonationCharge:
        return self._parse_item(self._get(f"/donation_charges/{charge_id}"), DonationCharge)

    # --- Events ---

    def get_events(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        scope_id: int | None = None,
        scope_type: str | None = None,
    ) -> PaginatedResponse[Event]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if scope_id:
            params["scope_id"] = scope_id
        if scope_type:
            params["scope_type"] = scope_type
        return self._parse_paginated(self._get("/events", params=params), Event)

    def get_event(self, event_id: int) -> Event:
        return self._parse_item(self._get(f"/events/{event_id}"), Event)

    def get_event_sessions(
        self, limit: int = 20, offset: int = 0, since: int = 0, event_id: int | None = None
    ) -> PaginatedResponse[EventSession]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if event_id:
            params["event_id"] = event_id
        return self._parse_paginated(self._get("/event_sessions", params=params), EventSession)

    def get_event_session(self, session_id: int) -> EventSession:
        return self._parse_item(self._get(f"/event_sessions/{session_id}"), EventSession)

    def create_event_session(self, data: EventSessionCreate | dict) -> EventSession:
        return self._parse_item(self._post("/event_sessions", json=data), EventSession)

    def update_event_session(
        self, session_id: int, data: EventSessionUpdate | dict
    ) -> EventSession:
        return self._parse_item(self._put(f"/event_sessions/{session_id}", json=data), EventSession)

    def delete_event_session(self, session_id: int):
        self._delete(f"/event_sessions/{session_id}")

    def get_event_rsvps(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        event_id: int | None = None,
        session_id: int | None = None,
    ) -> PaginatedResponse[EventRsvp]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if event_id:
            params["event_id"] = event_id
        if session_id:
            params["session_id"] = session_id
        return self._parse_paginated(self._get("/event_rsvps", params=params), EventRsvp)

    def get_event_rsvp(self, rsvp_id: int) -> EventRsvp:
        return self._parse_item(self._get(f"/event_rsvps/{rsvp_id}"), EventRsvp)

    def create_event_rsvp(self, data: EventRsvpCreate | dict) -> EventRsvp:
        return self._parse_item(self._post("/event_rsvps", json=data), EventRsvp)

    def update_event_rsvp(self, rsvp_id: int, data: EventRsvpUpdate | dict) -> EventRsvp:
        return self._parse_item(self._put(f"/event_rsvps/{rsvp_id}", json=data), EventRsvp)

    def delete_event_rsvp(self, rsvp_id: int):
        self._delete(f"/event_rsvps/{rsvp_id}")

    def get_event_attendances(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        event_id: int | None = None,
        session_id: int | None = None,
    ) -> PaginatedResponse[EventAttendance]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if event_id:
            params["event_id"] = event_id
        if session_id:
            params["session_id"] = session_id
        return self._parse_paginated(
            self._get("/event_attendances", params=params), EventAttendance
        )

    def create_event_attendance(self, data: EventAttendanceCreate | dict) -> EventAttendance:
        return self._parse_item(self._post("/event_attendances", json=data), EventAttendance)

    def delete_event_attendance(self, attendance_id: int):
        self._delete(f"/event_attendances/{attendance_id}")

    # --- User Actions ---

    def get_user_actions(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        user_id: int | None = None,
        page_id: int | None = None,
    ) -> PaginatedResponse[Any]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if user_id:
            params["user_id"] = user_id
        if page_id:
            params["page_id"] = page_id
        # Spec doesn't define response schema for GET /user_actions, assuming paginated
        return self._parse_paginated(self._get("/user_actions", params=params), BaseModel)

    def submit_user_action(self, data: UserActionCreate | dict):
        self._post("/user_actions", json=data)

    # --- Messaging ---

    def get_texts(
        self,
        limit: int = 20,
        offset: int = 0,
        since: str | None = None,
        user_id: int | None = None,
    ) -> PaginatedResponse[Text]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset}
        if since:
            params["_since"] = since
        if user_id:
            params["user_id"] = user_id
        return self._parse_paginated(self._get("/texts", params=params), Text)

    def create_text(self, user_id: int, body: str, media_urls: list[str] | None = None):
        params: dict[str, Any] = {"user_id": user_id, "body": body}
        if media_urls:
            params["media_urls"] = media_urls
        self._post("/texts", params=params)

    def send_email(self, user_id: int, subject: str, body_html: str, **kwargs):
        params = {"user_id": user_id, "subject": subject, "body_html": body_html, **kwargs}
        self._post("/emails", params=params)

    def get_email_senders(self, limit: int = 20, offset: int = 0) -> PaginatedResponse[EmailSender]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset}
        return self._parse_paginated(self._get("/email_senders", params=params), EmailSender)

    def get_email_blasts(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> PaginatedResponse[EmailBlast]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        return self._parse_paginated(self._get("/email_blasts", params=params), EmailBlast)

    def get_email_blast(self, blast_id: int) -> EmailBlast:
        return self._parse_item(self._get(f"/email_blasts/{blast_id}"), EmailBlast)

    # --- Scheduled Tasks ---

    def get_scheduled_tasks(
        self, limit: int = 20, offset: int = 0, since: int = 0, user_id: int | None = None
    ) -> PaginatedResponse[ScheduledTask]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if user_id:
            params["user_id"] = user_id
        return self._parse_paginated(self._get("/scheduled_tasks", params=params), ScheduledTask)

    def get_scheduled_task(self, task_id: int) -> ScheduledTask:
        return self._parse_item(self._get(f"/scheduled_tasks/{task_id}"), ScheduledTask)

    def create_scheduled_task(self, data: ScheduledTaskCreate | dict) -> ScheduledTask:
        return self._parse_item(self._post("/scheduled_tasks", json=data), ScheduledTask)

    def update_scheduled_task(
        self, task_id: int, data: ScheduledTaskUpdate | dict
    ) -> ScheduledTask:
        return self._parse_item(self._put(f"/scheduled_tasks/{task_id}", json=data), ScheduledTask)

    def delete_scheduled_task(self, task_id: int):
        self._delete(f"/scheduled_tasks/{task_id}")

    # --- User Notes ---

    def create_user_note(self, data: UserNoteCreate | dict):
        if isinstance(data, BaseModel):
            payload = data.model_dump(exclude_unset=True, mode="json")
        else:
            payload = data
        self._post("/user_notes", params=payload)

    def delete_user_note(self, note_id: int, user_id: int):
        self._delete(f"/user_notes/{note_id}", params={"user_id": user_id})

    # --- Organizations ---

    def get_organizations(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> PaginatedResponse[Organization]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        return self._parse_paginated(self._get("/organizations", params=params), Organization)

    def get_organization(self, org_id: int) -> Organization:
        return self._parse_item(self._get(f"/organizations/{org_id}"), Organization)

    # --- Automations ---

    def enroll_in_automation(self, data: AutomationEnrollmentCreate | dict):
        self._post("/automation_enrollments", json=data)

    # --- User Lists ---

    def get_user_lists(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> PaginatedResponse[UserList]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        return self._parse_paginated(self._get("/user_lists", params=params), UserList)

    def create_user_list(self, data: UserListCreate | dict) -> UserList:
        return self._parse_item(self._post("/user_lists", json=data), UserList)

    def get_user_list(self, list_id: int) -> UserList:
        return self._parse_item(self._get(f"/user_lists/{list_id}"), UserList)

    def update_user_list(self, list_id: int, data: UserListUpdate | dict) -> UserList:
        return self._parse_item(self._put(f"/user_lists/{list_id}", json=data), UserList)

    def delete_user_list(self, list_id: int):
        self._delete(f"/user_lists/{list_id}")

    # --- Relationships ---

    def get_relationship_types(self, user_id: int) -> list[RelationshipType]:
        response = self._get("/user_relationships", params={"user_id": user_id})
        return [RelationshipType.model_validate(item) for item in response.json()]

    def create_user_relationship(self, data: UserRelationshipCreate | dict):
        self._post(
            "/user_relationships",
            params=data if isinstance(data, dict) else data.model_dump(mode="json"),
        )

    def delete_user_relationship(self, relationship_id: int, user_id: int):
        self._delete(f"/user_relationships/{relationship_id}", params={"user_id": user_id})

    # --- Team Members ---

    def get_team_members(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> PaginatedResponse[TeamMember]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        return self._parse_paginated(self._get("/team_members", params=params), TeamMember)

    def create_team_member(self, data: TeamMemberCreate | dict) -> TeamMember:
        return self._parse_item(self._post("/team_members", json=data), TeamMember)

    def update_team_member(self, member_id: int, data: TeamMemberUpdate | dict) -> TeamMember:
        return self._parse_item(self._put(f"/team_members/{member_id}", json=data), TeamMember)

    # --- Text Templates ---

    def get_text_templates(
        self, limit: int = 20, offset: int = 0, since: int = 0, event_id: int | None = None
    ) -> PaginatedResponse[TextTemplate]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if event_id:
            params["event_id"] = event_id
        return self._parse_paginated(self._get("/text_templates", params=params), TextTemplate)

    def get_text_template(self, template_id: int) -> TextTemplate:
        return self._parse_item(self._get(f"/text_templates/{template_id}"), TextTemplate)

    def create_text_template(self, data: TextTemplateCreate | dict) -> TextTemplate:
        return self._parse_item(self._post("/text_templates", json=data), TextTemplate)

    def update_text_template(
        self, template_id: int, data: TextTemplateUpdate | dict
    ) -> TextTemplate:
        return self._parse_item(
            self._put(f"/text_templates/{template_id}", json=data), TextTemplate
        )

    def delete_text_template(self, template_id: int):
        self._delete(f"/text_templates/{template_id}")

    # --- Phonebanks & Textbanks ---

    def get_phonebanks(
        self, limit: int = 20, offset: int = 0, since: int = 0, event_id: int | None = None
    ) -> PaginatedResponse[Phonebank]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if event_id:
            params["event_id"] = event_id
        return self._parse_paginated(self._get("/phonebanks", params=params), Phonebank)

    def get_phonebank(self, phonebank_id: int) -> Phonebank:
        return self._parse_item(self._get(f"/phonebanks/{phonebank_id}"), Phonebank)

    def get_textbanks(
        self, limit: int = 20, offset: int = 0, since: int = 0, event_id: int | None = None
    ) -> PaginatedResponse[Textbank]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if event_id:
            params["event_id"] = event_id
        return self._parse_paginated(self._get("/textbanks", params=params), Textbank)

    def get_textbank(self, textbank_id: int) -> Textbank:
        return self._parse_item(self._get(f"/textbanks/{textbank_id}"), Textbank)

    def get_text_blasts(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> PaginatedResponse[TextBlast]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        return self._parse_paginated(self._get("/text_blasts", params=params), TextBlast)

    def get_text_blast(self, blast_id: int) -> TextBlast:
        return self._parse_item(self._get(f"/text_blasts/{blast_id}"), TextBlast)

    # --- Pages ---

    def get_pages(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> PaginatedResponse[Page]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        return self._parse_paginated(self._get("/pages", params=params), Page)

    def get_page(self, page_id: int) -> Page:
        return self._parse_item(self._get(f"/pages/{page_id}"), Page)

    # --- Scheduled Calls ---

    def get_scheduled_calls(
        self, limit: int = 20, offset: int = 0, since: int = 0, user_id: int | None = None
    ) -> PaginatedResponse[ScheduledCall]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset, "_since": since}
        if user_id:
            params["user_id"] = user_id
        return self._parse_paginated(self._get("/scheduled_calls", params=params), ScheduledCall)

    def get_scheduled_call(self, call_id: int) -> ScheduledCall:
        return self._parse_item(self._get(f"/scheduled_calls/{call_id}"), ScheduledCall)

    # --- Field Surveys ---

    def create_field_survey_url(
        self, user_id: int, agent_user_id: int, page_id: int
    ) -> FieldSurveyUrlResponse:
        payload = {"user_id": user_id, "agent_user_id": agent_user_id, "page_id": page_id}
        return self._parse_item(
            self._post("/field_survey_urls", json=payload), FieldSurveyUrlResponse
        )

    # --- Task Agents & Assignments ---

    def get_task_agents(
        self, limit: int = 20, offset: int = 0, task_id: int | None = None
    ) -> PaginatedResponse[TaskAgent]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset}
        if task_id:
            params["task_id"] = task_id
        return self._parse_paginated(self._get("/task_agents", params=params), TaskAgent)

    def get_task_agent(self, agent_id: int) -> TaskAgent:
        return self._parse_item(self._get(f"/task_agents/{agent_id}"), TaskAgent)

    def create_task_agent(self, user_id: int, task_id: int) -> TaskAgent:
        payload = {"user_id": user_id, "task_id": task_id}
        return self._parse_item(self._post("/task_agents", json=payload), TaskAgent)

    def delete_task_agent(self, agent_id: int):
        self._delete(f"/task_agents/{agent_id}")

    def get_task_assignments(
        self, limit: int = 20, offset: int = 0, task_id: int | None = None
    ) -> PaginatedResponse[TaskAssignment]:
        params: dict[str, Any] = {"_limit": limit, "_offset": offset}
        if task_id:
            params["task_id"] = task_id
        return self._parse_paginated(self._get("/task_assignments", params=params), TaskAssignment)

    def get_task_assignment(self, assignment_id: int) -> TaskAssignment:
        return self._parse_item(self._get(f"/task_assignments/{assignment_id}"), TaskAssignment)

    def create_task_assignment(
        self, user_id: int, task_id: int, agent_user_id: int | None = None
    ) -> TaskAssignment:
        payload: dict[str, Any] = {"user_id": user_id, "task_id": task_id}
        if agent_user_id:
            payload["agent_user_id"] = agent_user_id
        return self._parse_item(self._post("/task_assignments", json=payload), TaskAssignment)

    def update_task_assignment(self, assignment_id: int, agent_user_id: int) -> TaskAssignment:
        payload = {"agent_user_id": agent_user_id}
        return self._parse_item(
            self._put(f"/task_assignments/{assignment_id}", json=payload), TaskAssignment
        )

    def delete_task_assignment(self, assignment_id: int):
        self._delete(f"/task_assignments/{assignment_id}")
