from pathlib import Path

from typing import Any
from jinja2 import Environment, FileSystemLoader

template_dir = Path(__file__).parent / "templates"

env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)


def render_template(template_name: str, **context: Any) -> str:

    template = env.get_template(template_name)
    return template.render(**context)
