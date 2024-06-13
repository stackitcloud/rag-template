from rag_core.main import app as perfect_rag_app, register_dependency_container

from use_case_container import UseCaseContainer


register_dependency_container(UseCaseContainer())
