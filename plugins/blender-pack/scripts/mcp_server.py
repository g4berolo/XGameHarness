"""Small stdio MCP adapter over the same Blender runner used by both engine skills."""
from __future__ import annotations
import base64
import json
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import inside
from runner import batch, doctor, live_request, live_start

OWNER = "mcp-" + uuid.uuid4().hex


def tool(name, description, properties, required=(), readonly=False):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False},
            "annotations": {"readOnlyHint": readonly, "destructiveHint": not readonly, "openWorldHint": not readonly}}


STRING = {"type": "string"}
TOOLS = [
    tool("blender_doctor", "Find local Blender and report its actual version. No modeling performed.", {}, readonly=True),
    tool("blender_job", "Run a batch build, inspect, multiview preview, or GLB/FBX export plus reimport. Input .blend is preserved. Build scripts execute with local user privileges, like shell code; inspect them first. Outputs go into a new revision under workspace/runs.",
         {"workspace": STRING, "action": {"enum": ["build", "inspect", "preview", "export"]}, "script": STRING, "blend": STRING,
          "timeout": {"type": "integer", "minimum": 1, "maximum": 3600}, "format": {"enum": ["glb", "fbx"]}, "max_triangles": {"type": "integer", "minimum": 0}}, ["workspace", "action"]),
    tool("blender_live_start", "Open a dedicated visible Blender working copy. This MCP session owns the workspace until stopped/closed; never attaches to unrelated unsaved scenes.", {"workspace": STRING, "blend": STRING}, ["workspace"]),
    tool("blender_live_command", "Inspect, execute Python in, save, or stop this session's Blender. Stop saves to a new .blend first. Python has local user privileges. If a request times out, inspect before retrying; it may have partially executed.",
         {"workspace": STRING, "action": {"enum": ["status", "exec", "save", "stop"]}, "script": STRING}, ["workspace", "action"]),
    tool("blender_image", "Read a PNG preview inside the asset workspace for actual visual review.", {"workspace": STRING, "path": STRING}, ["workspace", "path"], readonly=True),
]


def call(name, args):
    definition = next((t for t in TOOLS if t["name"] == name), None)
    if not definition:
        raise ValueError("Unknown tool")
    schema = definition["inputSchema"]
    if set(args) - set(schema["properties"]) or set(schema["required"]) - set(args):
        raise ValueError("Unexpected or missing arguments")
    for key, value in args.items():
        prop = schema["properties"][key]
        if prop.get("type") == "string" and not isinstance(value, str):
            raise ValueError(f"{key} must be a string")
        if prop.get("type") == "integer" and (type(value) is not int or value < prop.get("minimum", value) or value > prop.get("maximum", value)):
            raise ValueError(f"{key} must be an integer in range")
        if "enum" in prop and value not in prop["enum"]:
            raise ValueError(f"Invalid {key}")
    if name == "blender_doctor":
        result = doctor()
    elif name == "blender_job":
        result = batch(**args)
    elif name == "blender_live_start":
        result = live_start(owner=OWNER, **args)
    elif name == "blender_live_command":
        result = live_request(owner=OWNER, **args)
    else:
        path = inside(args["workspace"], args["path"])
        if path.suffix.lower() != ".png" or path.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("Expected a PNG up to 10 MiB inside workspace")
        data = path.read_bytes()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Not a PNG file")
        return {"content": [{"type": "image", "mimeType": "image/png", "data": base64.b64encode(data).decode()}]}
    return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}


def handle(message):
    if "id" not in message:
        return None
    method, params = message.get("method"), message.get("params", {})
    response = {"jsonrpc": "2.0", "id": message["id"]}
    if method == "initialize":
        requested = params.get("protocolVersion")
        response["result"] = {"protocolVersion": requested if requested in {"2024-11-05", "2025-03-26", "2025-06-18"} else "2025-06-18",
            "capabilities": {"tools": {}}, "serverInfo": {"name": "xgh-blender", "version": "1.0.0"}}
    elif method == "ping":
        response["result"] = {}
    elif method == "tools/list":
        response["result"] = {"tools": TOOLS}
    elif method == "tools/call":
        try:
            response["result"] = call(params["name"], params.get("arguments", {}))
        except Exception as exc:
            response["result"] = {"isError": True, "content": [{"type": "text", "text": str(exc)}]}
    else:
        response["error"] = {"code": -32601, "message": "Method not found"}
    return response


def main():
    for line in sys.stdin:
        try:
            if len(line) > 4 * 1024 * 1024:
                raise ValueError("Request exceeds 4 MiB")
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("Expected a JSON-RPC object")
            response = handle(message)
        except (ValueError, TypeError, KeyError) as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    main()
