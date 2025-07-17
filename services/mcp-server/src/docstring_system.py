"""Extensible docstring system using Jinja2 templates and decorators."""

import functools
import inspect
from typing import Any, Callable, Dict, Optional

from jinja2 import Environment, DictLoader
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
        self.templates = {}
        self._setup_templates()

    def _setup_templates(self):
        """Set up the default Jinja2 templates."""
        # Base template that can be used for any function
        base_template = '''{{ docstring_content }}

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
{% endif %}'''

        template_strings = {
            'chat_simple': base_template,
            'chat_with_history': base_template,
            '_default': base_template  # Default template for any function
        }

        self.env = Environment(loader=DictLoader(template_strings))

    def get_template(self, template_name: str):
        """Get a Jinja2 template by name.

        Parameters
        ----------
        template_name : str
            Name of the template to retrieve

        Returns
        -------
        jinja2.Template
            The requested template
        """
        try:
            return self.env.get_template(template_name)
        except Exception:
            # Fallback to default template if specific template not found
            return self.env.get_template('_default')

    def render_docstring(self, template_name: str, **kwargs) -> str:
        """Render a docstring using the specified template.

        Parameters
        ----------
        template_name : str
            Name of the template to use
        **kwargs
            Variables to pass to the template

        Returns
        -------
        str
            The rendered docstring
        """
        template = self.get_template(template_name)
        return template.render(**kwargs)


def extensible_docstring(config_prefix: str):
    """Decorator for creating extensible docstrings.

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
            if hasattr(instance, '__docstring_system'):
                docstring_system = instance.__docstring_system

                # Get docstring content from settings
                docstring_content = ""
                if hasattr(instance._settings, f"{config_prefix}_description"):
                    docstring_content = getattr(instance._settings, f"{config_prefix}_description")

                # Extract parameters from function signature
                sig = inspect.signature(func)
                parameters = []
                param_descriptions = {}

                # Get parameter descriptions from settings if available
                if hasattr(instance._settings, f"{config_prefix}_parameter_descriptions"):
                    param_descriptions = getattr(instance._settings, f"{config_prefix}_parameter_descriptions")

                # Build parameter list from function signature
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':  # Skip 'self' parameter
                        continue

                    # Get type annotation
                    param_type = "Any"
                    if param.annotation != inspect.Parameter.empty:
                        param_type = getattr(param.annotation, '__name__', str(param.annotation))

                    # Add default value info if present
                    if param.default != inspect.Parameter.empty:
                        if param.default is None:
                            param_type += ", optional"
                        else:
                            param_type += f", default={param.default}"

                    # Get description from settings or use default
                    description = param_descriptions.get(param_name, f"Parameter {param_name}")

                    parameters.append({
                        "name": param_name,
                        "type": param_type,
                        "description": description
                    })

                # Get return configuration from function signature and settings
                return_type = "Any"
                if func.__annotations__.get('return') is not None:
                    return_annotation = func.__annotations__['return']
                    return_type = getattr(return_annotation, '__name__', str(return_annotation))

                return_description = "Return value"
                if hasattr(instance._settings, f"{config_prefix}_returns"):
                    return_description = getattr(instance._settings, f"{config_prefix}_returns")

                returns = {"type": return_type, "description": return_description}

                # Get optional notes
                notes = ""
                if hasattr(instance._settings, f"{config_prefix}_notes"):
                    notes = getattr(instance._settings, f"{config_prefix}_notes")

                # Get optional examples
                examples = ""
                if hasattr(instance._settings, f"{config_prefix}_examples"):
                    examples = getattr(instance._settings, f"{config_prefix}_examples")

                # Render the docstring using the function name as template
                template_name = func.__name__
                rendered_docstring = docstring_system.render_docstring(
                    template_name,
                    docstring_content=docstring_content,
                    parameters=parameters,
                    returns=returns,
                    notes=notes,
                    examples=examples
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
        if hasattr(attr, '_update_docstring'):
            attr._update_docstring(instance)
