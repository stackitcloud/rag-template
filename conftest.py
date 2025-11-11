import sys
import os
from pathlib import Path

# Add project root and specific directories to Python path
project_root = Path(__file__).parent

# Add services src directories to Python path
services_root = project_root / "services"
for service in ["admin-backend", "rag-backend", "document-extractor", "mcp-server"]:
    service_src = services_root / service / "src"
    if service_src.exists():
        sys.path.insert(0, str(service_src))

# point at each rag-core library's src folder so their packages (admin_api_lib, rag_core_api, etc.) are importable
lib_root = project_root / "libs"
for lib in ["admin-api-lib", "rag-core-api", "rag-core-lib", "extractor-api-lib"]:
    sys.path.insert(0, str(lib_root / lib / "src"))
    sys.path.insert(0, str(lib_root / lib / "tests"))
