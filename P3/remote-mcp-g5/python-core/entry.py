"""Private Python Worker: no public route, only Cloudflare Service Binding."""
import json
from workers import WorkerEntrypoint, Response
from core_runtime import wire_call

MAX_WIRE_BYTES = 2 * 1024 * 1024 + 4096

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method != 'POST' or request.url.split('?')[0].split('/')[-1] != 'execute':
            return Response('Not Found',status=404)
        try:
            raw = await request.text()
            if len(raw.encode('utf-8')) > MAX_WIRE_BYTES:
                return Response('Payload too large',status=413)
            payload = json.loads(raw)
            result = wire_call(payload)
            return Response(json.dumps(result,ensure_ascii=False,sort_keys=True,allow_nan=False),
                            headers={'content-type':'application/json;charset=utf-8',
                                     'cache-control':'no-store', 'x-content-type-options':'nosniff'})
        except (ValueError,UnicodeError,TypeError,RecursionError):
            return Response('{"ok":false,"diagnostic":{"code":"G5_JSON_INVALID","message":"Invalid JSON"}}',
                            status=400, headers={'content-type':'application/json'})
