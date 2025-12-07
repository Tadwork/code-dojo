#!/usr/bin/env python3
"""Generate OpenAPI specification file from FastAPI app."""

import json
import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

try:
    import yaml
except ImportError:
    yaml = None
    print("Warning: PyYAML not installed. Only JSON format will be available.")


def generate_openapi_json(output_path: Path):
    """Generate OpenAPI specification in JSON format."""
    openapi_schema = app.openapi()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI JSON specification generated: {output_path}")


def generate_openapi_yaml(output_path: Path):
    """Generate OpenAPI specification in YAML format."""
    if not yaml:
        print("❌ PyYAML not installed. Skipping YAML generation.")
        return
    
    openapi_schema = app.openapi()
    yaml_content = yaml.dump(openapi_schema, default_flow_style=False, sort_keys=False)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    
    print(f"✅ OpenAPI YAML specification generated: {output_path}")


def main():
    """Main function."""
    backend_dir = Path(__file__).parent.parent
    output_dir = backend_dir / "openapi"
    output_dir.mkdir(exist_ok=True)
    
    json_path = output_dir / "openapi.json"
    yaml_path = output_dir / "openapi.yaml"
    
    generate_openapi_json(json_path)
    generate_openapi_yaml(yaml_path)
    
    print(f"\n📄 OpenAPI specifications available at:")
    print(f"   - {json_path}")
    if yaml:
        print(f"   - {yaml_path}")
    print(f"\n🌐 Also accessible via API:")
    print(f"   - http://localhost:8000/api/openapi.json")
    print(f"   - http://localhost:8000/api/openapi.yaml")
    print(f"   - http://localhost:8000/docs (Interactive Swagger UI)")
    print(f"   - http://localhost:8000/redoc (ReDoc documentation)")


if __name__ == "__main__":
    main()

