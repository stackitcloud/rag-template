"""Extensible docstring system using Jinja2 templates and decorators."""

import functools
import inspect
from typing import Callable

from jinja2 import Environment
from pydantic_settings import BaseSettings


class DocstringTemplateSystem:
    """System for managing extensible docstrings using Jinja2 templates."""

    def __init__(self, settings: BaseSettings):
        """Initialize the docstring template system.

        Parameters
        ----------
        settings : BaseSettings
            Settings object containing template configurations
        """
        self.settings = settings
        self._setup_templates()

    def render_docstring(self, template_name: str, **kwargs: dict) -> str:
        """Render a docstring using the template.

        Parameters
        ----------
        template_name : str
            Name of the template to render
        **kwargs : dict
            Keyword arguments to pass to the render function of the template

        Returns
        -------
        str
            Rendered docstring
        """
        return self.template.render(**kwargs)

    def _setup_templates(self):
        """Set up the default Jinja2 templates."""
        # Single template string
        self.template_string = """{{ docstring_content }}

Parameters
----------
{% for param in parameters %}
{{ param.name }}: {{ param.type }}
    {{ param.description }}
{% endfor %}

Returns
-------
{{ returns.type }}
    {{ returns.description }}
{% if notes %}

Notes
-----
{{ notes }}
{% endif %}
{% if examples %}

Examples
--------
{{ examples }}
{% endif %}"""

        self.env = Environment(autoescape=True)
        self.template = self.env.from_string(self.template_string)


def _extract_parameter_info(sig: inspect.Signature, param_descriptions: dict) -> list[dict]:
    """Extract parameter information from function signature.

    Parameters
    ----------
    sig : inspect.Signature
        Function signature to extract parameters from
    param_descriptions : dict
        Dictionary mapping parameter names to descriptions

    Returns
    -------
    list[dict]
        List of parameter dictionaries with name, type, and description
    """
    parameters = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":  # Skip 'self' parameter
            continue

        # Get type annotation
        param_type = "Any"
        if param.annotation != inspect.Parameter.empty:
            param_type = getattr(param.annotation, "__name__", str(param.annotation))

        # Add default value info if present
        if param.default != inspect.Parameter.empty:
            if param.default is None:
                param_type += ", optional"
            else:
                param_type += f", default={param.default}"

        # Get description from settings or use default
        description = param_descriptions.get(param_name, f"Parameter {param_name}")
        parameters.append({"name": param_name, "type": param_type, "description": description})

    return parameters


def _get_return_info(func: Callable, settings, config_prefix: str) -> dict:
    """Get return type and description information.

    Parameters
    ----------
    func : Callable
        Function to get return info for
    settings : object
        Settings object containing configuration
    config_prefix : str
        Configuration prefix for settings lookup

    Returns
    -------
    dict
        Dictionary with return type and description
    """
    return_type = "Any"
    if func.__annotations__.get("return") is not None:
        return_annotation = func.__annotations__["return"]
        return_type = getattr(return_annotation, "__name__", str(return_annotation))

    return_description = "Return value"
    if hasattr(settings, f"{config_prefix}_returns"):
        return_description = getattr(settings, f"{config_prefix}_returns")

    return {"type": return_type, "description": return_description}


def _get_settings_value(settings, config_prefix: str, suffix: str, default: str = "") -> str:
    """Get a value from settings with the given prefix and suffix.

    Parameters
    ----------
    settings : object
        Settings object to get value from
    config_prefix : str
        Configuration prefix
    suffix : str
        Configuration suffix
    default : str, optional
        Default value if setting not found

    Returns
    -------
    str
        The settings value or default
    """
    attr_name = f"{config_prefix}_{suffix}"
    if hasattr(settings, attr_name):
        return getattr(settings, attr_name)
    return default


def extensible_docstring(config_prefix: str):
    """Create an extensible docstring decorator.

    Parameters
    ----------
    config_prefix : str
        Prefix for configuration attributes in settings (e.g., "chat_simple")

    Returns
    -------
    Callable
        Decorated function with dynamic docstring
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Get the instance and settings from the method
        def update_docstring(instance):
            if not hasattr(instance, "__docstring_system"):
                return

            docstring_system = instance.__docstring_system

            # Get docstring content from settings
            docstring_content = _get_settings_value(instance._settings, config_prefix, "description")

            # Extract parameters from function signature
            sig = inspect.signature(func)
            param_descriptions = {}
            if hasattr(instance._settings, f"{config_prefix}_parameter_descriptions"):
                param_descriptions = getattr(instance._settings, f"{config_prefix}_parameter_descriptions")

            parameters = _extract_parameter_info(sig, param_descriptions)
            returns = _get_return_info(func, instance._settings, config_prefix)

            # Get optional notes and examples
            notes = _get_settings_value(instance._settings, config_prefix, "notes")
            examples = _get_settings_value(instance._settings, config_prefix, "examples")

            # Render the docstring using the function name as template
            template_name = func.__name__
            rendered_docstring = docstring_system.render_docstring(
                template_name,
                docstring_content=docstring_content,
                parameters=parameters,
                returns=returns,
                notes=notes,
                examples=examples,
            )

            wrapper.__doc__ = rendered_docstring

        # Store the update function for later use
        wrapper._update_docstring = update_docstring
        wrapper._original_func = func

        return wrapper

    return decorator


def setup_extensible_docstrings(instance, docstring_system: DocstringTemplateSystem):
    """Set up extensible docstrings for all decorated methods in an instance.

    Parameters
    ----------
    instance : object
        The instance to set up docstrings for
    docstring_system : DocstringTemplateSystem
        The docstring system to use for rendering
    """
    instance.__docstring_system = docstring_system

    # Find all methods with extensible docstrings and update them
    for attr_name in dir(instance):
        attr = getattr(instance, attr_name)
        if hasattr(attr, "_update_docstring"):
            attr._update_docstring(instance)
