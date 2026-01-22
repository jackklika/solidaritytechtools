from typing import Any, Final

import httpx
from pydantic import BaseModel

from .models import (
    EventRsvpCreate,
    EventRsvpUpdate,
    ScheduledTaskCreate,
    UserCreate,
    UserNoteCreate,
    UserUpdate,
)

DEFAULT_V1_ST_API_BASE_URL: Final[str] = "https://api.solidarity.tech/v1/"


class STClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initializes the Solidarity Tech API client.

        Args:
            api_key: Optional API key. If not provided, it will be loaded
                from the ST_API_KEY env var.
            base_url: Optional base URL. If not provided, it will be loaded o
                from ST_BASE_URL env var or default.
        """
        if not api_key:
            raise ValueError("Must pass api_key")
        self.api_key: str = api_key

        if not base_url:
            base_url = DEFAULT_V1_ST_API_BASE_URL
        self.base_url: str = base_url

        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            },
        )

    # --- HTTP Helpers ---

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        response = self._client.post(path, json=json)
        response.raise_for_status()
        return response.json()

    def _put(self, path: str, json: dict[str, Any] | None = None) -> Any:
        response = self._client.put(path, json=json)
        response.raise_for_status()
        return response.json()

    def _delete(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self._client.delete(path, params=params)
        response.raise_for_status()
        return response.json()

    def _build_params(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = {"_limit": limit, "_offset": offset, "_since": since}
        if extra:
            params.update({k: v for k, v in extra.items() if v is not None})
        return params

    def _to_dict(self, data: BaseModel | dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, BaseModel):
            return data.model_dump(exclude_unset=True)
        return data

    # --- Users ---

    def get_users(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        user_list_ids: list[int] | str | None = None,
    ) -> list[dict[str, Any]]:
        extra = {}
        if user_list_ids:
            extra["user_list_ids"] = (
                ",".join([str(i) for i in user_list_ids])
                if isinstance(user_list_ids, list)
                else user_list_ids
            )
        params = self._build_params(limit, offset, since, extra)
        return self._get("users", params=params)

    def get_user(self, user_id: int) -> dict[str, Any]:
        return self._get(f"users/{user_id}")

    def create_user(self, user_data: UserCreate | dict[str, Any]) -> dict[str, Any]:
        return self._post("users", json=self._to_dict(user_data))

    def update_user(self, user_id: int, user_data: UserUpdate | dict[str, Any]) -> dict[str, Any]:
        return self._put(f"users/{user_id}", json=self._to_dict(user_data))

    # --- Activities ---

    def get_activities(self, limit: int = 20, offset: int = 0, since: int = 0) -> dict[str, Any]:
        return self._get("activities", params=self._build_params(limit, offset, since))

    # --- Agent Assignments ---

    def get_agent_assignments(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> list[dict[str, Any]]:
        extra = {"user_id": user_id, "agent_user_id": agent_user_id}
        params = self._build_params(limit, offset, since, extra)
        return self._get("agent_assignments", params=params)

    def create_agent_assignment(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._post("agent_assignments", json=data)

    def update_agent_assignment(self, assignment_id: int, data: dict[str, Any]) -> dict[str, Any]:
        return self._put(f"agent_assignments/{assignment_id}", json=data)

    def delete_agent_assignment(self, assignment_id: int) -> dict[str, Any]:
        return self._delete(f"agent_assignments/{assignment_id}")

    # --- Calls ---

    def get_calls(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        user_id: int | None = None,
    ) -> list[dict[str, Any]]:
        extra = {"user_id": user_id}
        params = self._build_params(limit, offset, since, extra)
        return self._get("calls", params=params)

    # --- Chapters ---

    def get_chapters(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("chapters", params=self._build_params(limit, offset, since))

    def get_chapter_phone_numbers(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("chapter_phone_numbers", params=self._build_params(limit, offset, since))

    # --- Custom User Properties ---

    def get_custom_user_properties(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("custom_user_properties", params=self._build_params(limit, offset, since))

    # --- Donations ---

    def get_donation_charges(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("donation_charges", params=self._build_params(limit, offset, since))

    def get_donation_charge(self, charge_id: int) -> dict[str, Any]:
        return self._get(f"donation_charges/{charge_id}")

    # --- Events & RSVPs ---

    def get_events(self, limit: int = 20, offset: int = 0, since: int = 0) -> list[dict[str, Any]]:
        return self._get("events", params=self._build_params(limit, offset, since))

    def get_event(self, event_id: int) -> dict[str, Any]:
        return self._get(f"events/{event_id}")

    def get_event_sessions(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("event_sessions", params=self._build_params(limit, offset, since))

    def get_event_rsvps(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        event_id: int | None = None,
        user_id: int | None = None,
    ) -> list[dict[str, Any]]:
        extra = {"event_id": event_id, "user_id": user_id}
        params = self._build_params(limit, offset, since, extra)
        return self._get("event_rsvps", params=params)

    def create_event_rsvp(self, rsvp_data: EventRsvpCreate | dict[str, Any]) -> dict[str, Any]:
        return self._post("event_rsvps", json=self._to_dict(rsvp_data))

    def update_event_rsvp(
        self, rsvp_id: int, rsvp_data: EventRsvpUpdate | dict[str, Any]
    ) -> dict[str, Any]:
        return self._put(f"event_rsvps/{rsvp_id}", json=self._to_dict(rsvp_data))

    # --- User Actions ---

    def submit_user_action(self, action_data: dict[str, Any]) -> dict[str, Any]:
        """
        Submits a user action (e.g., form submission, petition signature).
        Matches POST /user_actions.
        """
        return self._post("user_actions", json=action_data)

    # --- Texts ---

    def get_texts(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        user_id: int | None = None,
    ) -> list[dict[str, Any]]:
        extra = {"user_id": user_id}
        params = self._build_params(limit, offset, since, extra)
        return self._get("texts", params=params)

    def create_text(self, text_data: dict[str, Any]) -> dict[str, Any]:
        return self._post("texts", json=text_data)

    # --- Emails ---

    def send_email(self, email_data: dict[str, Any]) -> dict[str, Any]:
        return self._post("emails", json=email_data)

    def get_email_blasts(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("email_blasts", params=self._build_params(limit, offset, since))

    # --- Scheduled Tasks ---

    def get_scheduled_tasks(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> list[dict[str, Any]]:
        extra = {"user_id": user_id, "agent_user_id": agent_user_id}
        params = self._build_params(limit, offset, since, extra)
        return self._get("scheduled_tasks", params=params)

    def create_scheduled_task(
        self, task_data: ScheduledTaskCreate | dict[str, Any]
    ) -> dict[str, Any]:
        return self._post("scheduled_tasks", json=self._to_dict(task_data))

    def update_scheduled_task(self, task_id: int, task_data: dict[str, Any]) -> dict[str, Any]:
        return self._put(f"scheduled_tasks/{task_id}", json=task_data)

    # --- User Notes ---

    def create_user_note(self, note_data: UserNoteCreate | dict[str, Any]) -> dict[str, Any]:
        return self._post("user_notes", json=self._to_dict(note_data))

    def delete_user_note(self, note_id: int) -> dict[str, Any]:
        return self._delete(f"user_notes/{note_id}")

    # --- Organizations ---

    def get_organizations(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("organizations", params=self._build_params(limit, offset, since))

    # --- Automation Enrollments ---

    def enroll_in_automation(self, enrollment_data: dict[str, Any]) -> dict[str, Any]:
        return self._post("automation_enrollments", json=enrollment_data)

    # --- Phonebanks & Textbanks ---

    def get_phonebanks(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("phonebanks", params=self._build_params(limit, offset, since))

    def get_phonebank(self, phonebank_id: int) -> dict[str, Any]:
        return self._get(f"phonebanks/{phonebank_id}")

    def get_textbanks(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("textbanks", params=self._build_params(limit, offset, since))

    def get_textbank(self, textbank_id: int) -> dict[str, Any]:
        return self._get(f"textbanks/{textbank_id}")

    def get_text_blasts(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("text_blasts", params=self._build_params(limit, offset, since))

    def get_text_blast(self, text_blast_id: int) -> dict[str, Any]:
        return self._get(f"text_blasts/{text_blast_id}")

    # --- User Lists ---

    def get_user_lists(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("user_lists", params=self._build_params(limit, offset, since))

    def create_user_list(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._post("user_lists", json=data)

    def get_user_list(self, list_id: int) -> dict[str, Any]:
        return self._get(f"user_lists/{list_id}")

    def update_user_list(self, list_id: int, data: dict[str, Any]) -> dict[str, Any]:
        return self._put(f"user_lists/{list_id}", json=data)

    def delete_user_list(self, list_id: int) -> dict[str, Any]:
        return self._delete(f"user_lists/{list_id}")

    # --- Relationships ---

    def get_user_relationships(self, user_id: int) -> list[dict[str, Any]]:
        return self._get("user_relationships", params={"user_id": user_id})

    def create_user_relationship(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._post("user_relationships", json=data)

    def delete_user_relationship(self, relationship_id: int, user_id: int) -> dict[str, Any]:
        return self._delete(f"user_relationships/{relationship_id}", params={"user_id": user_id})

    # --- Task Agents & Assignments ---

    def get_task_agents(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("task_agents", params=self._build_params(limit, offset, since))

    def create_task_agent(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._post("task_agents", json=data)

    def get_task_agent(self, agent_id: int) -> dict[str, Any]:
        return self._get(f"task_agents/{agent_id}")

    def delete_task_agent(self, agent_id: int) -> dict[str, Any]:
        return self._delete(f"task_agents/{agent_id}")

    def get_task_assignments(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("task_assignments", params=self._build_params(limit, offset, since))

    def create_task_assignment(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._post("task_assignments", json=data)

    def get_task_assignment(self, assignment_id: int) -> dict[str, Any]:
        return self._get(f"task_assignments/{assignment_id}")

    def update_task_assignment(self, assignment_id: int, data: dict[str, Any]) -> dict[str, Any]:
        return self._put(f"task_assignments/{assignment_id}", json=data)

    def delete_task_assignment(self, assignment_id: int) -> dict[str, Any]:
        return self._delete(f"task_assignments/{assignment_id}")

    # --- Team Members ---

    def get_team_members(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("team_members", params=self._build_params(limit, offset, since))

    def create_team_member(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._post("team_members", json=data)

    def update_team_member(self, member_id: int, data: dict[str, Any]) -> dict[str, Any]:
        return self._put(f"team_members/{member_id}", json=data)

    # --- Text Templates ---

    def get_text_templates(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("text_templates", params=self._build_params(limit, offset, since))

    def create_text_template(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._post("text_templates", json=data)

    def get_text_template(self, template_id: int) -> dict[str, Any]:
        return self._get(f"text_templates/{template_id}")

    def update_text_template(self, template_id: int, data: dict[str, Any]) -> dict[str, Any]:
        return self._put(f"text_templates/{template_id}", json=data)

    def delete_text_template(self, template_id: int) -> dict[str, Any]:
        return self._delete(f"text_templates/{template_id}")

    # --- Scheduled Calls ---

    def get_scheduled_calls(
        self, limit: int = 20, offset: int = 0, since: int = 0
    ) -> list[dict[str, Any]]:
        return self._get("scheduled_calls", params=self._build_params(limit, offset, since))

    def get_scheduled_call(self, call_id: int) -> dict[str, Any]:
        return self._get(f"scheduled_calls/{call_id}")

    # --- Other ---

    def create_field_survey_url(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._post("field_survey_urls", json=data)

    def create_custom_user_property_option(
        self, property_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return self._post(f"custom_user_properties/{property_id}/options", json=data)

    def delete_custom_user_property_option(
        self, property_id: int, option_id: int
    ) -> dict[str, Any]:
        return self._delete(f"custom_user_properties/{property_id}/options/{option_id}")

    # --- Lifecycle ---

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()

    def close(self):
        """Closes the underlying httpx client."""
        self._client.close()
