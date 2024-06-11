import uvicorn
from dependency_injector.providers import Singleton
from rag_core.main import app, register_dependency

if __name__ == "__main__":
    uvicorn.run(app)
