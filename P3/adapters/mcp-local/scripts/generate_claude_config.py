"""Print a configuration snippet; NEVER edits Claude Desktop settings."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
obj={'mcpServers':{'aiaeao-cube':{
    'command':str(Path(sys.executable).absolute()),
    'args':['-u',str((root/'run_server.py').resolve())]
}}}
print(json.dumps(obj,indent=2,ensure_ascii=False))
