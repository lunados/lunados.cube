"""P1.2 strict deterministic ACG parser and P0 AST shape checker.

Only syntax and AST structure. Never resolves concepts, referents, predicates,
methods, authorization, historical truth, or a Core runtime contract.
No third-party runtime dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import math
import hashlib
import json
import re
from typing import Any

MAX_SOURCE_BYTES = 1_048_576
MAX_DEPTH = 64
MAX_NODES = 10_000
MAX_PARAMS = 64
MAX_QUALIFIERS = 64
WS = " \t\r\n"
METHOD = re.compile(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*/v[1-9][0-9]*", re.ASCII)
PARAM = re.compile(r"[A-Za-z_][A-Za-z0-9_]*", re.ASCII)
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", re.ASCII)
KINDS = frozenset(("reference", "qualified", "relation", "application"))
HOME = frozenset(("X", "Y", "Z"))
LAYER = frozenset(("α", "β", "ζ"))
QUALIFIER = frozenset(("T", "F", "M", "O"))
KEY_FORBIDDEN = frozenset("[]():;,=@\"\\")


class ParseError(Exception):
    """Stable diagnostics with UTF-8 span in source text where available."""
    def __init__(self, code: str, message: str, index: int = 0, *, end: int | None = None, stage: str = "syntax") -> None:
        super().__init__(message)
        self.code, self.message, self.index, self.end, self.stage = code, message, index, end, stage


@dataclass
class ResourceBudget:
    nodes: int = 0

    def add(self, position: int = 0) -> None:
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise ParseError("P1_INPUT_LIMIT", "Maximum AST node count exceeded (10000).", position)


def _decode_source(source: bytes) -> str:
    if len(source) > MAX_SOURCE_BYTES:
        raise ParseError("P1_INPUT_LIMIT", "Input exceeds 1048576 UTF-8 bytes.")
    try:
        s = source.decode("utf-8", errors="strict")
    except UnicodeDecodeError as e:
        # Byte offset; reporter recognizes a decoding failure specially.
        raise ParseError("P1_INVALID_UTF8", "Input is not valid UTF-8.", e.start, end=e.end) from e
    if s.startswith("\ufeff"):
        raise ParseError("P1_INVALID_UTF8", "UTF-8 BOM is not permitted.", 0, end=3)
    # UTF-8 itself cannot contain literal surrogate codepoints.
    return s


def _has_surrogate(s: str) -> bool:
    return any(0xD800 <= ord(c) <= 0xDFFF for c in s)


def _valid_concept_key(s: str) -> bool:
    return bool(s) and not any(c.isspace() or c in KEY_FORBIDDEN or ord(c) < 0x20 or _has_surrogate(c) for c in s)


class Parser:
    def __init__(self, source: str) -> None:
        self.text = source
        self.i = 0
        self.budget = ResourceBudget()
        self.decoder = json.JSONDecoder(strict=True, parse_int=Decimal, parse_float=Decimal)

    def error(self, msg: str, *, code: str = "P1_SYNTAX", start: int | None = None, end: int | None = None) -> None:
        raise ParseError(code, msg, self.i if start is None else start, end=end)

    def skip_ws(self) -> None:
        n, s = len(self.text), self.text
        while self.i < n and s[self.i] in WS:
            self.i += 1

    def consume(self, expected: str) -> bool:
        self.skip_ws()
        if self.text.startswith(expected, self.i):
            self.i += len(expected)
            return True
        return False

    def expect(self, expected: str) -> None:
        if not self.consume(expected):
            self.error(f"Expected {expected!r}.")

    def string(self) -> str:
        self.skip_ws()
        start = self.i
        if self.i >= len(self.text) or self.text[self.i] != '"':
            self.error('Expected JSON double-quoted string.')
        try:
            result, end = self.decoder.raw_decode(self.text, self.i)
        except (json.JSONDecodeError, ValueError) as e:
            self.error("Invalid JSON string literal.", start=start)
        if not isinstance(result, str):
            self.error("Expected JSON string.", start=start)
        if _has_surrogate(result):
            self.error("Unpaired JSON UTF-16 surrogate escape is forbidden.", start=start, end=end)
        self.i = end
        return result

    def scalar(self) -> str | bool | None | Decimal:
        self.skip_ws()
        if self.i >= len(self.text):
            self.error("Expected JSON scalar value.")
        if self.text[self.i] == '"':
            return self.string()
        for token, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(token, self.i):
                self.i += len(token)
                return value
        m = NUMBER.match(self.text, self.i)
        if m:
            self.i = m.end()
            return Decimal(m.group())
        self.error("Expected JSON scalar value.")

    def params(self) -> dict[str, Any]:
        self.skip_ws()
        params: dict[str, Any] = {}
        while True:
            self.skip_ws()
            match = PARAM.match(self.text, self.i)
            if not match:
                self.error("Expected ASCII parameter name.")
            name = match.group()
            if name in params:
                self.error("Duplicate parameter name.", code="P1_DUPLICATE_PARAMETER", start=self.i, end=match.end())
            self.i = match.end()
            self.expect("=")
            value = self.scalar()
            params[name] = value
            if len(params) > MAX_PARAMS:
                self.error("More than 64 parameters in one parameter list.", code="P1_INPUT_LIMIT")
            if not self.consume(","):
                return params

    def reference(self) -> dict:
        self.skip_ws()
        pos = self.i
        if self.i >= len(self.text) or self.text[self.i] not in HOME:
            self.error("Expected home X, Y, or Z.")
        home = self.text[self.i]
        self.i += 1
        self.expect(":")
        self.skip_ws()
        if self.i >= len(self.text) or self.text[self.i] not in LAYER:
            self.error("Expected layer α, β, or ζ.")
        layer = self.text[self.i]
        self.i += 1
        self.expect(":")
        self.skip_ws()
        start = self.i
        while self.i < len(self.text):
            c = self.text[self.i]
            if c in WS or c == "[":
                break
            if c in KEY_FORBIDDEN or ord(c) < 0x20 or c.isspace():
                self.error("Invalid concept key token.")
            self.i += 1
        key = self.text[start:self.i]
        if not _valid_concept_key(key):
            self.error("Expected nonempty concept key token.", start=start)
        self.expect("[")
        referent = self.string()
        self.expect("]")
        self.budget.add(pos)
        return {"kind": "reference", "address": {"home": home, "layer": layer, "concept_key": key}, "referent_ref": referent}

    def relation(self, depth: int) -> dict:
        pos = self.i
        self.i += 3
        self.expect("(")
        predicate = self.string()
        if not predicate:
            self.error("Predicate must be a nonempty string.", start=pos)
        self.expect(",")
        subject = self.expression(depth + 1)
        self.expect(",")
        obj = self.expression(depth + 1)
        params = self.params() if self.consume(";") else {}
        self.expect(")")
        self.budget.add(pos)
        return {"kind": "relation", "predicate_id": predicate, "subject": subject, "object": obj, "parameters": params}

    def application(self, depth: int) -> dict:
        self.skip_ws()
        pos = self.i
        m = METHOD.match(self.text, self.i)
        if not m:
            self.error("Expected versioned MethodID (namespace/vN).")
        name = m.group()
        self.i = m.end()
        self.expect("(")
        args: list[dict] = []
        params: dict[str, Any] = {}
        self.skip_ws()
        if self.i < len(self.text) and self.text[self.i] not in ");":
            args.append(self.expression(depth + 1))
            while self.consume(","):
                args.append(self.expression(depth + 1))
        if self.consume(";"):
            params = self.params()
        self.expect(")")
        self.budget.add(pos)
        return {"kind": "application", "method_id": name, "arguments": args, "parameters": params}

    def expression(self, depth: int = 1) -> dict:
        if depth > MAX_DEPTH:
            self.error("Maximum AST expression depth exceeded (64).", code="P1_INPUT_LIMIT")
        self.skip_ws()
        pos = self.i
        if self.consume("("):
            primary = self.expression(depth + 1)
            self.expect(")")
        elif self.i < len(self.text) and self.text[self.i] in HOME:
            primary = self.reference()
        elif self.text.startswith("rel", self.i) and (
            self.i + 3 == len(self.text) or self.text[self.i + 3] in WS + "("
        ):
            primary = self.relation(depth)
        else:
            primary = self.application(depth)
        qualifiers: list[dict] = []
        while self.consume("@"):
            if len(qualifiers) >= MAX_QUALIFIERS:
                self.error("More than 64 qualifiers on one expression.", code="P1_INPUT_LIMIT")
            self.skip_ws()
            if self.i >= len(self.text) or self.text[self.i] not in QUALIFIER:
                self.error("Expected qualifier T, F, M, or O.")
            coordinate = self.text[self.i]
            self.i += 1
            self.expect("(")
            params = {} if self.consume(")") else self.params()
            if params:
                self.expect(")")
            qualifiers.append({"coordinate": coordinate, "parameters": params})
            self.budget.add(pos)
        if qualifiers:
            self.budget.add(pos)
            return {"kind": "qualified", "expression": primary, "qualifiers": qualifiers}
        return primary

    def parse(self) -> dict:
        self.skip_ws()
        if self.i == len(self.text):
            self.error("Empty input; exactly one expression is required.")
        ast = self.expression()
        self.skip_ws()
        if self.i != len(self.text):
            self.error("Unexpected trailing content; expected EOF.")
        return ast


def parse_acg_bytes(source: bytes) -> dict:
    text = _decode_source(source)
    return Parser(text).parse()


def _is_json_scalar(value: Any) -> bool:
    return (value is None or isinstance(value, (bool, str, Decimal)) or
            (isinstance(value, int) and not isinstance(value, bool)) or
            (isinstance(value,float) and math.isfinite(value)))


def _validate_ast_node(node: Any, budget: ResourceBudget, depth: int = 1) -> None:
    if depth > MAX_DEPTH:
        raise ParseError("P1_INPUT_LIMIT", "Maximum AST expression depth exceeded (64).", stage="structure")
    budget.add()
    if not isinstance(node, dict):
        raise ParseError("P1_STRUCTURAL_AST", "AST expression must be an object.", stage="structure")
    kind = node.get("kind")
    if kind not in KINDS:
        raise ParseError("P1_STRUCTURAL_AST", "AST kind must be reference/qualified/relation/application.", stage="structure")

    def shape(required: set[str], optional: set[str] = frozenset()) -> None:
        if not required <= node.keys() or node.keys() - required - optional:
            raise ParseError("P1_STRUCTURAL_AST", f"Incorrect fields for AST kind {kind}.", stage="structure")

    def params(p: Any) -> None:
        if not isinstance(p, dict):
            raise ParseError("P1_STRUCTURAL_AST", "Parameters must be an object.", stage="structure")
        if len(p) > MAX_PARAMS:
            raise ParseError("P1_INPUT_LIMIT", "More than 64 parameters.", stage="structure")
        for key, value in p.items():
            if not isinstance(key, str) or PARAM.fullmatch(key) is None or not _is_json_scalar(value):
                raise ParseError("P1_STRUCTURAL_AST", "Invalid parameter name or scalar value.", stage="structure")
            if isinstance(value, str) and _has_surrogate(value):
                raise ParseError("P1_STRUCTURAL_AST", "Unpaired Unicode surrogate in string.", stage="structure")

    if kind == "reference":
        shape({"kind", "address", "referent_ref"})
        addr = node["address"]
        if not isinstance(addr, dict) or not {"home", "layer", "concept_key"} <= addr.keys() or addr.keys() - {"home", "layer", "concept_key", "concept_id"}:
            raise ParseError("P1_STRUCTURAL_AST", "Invalid reference address shape.", stage="structure")
        if addr["home"] not in HOME or addr["layer"] not in LAYER or not isinstance(addr["concept_key"], str) or not _valid_concept_key(addr["concept_key"]):
            raise ParseError("P1_STRUCTURAL_AST", "Invalid reference address token.", stage="structure")
        if "concept_id" in addr and (not isinstance(addr["concept_id"], str) or not addr["concept_id"]):
            raise ParseError("P1_STRUCTURAL_AST", "Invalid concept_id.", stage="structure")
        if not isinstance(node["referent_ref"], str) or not node["referent_ref"] or _has_surrogate(node["referent_ref"]):
            raise ParseError("P1_STRUCTURAL_AST", "Missing or invalid referent_ref.", stage="structure")
    elif kind == "qualified":
        shape({"kind", "expression", "qualifiers"})
        q = node["qualifiers"]
        if not isinstance(q, list) or not q:
            raise ParseError("P1_STRUCTURAL_AST", "Qualified requires at least one qualifier.", stage="structure")
        if len(q) > MAX_QUALIFIERS:
            raise ParseError("P1_INPUT_LIMIT", "More than 64 qualifiers.", stage="structure")
        for item in q:
            budget.add()
            if not isinstance(item, dict) or not {"coordinate", "parameters"} <= item.keys() or item.keys() - {"coordinate", "parameters", "profile_ref"} or item["coordinate"] not in QUALIFIER:
                raise ParseError("P1_STRUCTURAL_AST", "Invalid qualifier shape.", stage="structure")
            if "profile_ref" in item and (not isinstance(item["profile_ref"], str) or not item["profile_ref"]):
                raise ParseError("P1_STRUCTURAL_AST", "Invalid qualifier profile_ref.", stage="structure")
            params(item["parameters"])
        _validate_ast_node(node["expression"], budget, depth + 1)
    elif kind == "relation":
        shape({"kind", "predicate_id", "subject", "object", "parameters"})
        if not isinstance(node["predicate_id"], str) or not node["predicate_id"] or _has_surrogate(node["predicate_id"]):
            raise ParseError("P1_STRUCTURAL_AST", "Invalid predicate_id.", stage="structure")
        params(node["parameters"])
        _validate_ast_node(node["subject"], budget, depth + 1)
        _validate_ast_node(node["object"], budget, depth + 1)
    else:
        shape({"kind", "method_id", "arguments", "parameters"})
        if not isinstance(node["method_id"], str) or METHOD.fullmatch(node["method_id"]) is None:
            raise ParseError("P1_STRUCTURAL_AST", "Invalid versioned method_id.", stage="structure")
        params(node["parameters"])
        if not isinstance(node["arguments"], list):
            raise ParseError("P1_STRUCTURAL_AST", "Arguments must be an array.", stage="structure")
        for arg in node["arguments"]:
            _validate_ast_node(arg, budget, depth + 1)


def validate_ast(ast: Any) -> None:
    _validate_ast_node(ast, ResourceBudget())


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    obj: dict = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"Duplicate JSON object key: {key!r}")
        obj[key] = value
    return obj


def load_ast_bytes(source: bytes) -> dict:
    text = _decode_source(source)
    try:
        obj = json.loads(text, parse_int=Decimal, parse_float=Decimal,
                         parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Non-JSON numeric constant: {x}")),
                         object_pairs_hook=_no_duplicate_keys)
    except (ValueError, json.JSONDecodeError, RecursionError) as e:
        raise ParseError("P1_STRUCTURAL_AST", "Invalid JSON AST document: " + str(e)[:160], stage="structure") from e
    # JSON decoding accepts escaped unpaired surrogates on some Python versions:
    # reject them in ALL string keys/values, not just referents or parameters.
    def reject_surrogates(v, depth=0):
        if depth > MAX_DEPTH * 3:
            raise ParseError("P1_INPUT_LIMIT", "JSON nesting limit exceeded.", stage="structure")
        if isinstance(v, str) and _has_surrogate(v):
            raise ParseError("P1_STRUCTURAL_AST", "Unpaired Unicode surrogate escape in JSON AST.", stage="structure")
        if isinstance(v, dict):
            for k,x in v.items():
                reject_surrogates(k,depth+1)
                reject_surrogates(x,depth+1)
        if isinstance(v, list):
            for x in v:
                reject_surrogates(x,depth+1)
    reject_surrogates(obj)
    validate_ast(obj)
    return obj


def _canonical_decimal(value: Decimal) -> str:
    if not value.is_finite():
        raise ValueError("Non-finite decimal numbers are not JSON values.")
    sign, digits, exponent = value.as_tuple()
    coefficient = ''.join(str(d) for d in digits)
    if not any(digits):
        return '0'
    trim = len(coefficient) - len(coefficient.rstrip('0'))
    coefficient = coefficient[:len(coefficient)-trim] if trim else coefficient
    exponent += trim
    return ('-' if sign else '') + coefficient + (('e'+str(exponent)) if exponent else '')


def json_dump(value: Any, *, indent: int | None = 2) -> str:
    """JSON with exact Decimals and stable field ordering, no float conversion."""
    # We don't build an enormous intermediate string for individual numbers.
    def dump(v: Any, depth: int) -> str:
        if isinstance(v, Decimal):
            return _canonical_decimal(v)
        if v is None:
            return 'null'
        if v is True:
            return 'true'
        if v is False:
            return 'false'
        if isinstance(v, str):
            return json.dumps(v, ensure_ascii=False)
        if isinstance(v, int):
            return str(v)
        if isinstance(v, float) and math.isfinite(v):
            return _canonical_decimal(Decimal(str(v)))
        if isinstance(v, list):
            if not v: return '[]'
            if indent is None: return '['+','.join(dump(x, depth+1) for x in v)+']'
            p=' '*(indent*(depth+1)); q=' '*(indent*depth)
            return '[\n'+',\n'.join(p+dump(x, depth+1) for x in v)+'\n'+q+']'
        if isinstance(v, dict):
            if not v: return '{}'
            if indent is None: return '{'+','.join(dump(k,depth+1)+':'+dump(x,depth+1) for k,x in v.items())+'}'
            p=' '*(indent*(depth+1)); q=' '*(indent*depth)
            return '{\n'+',\n'.join(p+dump(k,depth+1)+': '+dump(x,depth+1) for k,x in v.items())+'\n'+q+'}'
        raise TypeError(f"Unsupported JSON value: {type(v).__name__}")
    return dump(value, 0)


def canonical_acg(ast: dict) -> str:
    """Canonical single-line ACG; equality guaranteed at AST *values* not bytes.

    Note P0 AST's optional concept_id/profile_ref have no ACG text encoding.
    Reject rather than silently discard such annotations.
    """
    validate_ast(ast)
    def quoted(s: str) -> str:
        return json.dumps(s, ensure_ascii=False, separators=(',', ':'))
    def plist(p: dict) -> str:
        return ','.join(k+'='+(_canonical_decimal(v) if isinstance(v, Decimal) else json_dump(v, indent=None)) for k,v in sorted(p.items()))
    def render(node: dict) -> str:
        kind = node['kind']
        if kind == 'reference':
            a=node['address']
            if 'concept_id' in a:
                raise ValueError('Cannot print concept_id annotation as ACG without information loss.')
            return a['home']+':'+a['layer']+':'+a['concept_key']+'['+quoted(node['referent_ref'])+']'
        if kind == 'relation':
            return ('rel('+quoted(node['predicate_id'])+','+render(node['subject'])+','+render(node['object'])+
                    (';'+plist(node['parameters']) if node['parameters'] else '')+')')
        if kind == 'application':
            return (node['method_id']+'('+','.join(render(a) for a in node['arguments'])+
                    (';'+plist(node['parameters']) if node['parameters'] else '')+')')
        if kind == 'qualified':
            base = render(node['expression'])
            if node['expression']['kind']=='qualified':
                base='('+base+')'
            for q in node['qualifiers']:
                if 'profile_ref' in q:
                    raise ValueError('Cannot print qualifier profile_ref without information loss.')
                base+='@'+q['coordinate']+'('+plist(q['parameters'])+')'
            return base
        raise AssertionError('validated AST kind')
    return render(ast)


def error_diagnostic(err: ParseError, raw: bytes) -> dict:
    if err.code == 'P1_INVALID_UTF8' and raw:
        byte_start = min(err.index, len(raw))
        byte_end = min(err.end if err.end is not None else err.index+1, len(raw))
        # Column cannot be established across invalid UTF-8 boundaries.
        line = column = None
    else:
        text = raw.decode('utf-8', errors='replace')
        idx = min(max(0,err.index), len(text))
        prefix = text[:idx]
        byte_start = len(prefix.encode('utf-8'))
        end_index = min(len(text), err.end if err.end is not None else err.index+1)
        byte_end = len(text[:max(idx,end_index)].encode('utf-8'))
        line = prefix.count('\n') + 1
        column = len(prefix.rsplit('\n',1)[-1]) + 1
    diagnostic = {
        'code':err.code, 'stage':err.stage,
        'severity':'error', 'message':err.message,
        'reference_rule': ('P0 notation/ast.schema.json' if err.stage=='structure' else 'P1.1 notation_p1.ebnf / validation_profile.json'),
        'byte_start':byte_start, 'byte_end':max(byte_start,byte_end)
    }
    if line is not None:
        diagnostic['line']=line
        diagnostic['column']=column
    return diagnostic


def parse_result(raw: bytes, *, input_format: str='acg_text') -> dict:
    """P1.2-only result; deliberately NOT a full P1 validation report."""
    outcome: dict = {
        'format': 'aiaeao.cube.parser-result/1', 'profile': 'P1-VC/1.0.0',
        'reference_version': 'v9.4', 'input_format': input_format,
        'input_sha256': hashlib.sha256(raw).hexdigest(),
        'syntax_status': 'NOT_EVALUATED' if input_format=='json_ast' else 'PASS',
        'structure_status': 'NOT_EVALUATED',
        'semantic_validation': 'NOT_EVALUATED',
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
        'diagnostics': [],
    }
    try:
        if input_format == 'acg_text':
            ast = parse_acg_bytes(raw)
            outcome['syntax_status'] = 'PASS'
            validate_ast(ast)
        elif input_format == 'json_ast':
            # JSON shape check: a preexisting AST cannot prove provenance from source grammar.
            ast = load_ast_bytes(raw)
        else:
            raise ValueError('input_format must be acg_text or json_ast')
        outcome['structure_status'] = 'PASS'
        outcome['ast'] = ast
    except ParseError as e:
        outcome['diagnostics'] = [error_diagnostic(e, raw)]
        outcome[e.stage+'_status'] = 'FAIL'
    return outcome
