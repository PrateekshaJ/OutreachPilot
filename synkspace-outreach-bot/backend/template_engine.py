"""
Jinja2-based email template rendering engine with multi-template support.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateError

TEMPLATES_DIR = Path(__file__).parent / "templates"


# Maps campaign template_type keys to file paths under templates/
TEMPLATE_MAP: dict[str, str] = {
    "founding_creator": "creators/founding_creator.html",
    "follow_up": "creators/follow_up.html",
    "brand_invite": "brands/brand_invite.html",
    "event_invite": "organizers/event_invite.html",
}


TEMPLATE_LABELS: dict[str, str] = {
    "founding_creator": "Founding Creator Invite",
    "follow_up": "Creator Follow Up",
    "brand_invite": "Brand Invite",
    "event_invite": "Event Organizer Invite",
    "custom": "Custom HTML Template",
}


class TemplateEngine:
    """Loads and renders HTML email templates with recipient-specific variables."""

    def __init__(self) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=True,
        )


    def list_templates(self) -> list[dict[str, str]]:
        """Return available templates for dropdown."""
        return [
            {"id": key, "label": value}
            for key, value in TEMPLATE_LABELS.items()
        ]


    def get_template_path(self, template_type: str) -> str:
        if template_type not in TEMPLATE_MAP:
            raise ValueError(
                f"Unknown template type '{template_type}'. "
                f"Valid types: {', '.join(TEMPLATE_MAP)}"
            )

        return TEMPLATE_MAP[template_type]


    def render_file(
        self,
        template_type: str,
        context: dict[str, Any]
    ) -> str:
        """Render a predefined template file."""

        template_path = self.get_template_path(template_type)

        try:
            template = self._env.get_template(template_path)
            return template.render(**context)

        except TemplateError as exc:
            raise ValueError(
                f"Template rendering failed: {exc}"
            ) from exc


    def render(
        self,
        template_html: str,
        context: dict[str, Any]
    ) -> str:
        """Render custom HTML template."""

        try:
            template = self._env.from_string(template_html)
            return template.render(**context)

        except TemplateError as exc:
            raise ValueError(
                f"Template rendering failed: {exc}"
            ) from exc


    def render_campaign(
        self,
        template_type: str,
        context: dict[str, Any],
        html_template: str | None = None,
    ) -> str:

        if template_type == "custom":
            if not html_template or not html_template.strip():
                raise ValueError(
                    "Custom template requires html_template."
                )

            return self.render(html_template, context)

        return self.render_file(template_type, context)


template_engine = TemplateEngine()