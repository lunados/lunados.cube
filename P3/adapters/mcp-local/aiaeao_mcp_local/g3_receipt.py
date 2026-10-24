"""G3-only independent evidence assembler; NOT a new MCP tool or ACG->SVG converter.

Accepts independently observed P0, P1 and P2 tool results. A successful
G3 trace never implies the P1 expression is the source of the P2 picture.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any

FORMAT = 'aiaeao.cube.g3-cross-domain-evidence/1'
CHECKS = ('syntax','structure','concept_resolution','referent_binding',
          'predicate_typing','method_typing','qualifier_typing','scope_consistency')
NOT_EVALUATED_FIELDS = ('epistemic_warrant','current_authority','canonical_admission')


class G3ProofError(ValueError):
    """A mismatch between independent observations; safe fixed diagnostic code."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def require(ok: bool, code: str) -> None:
    if not ok:
        raise G3ProofError(code)


def _utf8(content: str) -> bytes:
    require(type(content) is str, 'G3_CONTENT_NOT_TEXT')
    try:
        return content.encode('utf-8', 'strict')
    except UnicodeError:
        raise G3ProofError('G3_CONTENT_NOT_UTF8') from None


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_p0(index_page: dict, reference_uri: str, pages: list[dict]) -> dict:
    """Prove transmission-byte fidelity against a *declared* P0 digest.

    Does not claim that the content is empirically true or that the registry
    publisher is authenticated by the hash alone.
    """
    require(type(index_page) is dict and index_page.get('complete') is True, 'G3_INDEX_INCOMPLETE')
    require(index_page.get('uri') == 'aiaeao://p0/resources/v1', 'G3_INDEX_URI_INVALID')
    idx_bytes = _utf8(index_page.get('content'))
    require(index_page.get('sha256') == _sha(idx_bytes), 'G3_INDEX_DIGEST_MISMATCH')
    try:
        catalog = json.loads(idx_bytes)
    except (ValueError, UnicodeError):
        raise G3ProofError('G3_INDEX_JSON_INVALID') from None
    require(catalog.get('reference_version') == 'v9.4', 'G3_REFERENCE_VERSION_MISMATCH')
    require(catalog.get('source_warrant') == 'canonical_documentary_reference_only', 'G3_SOURCE_WARRANT_INVALID')
    targets = [e for e in catalog.get('resources', []) if e.get('uri') == reference_uri]
    require(len(targets) == 1, 'G3_REFERENCE_NOT_PINNED')
    expected = targets[0]
    require(type(pages) is list and len(pages) > 0, 'G3_REFERENCE_NOT_READ')
    offset = 0
    fragments = []
    for i, page in enumerate(pages):
        require(type(page) is dict and page.get('uri') == reference_uri, 'G3_REFERENCE_URI_MISMATCH')
        require(page.get('integrity_verified') is True, 'G3_REFERENCE_NOT_VERIFIED')
        require(page.get('offset') == offset, 'G3_PAGE_OFFSET_MISMATCH')
        raw = _utf8(page.get('content'))
        require(page.get('page_bytes') == len(raw), 'G3_PAGE_SIZE_MISMATCH')
        require(page.get('sha256') == expected['sha256'], 'G3_REFERENCE_DECLARATION_MISMATCH')
        offset += len(raw)
        if i < len(pages)-1:
            require(page.get('complete') is False and page.get('next_offset') == offset,
                    'G3_PAGE_CHAIN_BROKEN')
        else:
            require(page.get('complete') is True and page.get('next_offset') is None,
                    'G3_REFERENCE_INCOMPLETE')
        fragments.append(raw)
    content = b''.join(fragments)
    require(len(content) == expected['bytes'] == pages[-1].get('total_bytes'), 'G3_REFERENCE_SIZE_MISMATCH')
    require(_sha(content) == expected['sha256'], 'G3_REFERENCE_DIGEST_MISMATCH')
    return {
        'domain': 'P0', 'status': 'INTEGRITY_CHECKED',
        'uri': reference_uri, 'reference_version': 'v9.4',
        'index_sha256': _sha(idx_bytes), 'snapshot_lock_sha256': catalog['snapshot_lock_sha256'],
        'bytes_read': len(content), 'pages_read': len(pages),
        'content_sha256': _sha(content), 'source_warrant': 'canonical_documentary_reference_only',
        'content_truth': 'NOT_EVALUATED', 'integrity_basis': 'independently_hashed_mcp_transferred_utf8_bytes',
    }


def verify_p1(response: dict, original_acg_text: str) -> dict:
    require(type(response) is dict and type(response.get('report')) is dict, 'G3_P1_RESULT_INVALID')
    report = response['report']
    require(response.get('p1_validation_performed') is True and
            response.get('p2_printing_performed') is False, 'G3_P1_SCOPE_MISMATCH')
    require(response.get('core_profile') == 'P1-VC/1.0.0', 'G3_P1_PROFILE_MISMATCH')
    require(response.get('source_warrant') == 'declared_unverified', 'G3_P1_WARRANT_ESCALATED')
    require(report.get('overall_status') in ('PASS','FAIL','UNRESOLVED'), 'G3_P1_STATUS_INVALID')
    require(tuple(report.get('checks',{})) == CHECKS, 'G3_P1_CHECKS_INVALID')
    require(report.get('input_sha256') == _sha(_utf8(original_acg_text)), 'G3_P1_INPUT_DIGEST_MISMATCH')
    require(all(report.get(k) == 'NOT_EVALUATED' for k in NOT_EVALUATED_FIELDS), 'G3_P1_AUTHORITY_CLAIM')
    return {
        'domain':'P1', 'status':report['overall_status'], 'profile':'P1-VC/1.0.0',
        'input_sha256':report['input_sha256'], 'checks':list(CHECKS),
        'source_warrant':'declared_unverified',
        'epistemic_warrant':'NOT_EVALUATED','current_authority':'NOT_EVALUATED',
        'canonical_admission':'NOT_EVALUATED',
    }


def verify_p2(job: dict, check_result: dict, render_result: dict,
              original_bundle: dict, expected_svg_sha256: str | None = None) -> dict:
    require(type(job) is dict and type(check_result) is dict and type(render_result) is dict,
            'G3_P2_RESPONSE_INVALID')
    require(job.get('source_bundle') == original_bundle, 'G3_P2_BUNDLE_CHANGED')
    require(job.get('reference_version') == 'v9.4', 'G3_P2_REFERENCE_VERSION_MISMATCH')
    require(render_result.get('report') == check_result, 'G3_P2_CHECK_RENDER_DISAGREE')
    require(check_result.get('status') == 'PASS', 'G3_P2_CHECK_NOT_PASS')
    require(render_result.get('source_status') == 'declared_unverified', 'G3_P2_WARRANT_ESCALATED')
    require(all(check_result.get(k) == 'NOT_EVALUATED' for k in NOT_EVALUATED_FIELDS),
            'G3_P2_AUTHORITY_CLAIM')
    artifact = render_result.get('artifact')
    require(type(artifact) is dict and artifact.get('media_type') == 'image/svg+xml',
            'G3_P2_ARTIFACT_INVALID')
    svg_bytes = _utf8(artifact.get('svg_text'))
    svg_digest = _sha(svg_bytes)
    require(len(svg_bytes) == artifact.get('byte_length'), 'G3_P2_SVG_SIZE_MISMATCH')
    require(svg_digest == artifact.get('sha256') == check_result.get('svg_sha256'),
            'G3_P2_SVG_DIGEST_MISMATCH')
    if expected_svg_sha256 is not None:
        require(svg_digest == expected_svg_sha256, 'G3_P2_GOLDEN_MISMATCH')
    require(check_result.get('source_bundle_sha256') == job.get('source_bundle_sha256'),
            'G3_P2_SOURCE_LOCK_MISMATCH')
    dims = check_result['dimensions']
    require(dims['view'] in ('cube.flow','cube.diagramm','cube.tree'), 'G3_P2_VIEW_INVALID')
    return {
        'domain':'P2', 'status':check_result['status'], 'profile':'P2-VP/1.0.0-rc1',
        'view':dims['view'],'lens':dims['lens'],'granularity':dims['granularity'],
        'svg_sha256':svg_digest,'svg_bytes':len(svg_bytes),
        'source_bundle_sha256':job['source_bundle_sha256'],
        'source_status':'declared_unverified',
        'decision':check_result['decision']['action'],
        'omitted_item_ids':check_result['loss_ledger']['omitted_item_ids'],
        'omitted_source_edge_ids':check_result['loss_ledger']['omitted_source_edge_ids'],
        'epistemic_warrant':'NOT_EVALUATED','current_authority':'NOT_EVALUATED',
        'canonical_admission':'NOT_EVALUATED',
    }


def assemble(p0_evidence: dict, p1_evidence: dict, p2_evidence: dict, *, scenario: str) -> dict:
    require(type(scenario) is str and scenario in
            ('declared_fixture','p1_fail_p2_valid','p1_unresolved_p2_valid'), 'G3_SCENARIO_INVALID')
    require(p0_evidence.get('domain') == 'P0' and p1_evidence.get('domain') == 'P1' and
            p2_evidence.get('domain') == 'P2', 'G3_DOMAIN_CONFUSION')
    if scenario == 'p1_fail_p2_valid':
        require(p1_evidence['status'] == 'FAIL', 'G3_CONTRADICTION_NOT_TESTED')
    if scenario == 'p1_unresolved_p2_valid':
        require(p1_evidence['status'] == 'UNRESOLVED', 'G3_UNRESOLVED_NOT_TESTED')
    require(p2_evidence['source_status'] == 'declared_unverified', 'G3_SOURCE_WARRANT_ESCALATED')
    # Deliberately no derived cross-domain mapping or composite PASS/FAIL.
    return {
        'format':FORMAT,'scenario':scenario,'trace_status':'COMPLETE',
        'p0':p0_evidence,'p1':p1_evidence,'p2':p2_evidence,
        'cross_domain_link':'NOT_ESTABLISHED',
        'acg_to_vp03_mapping':'NOT_PERFORMED',
        'p2_bundle_provision':'separately_supplied_explicit_vp03_declaration',
        'source_truth':'NOT_EVALUATED', 'authority':'NOT_EVALUATED',
        'admission':'NOT_EVALUATED',
        'note':'Trace COMPLETE is not overall semantic PASS; domains remain independent.',
    }
