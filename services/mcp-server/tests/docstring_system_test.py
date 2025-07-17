import pytest

from src.docstring_system import DocstringTemplateSystem, extensible_docstring, setup_extensible_docstrings
from src.settings.mcp_settings import MCPSettings


# Fixtures
@pytest.fixture
def settings():
    """Create a default MCPSettings instance."""
    return MCPSettings()


@pytest.fixture
def docstring_system(settings):
    """Create a DocstringTemplateSystem instance."""
    return DocstringTemplateSystem(settings)


@pytest.fixture
def test_class_factory():
    """Factory fixture for creating test classes."""

    def _create_test_class(settings):
        class TestClass:
            def __init__(self, settings):
                self._settings = settings
                docstring_system = DocstringTemplateSystem(settings)
                setup_extensible_docstrings(self, docstring_system)

            @extensible_docstring("chat_simple")
            def chat_simple(self, session_id: str, message: str) -> str:
                return f"Response for {session_id}: {message}"

            @extensible_docstring("chat_with_history")
            def chat_with_history(self, session_id: str, message: str, history: list = None) -> dict:
                return {"answer": f"Response for {session_id}: {message}", "citations": []}

        return TestClass(settings)

    return _create_test_class


# Tests for DocstringTemplateSystem
def test_docstring_system_initialization(settings, docstring_system):
    """Test that DocstringTemplateSystem initializes correctly."""
    assert docstring_system.env is not None
    assert docstring_system.settings is not None
    assert docstring_system.settings == settings


def test_render_docstring_basic(docstring_system):
    """Test basic docstring rendering."""
    result = docstring_system.render_docstring(
        "chat_simple",
        docstring_content="Test description",
        parameters=[],
        returns={"type": "str", "description": "Test return"},
        notes="",
        examples="",
    )

    assert "Test description" in result
    assert "Parameters" in result
    assert "Returns" in result
    assert "str" in result
    assert "Test return" in result


def test_render_docstring_with_parameters(docstring_system):
    """Test docstring rendering with parameters."""
    parameters = [
        {"name": "param1", "type": "str", "description": "First parameter"},
        {"name": "param2", "type": "int", "description": "Second parameter"},
    ]

    result = docstring_system.render_docstring(
        "chat_simple",
        docstring_content="Test description",
        parameters=parameters,
        returns={"type": "str", "description": "Test return"},
        notes="",
        examples="",
    )

    assert "param1: str" in result
    assert "First parameter" in result
    assert "param2: int" in result
    assert "Second parameter" in result


def test_render_docstring_with_notes_and_examples(docstring_system):
    """Test docstring rendering with notes and examples."""
    result = docstring_system.render_docstring(
        "chat_simple",
        docstring_content="Test description",
        parameters=[],
        returns={"type": "str", "description": "Test return"},
        notes="This is a test note",
        examples=">>> example_function()\n'result'",
    )

    assert "Notes" in result
    assert "This is a test note" in result
    assert "Examples" in result
    assert ">>> example_function()" in result


def test_render_docstring_without_notes_and_examples(docstring_system):
    """Test docstring rendering without notes and examples."""
    result = docstring_system.render_docstring(
        "chat_simple",
        docstring_content="Test description",
        parameters=[],
        returns={"type": "str", "description": "Test return"},
        notes="",
        examples="",
    )

    assert "Notes" not in result
    assert "Examples" not in result


# Tests for extensible_docstring decorator
def test_decorator_creation():
    """Test that the decorator can be created."""
    decorator = extensible_docstring("chat_simple")
    assert decorator is not None

    # Test that it can decorate a function
    @decorator
    def test_function():
        pass

    assert test_function is not None
    assert hasattr(test_function, "_update_docstring")
    assert hasattr(test_function, "_original_func")


def test_decorator_preserves_function_metadata():
    """Test that the decorator preserves function metadata."""

    @extensible_docstring("chat_simple")
    def test_function(param1: str, param2: int) -> str:
        """Original docstring."""
        return "test"

    assert test_function.__name__ == "test_function"
    assert test_function._original_func.__name__ == "test_function"


def test_decorator_function_execution():
    """Test that decorated functions still execute correctly."""

    @extensible_docstring("chat_simple")
    def test_function(x: int) -> int:
        return x * 2

    result = test_function(5)
    assert result == 10


# Tests for MCPSettings
def test_default_settings(settings):
    """Test that default settings are loaded correctly."""
    # Test basic settings
    assert settings.host == "0.0.0.0"  # nosec S104 - test setting only
    assert settings.port == 8000
    assert settings.name == "RAG MCP server"

    # Test chat_simple settings
    assert settings.chat_simple_description is not None
    assert isinstance(settings.chat_simple_parameter_descriptions, dict)
    assert isinstance(settings.chat_simple_returns, str)
    assert settings.chat_simple_notes == ""
    assert settings.chat_simple_examples == ""

    # Test chat_with_history settings
    assert settings.chat_with_history_description is not None
    assert isinstance(settings.chat_with_history_parameter_descriptions, dict)
    assert isinstance(settings.chat_with_history_returns, str)
    assert settings.chat_with_history_notes == ""
    assert settings.chat_with_history_examples == ""


def test_parameter_descriptions():
    """Test parameter descriptions configuration."""
    param_descriptions = {"test_param": "Test description for parameter"}

    settings = MCPSettings(chat_simple_parameter_descriptions=param_descriptions)

    assert settings.chat_simple_parameter_descriptions == param_descriptions


def test_return_config():
    """Test return description configuration."""
    return_desc = "Test return description"
    assert return_desc == "Test return description"


def test_custom_settings():
    """Test custom settings override."""
    custom_param_descriptions = {"custom_param": "Custom parameter description"}
    custom_returns = "Custom return description"

    settings = MCPSettings(
        chat_simple_description="Custom description",
        chat_simple_parameter_descriptions=custom_param_descriptions,
        chat_simple_returns=custom_returns,
        chat_simple_notes="Custom notes",
        chat_simple_examples="Custom examples",
    )

    assert settings.chat_simple_description == "Custom description"
    assert settings.chat_simple_parameter_descriptions == custom_param_descriptions
    assert settings.chat_simple_returns == custom_returns
    assert settings.chat_simple_notes == "Custom notes"
    assert settings.chat_simple_examples == "Custom examples"


# Integration tests
def test_setup_extensible_docstrings(settings, test_class_factory):
    """Test that setup_extensible_docstrings works correctly."""
    instance = test_class_factory(settings)

    # Check that the docstring system is set up
    assert hasattr(instance, "__docstring_system")

    # Check that docstrings are generated
    assert instance.chat_simple.__doc__ is not None
    assert instance.chat_with_history.__doc__ is not None


def test_generated_docstrings_content(settings, test_class_factory):
    """Test that generated docstrings contain expected content."""
    instance = test_class_factory(settings)

    # Test chat_simple docstring
    simple_doc = instance.chat_simple.__doc__
    assert "Send a message to the RAG system" in simple_doc
    assert "Parameters" in simple_doc
    assert "session_id: str" in simple_doc
    assert "message: str" in simple_doc
    assert "Returns" in simple_doc
    assert "str" in simple_doc

    # Test chat_with_history docstring
    history_doc = instance.chat_with_history.__doc__
    assert "Send a message with conversation history" in history_doc
    assert "Parameters" in history_doc
    assert "session_id: str" in history_doc
    assert "message: str" in history_doc
    assert "history: list, optional" in history_doc
    assert "Returns" in history_doc
    assert "dict" in history_doc  # Return type from function signature


def test_custom_configuration(test_class_factory):
    """Test that custom configuration works."""
    # Create custom settings
    custom_settings = MCPSettings(
        chat_simple_description="Custom simple description",
        chat_simple_parameter_descriptions={
            "session_id": "Custom session parameter",
            "message": "Custom message parameter",
        },
        chat_simple_returns="Custom return value",
        chat_simple_notes="Custom notes section",
        chat_simple_examples=">>> custom_example()\n'result'",
    )

    instance = test_class_factory(custom_settings)

    # Check that custom content is in the docstring
    simple_doc = instance.chat_simple.__doc__
    assert "Custom simple description" in simple_doc
    assert "session_id: str" in simple_doc
    assert "Custom session parameter" in simple_doc
    assert "message: str" in simple_doc
    assert "Custom message parameter" in simple_doc
    assert "str" in simple_doc  # Return type from function signature
    assert "Custom return value" in simple_doc
    assert "Notes" in simple_doc
    assert "Custom notes section" in simple_doc
    assert "Examples" in simple_doc
    assert ">>> custom_example()" in simple_doc


def test_function_execution_still_works(settings, test_class_factory):
    """Test that decorated functions still execute correctly."""
    instance = test_class_factory(settings)

    # Test chat_simple execution
    result = instance.chat_simple("test_session", "test_message")
    assert result == "Response for test_session: test_message"

    # Test chat_with_history execution
    result = instance.chat_with_history("test_session", "test_message", [])
    expected = {"answer": "Response for test_session: test_message", "citations": []}
    assert result == expected


# Edge case tests
def test_missing_settings_attributes():
    """Test behavior when settings attributes are missing."""
    # Create minimal settings without some attributes
    settings = MCPSettings()

    # Remove some attributes to test handling
    delattr(settings, "chat_simple_notes")
    delattr(settings, "chat_simple_examples")

    class TestClass:
        def __init__(self, settings):
            self._settings = settings
            docstring_system = DocstringTemplateSystem(settings)
            setup_extensible_docstrings(self, docstring_system)

        @extensible_docstring("chat_simple")
        def test_method(self):
            pass

    # Should not raise an exception
    instance = TestClass(settings)
    assert instance.test_method.__doc__ is not None


def test_empty_configuration():
    """Test behavior with empty configuration."""
    settings = MCPSettings(
        chat_simple_description="", chat_simple_parameter_descriptions={}, chat_simple_notes="", chat_simple_examples=""
    )

    class TestClass:
        def __init__(self, settings):
            self._settings = settings
            docstring_system = DocstringTemplateSystem(settings)
            setup_extensible_docstrings(self, docstring_system)

        @extensible_docstring("chat_simple")
        def test_method(self):
            pass

    instance = TestClass(settings)
    doc = instance.test_method.__doc__

    # Should still have structure but with empty content
    assert "Parameters" in doc
    assert "Returns" in doc
    assert "Notes" not in doc
    assert "Examples" not in doc


if __name__ == "__main__":
    # Run pytest with verbose output
    pytest.main([__file__, "-v"])
