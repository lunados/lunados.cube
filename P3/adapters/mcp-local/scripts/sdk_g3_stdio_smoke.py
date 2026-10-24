"""G3 genuine MCP-SDK-v2 stdio cross-domain test, run in the target Mac .venv.

The six unchanged MCP tools are invoked against a separate real server process.
No ACG->VP03 mapping; a frozen VP-03 fixture is supplied independently.
Requires: mcp==2.0.0. Does not write files unless --evidence is specified.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE))
from aiaeao_mcp_local import g3_receipt as proof, p0_resources

P0_INDEX = 'aiaeao://p0/resources/v1'
P0_CONCEPTS = 'https://cube.lunados.net/v9.4/grammar/concepts.json'
TOOL_NAMES = ['cube_get_capabilities','cube_prepare_print','cube_check_print',
              'cube_render_svg','cube_read_reference','cube_validate','cube_discover_surface']


async def run() -> dict:
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as error:
        raise RuntimeError('MCP_SDK_NOT_INSTALLED: install mcp==2.0.0') from error
    examples = ROOT/'P2/visual-printer-release-v1/examples'
    p1_fixtures = ROOT/'P1/semantic-validator-v1/fixtures'
    acg = (p1_fixtures/'migration.acg').read_text(encoding='utf-8')
    ctx = json.loads((p1_fixtures/'migration.binding-context.json').read_text(encoding='utf-8'))
    bundle = json.loads((examples/'flow_provenance_standard.vp03.bundle.json').read_text(encoding='utf-8'))
    golden = (examples/'flow_provenance_standard.svg').read_bytes()
    golden_report = json.loads((examples/'flow_provenance_standard.report.json').read_text(encoding='utf-8'))
    golden_job = json.loads((examples/'flow_provenance_standard.job.json').read_text(encoding='utf-8'))
    server_params = StdioServerParameters(command=sys.executable, args=['-u',str(BASE/'run_server.py')])
    async with Client(stdio_client(server_params), mode='2026-07-28') as client:
        names = [t.name for t in (await client.list_tools()).tools]
        assert names == TOOL_NAMES, (names, TOOL_NAMES)

        async def call(name, kwargs):
            r = await client.call_tool(name, kwargs)
            assert not r.is_error, (name, r.content)
            assert type(r.structured_content) is dict, (name, 'no structured content')
            return r.structured_content

        # P0: exact allowlisted reference bytes reassembled from MCP tool pages.
        index_page = await call('cube_read_reference',{'uri':P0_INDEX})
        offset = 0
        pages = []
        while True:
            page = await call('cube_read_reference',
                              {'uri':P0_CONCEPTS,'offset':offset,'max_bytes':32768})
            pages.append(page)
            if page['complete']:
                break
            offset=page['next_offset']
            assert len(pages) <= 100
        p0_info = proof.verify_p0(index_page,P0_CONCEPTS,pages)
        assert b''.join(page['content'].encode('utf-8') for page in pages) == p0_resources.read_bytes(P0_CONCEPTS)
        assert p0_info['content_sha256'] == hashlib.sha256(p0_resources.read_bytes(P0_CONCEPTS)).hexdigest()

        # P1: independent submitted ACG and declared context; never linked to P2.
        p1_ok = await call('cube_validate',{'input_text':acg,'context':ctx})
        p1_pass = proof.verify_p1(p1_ok,acg)
        assert p1_pass['status'] == 'PASS'
        p1_bad_text = 'this is not valid ACG'
        p1_bad = await call('cube_validate',{'input_text':p1_bad_text})
        p1_fail = proof.verify_p1(p1_bad,p1_bad_text)
        assert p1_fail['status'] == 'FAIL'
        p1_unresolved = await call('cube_validate',{'input_text':acg})
        p1_unknown = proof.verify_p1(p1_unresolved,acg)
        assert p1_unknown['status'] == 'UNRESOLVED'

        # P2: a separately provided, explicit and unchanged VP-03 declaration.
        prepared = await call('cube_prepare_print',
                              {'bundle':bundle,'lens':'cube.lens.provenance','granularity':'standard'})
        assert prepared == golden_job
        checked = await call('cube_check_print',{'job':prepared})
        assert checked == golden_report
        rendered = await call('cube_render_svg',{'job':prepared})
        assert rendered['artifact']['svg_text'].encode('utf-8') == golden
        p2_info = proof.verify_p2(prepared,checked,rendered,bundle,hashlib.sha256(golden).hexdigest())
        for _ in range(2):
            again = await call('cube_render_svg',{'job':prepared})
            assert again == rendered

        good = proof.assemble(p0_info,p1_pass,p2_info,scenario='declared_fixture')
        contradiction = proof.assemble(p0_info,p1_fail,p2_info,scenario='p1_fail_p2_valid')
        unknown = proof.assemble(p0_info,p1_unknown,p2_info,scenario='p1_unresolved_p2_valid')
        assert good['p1']['status'] == 'PASS' and good['p2']['status'] == 'PASS'
        assert contradiction['p1']['status'] == 'FAIL' and contradiction['p2']['status'] == 'PASS'
        assert unknown['p1']['status'] == 'UNRESOLVED' and unknown['p2']['status'] == 'PASS'
        # No input->view provenance assertion even in the PASS scenario.
        assert all(x['cross_domain_link']=='NOT_ESTABLISHED' and
                   x['acg_to_vp03_mapping']=='NOT_PERFORMED' for x in (good,contradiction,unknown))
        return {'format':'aiaeao.cube.g3-mcp-sdk-smoke/1',
                'transport':'official_MCP_SDK_v2_stdio_child_process',
                'tool_names':names,'host':'local_python_SDK_client_not_Claude',
                'scenarios':[good,contradiction,unknown],
                'report_parity':'exact_frozen_VP06_fixture',
                'host_acceptance':'PENDING'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,default=None,help='Optional JSON evidence output outside source tree')
    args=parser.parse_args()
    receipt = asyncio.run(run())
    if args.evidence:
        if args.evidence.exists():
            raise SystemExit('EVIDENCE_TARGET_EXISTS: refusing to overwrite')
        args.evidence.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('PASS G3 official MCP SDK v2 stdio: P0 pinned reference, P1 PASS/FAIL/UNRESOLVED, '
          'P2 golden SVG/report parity x3; independent domain outcomes; no auto-mapping')
    return 0

if __name__=='__main__':raise SystemExit(main())
