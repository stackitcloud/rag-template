import sys
import os
from pathlib import Path

# Add project root and specific directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "admin-backend"))
sys.path.insert(0, str(project_root / "rag-backend"))
sys.path.insert(0, str(project_root / "document-extractor"))

# point at each rag-core library's src folder so their packages (admin_api_lib, rag_core_api, etc.) are importable
lib_root = project_root / "libs"
for lib in ["admin-api-lib", "rag-core-api", "rag-core-lib", "extractor-api-lib"]:
    sys.path.insert(0, str(lib_root / lib / "src"))
