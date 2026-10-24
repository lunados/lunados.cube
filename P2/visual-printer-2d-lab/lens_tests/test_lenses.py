"""VP-03 black-box-level and component negative tests with independent invariants."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from vplenses import LensPrinter, LensError, PROFILES, PROFILE
from vplenses.printer import source_digest, NS

ROOT=Path(__file__).resolve().parents[1]
BUNDLES={p.stem:json.loads(p.read_text('utf8')) for p in (ROOT/'lens_bundles').glob('*.json')}
P=LensPrinter()

class LensContract(unittest.TestCase):
    def pick(self,b='flow_migration'):
        return copy.deepcopy(BUNDLES[b])

    def test_five_exact_lenses(self):
        self.assertEqual(PROFILES,tuple('cube.lens.'+name for name in ('semantics','provenance','execution','governance','epistemology')))
        for x in ('flow','chart','tree','planner.flow','cube.flow','neutral','cube.lens.other','governance'):
            with self.subTest(x=x),self.assertRaises(LensError):P.validate(self.pick(),x)

    def test_three_bundles_each_five_lenses(self):
        self.assertEqual(set(BUNDLES),{'flow_migration','chart_inventory','tree_modules'})
        for k,b in BUNDLES.items():
            with self.subTest(bundle=k):
                self.assertEqual({x['lens'] for x in b['facet_bindings']},set(PROFILES))
                for x in PROFILES:self.assertGreater(len(P.validate(b,x)['selected']),0)

    def test_color_tokens_are_p1_baseline(self):
        for lens in PROFILES:
            token='domain.'+lens.rsplit('.',1)[-1]
            self.assertEqual(P.accents[lens],P.base.base.colors[token])

    def test_each_lens_different_svg_no_plan_change(self):
        for name,b in BUNDLES.items():
            before=source_digest(b['view_plan'])
            rendered=[P.render(b,l) for l in PROFILES]
            self.assertEqual(len(set(rendered)),5,name)
            self.assertEqual(source_digest(b['view_plan']),before)
            self.assertTrue(all(x.startswith(b'<?xml ') for x in rendered))

    def test_identical_input_identical_bytes(self):
        for b in BUNDLES.values():
            for l in PROFILES:
                with self.subTest(view=b['view_plan']['view'],lens=l):
                    self.assertEqual(P.render(b,l),P.render(b,l))

    def test_all_original_node_edge_sample_identity_preserved(self):
        for b in BUNDLES.values():
            v=b['view_plan'];base=P.base.report(v,P.base.render(v))
            for l in PROFILES:
                svg=P.render(b,l);root=ET.fromstring(svg)
                rpt=P.report(b,l,svg)
                self.assertEqual(rpt['original_vp02_report'],base)
                self.assertEqual(rpt['base_view_svg_sha256'],hashlib.sha256(P.base.render(v)).hexdigest())
                if v['view']=='cube.diagramm':
                    self.assertEqual(base['sample_ids'],[x['id'] for x in v['samples']])
                    self.assertEqual(rpt['original_vp02_report']['unit'],v['metric']['unit'])
                    # Chart quantities must be present exactly as in the VP-02 original.
                    base_text=[x.text for x in ET.fromstring(P.base.render(v)).iter(f'{{{NS}}}text')]
                    projected_text=[x.text for x in root.iter(f'{{{NS}}}text')]
                    self.assertEqual(projected_text[:len(base_text)],base_text)
                else:
                    ids={g.get('data-item-id') for g in root.iter(f'{{{NS}}}g') if g.get('data-item-id')}
                    self.assertEqual(ids,{n['id'] for n in v['nodes']})
                    edges={g.get('data-edge-id') for g in root.iter(f'{{{NS}}}g') if g.get('data-edge-id')}
                    self.assertEqual(edges,{f'e{i+1}' for i in range(len(v['edges']))})
                    for e in v['edges']:
                        self.assertTrue(any(g.get('data-declaration-ref')==e['declaration_ref'] for g in root.iter(f'{{{NS}}}g')))

    def test_svg_focus_matches_explicit_bindings(self):
        for b in BUNDLES.values():
            for lens in PROFILES:
                root=ET.fromstring(P.render(b,lens))
                targets=P.validate(b,lens)['selected']
                for entry in targets:
                    k,t=entry['target_kind'],entry['target_id']
                    attr={'node':'data-item-id','edge':'data-edge-id','sample':'data-sample-id','metric':'data-metric-id'}[k]
                    matching=[g for g in root.iter(f'{{{NS}}}g') if g.get(attr)==t]
                    self.assertEqual(len(matching),1,(lens,k,t))
                    self.assertEqual(matching[0].get('data-vp03-lens-focus'),'declared')
                all_focus=[g for g in root.iter(f'{{{NS}}}g') if g.get('data-vp03-lens-focus')=='declared']
                self.assertEqual(len(all_focus),len(targets))
                self.assertEqual(root.get('data-vp03-lens'),lens)
                metadata=root.find(f'{{{NS}}}metadata')
                self.assertEqual(json.loads(metadata.text)['bindings'],targets)

    def test_report_truth_authority_never_promoted(self):
        for b in BUNDLES.values():
            for l in PROFILES:
                result=P.report(b,l,P.render(b,l))
                for field in ('semantic_conformance','epistemic_warrant','current_authority','canonical_admission'):
                    self.assertEqual(result[field],'NOT_EVALUATED')
                self.assertEqual(result['content_status'],'declared_unverified')
                self.assertEqual(result['granularity'],'standard')
                self.assertEqual(result['focus_status'],'declared_unverified')

    def test_wrong_source_checksum_fails(self):
        b=self.pick();b['source_view_sha256']='0'*64
        with self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_mutated_source_without_pin_update_fails(self):
        b=self.pick();b['view_plan']['nodes'][0]['label']='Changed label'
        with self.assertRaises(LensError):P.render(b,PROFILES[0])

    def test_modified_source_with_pin_still_vp02_validated(self):
        b=self.pick();b['view_plan']['nodes'][0]['anchor_id']='totally.invalid'
        b['source_view_sha256']=source_digest(b['view_plan'])
        with self.assertRaises(LensError):P.render(b,PROFILES[0])

    def test_invalid_bundle_fields(self):
        for mutate in [lambda b:b.update(format='bad'),lambda b:b.update(lens_profile='VP-02'),lambda b:b.update(reference_version='v9.3'),lambda b:b.update(basis='verified'),lambda b:b.update(extra=True),lambda b:b.pop('facet_bindings')]:
            b=self.pick();mutate(b)
            with self.subTest(b=b.keys()),self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_wrong_facet_kind_and_target(self):
        for kind,target in [('sample','artifact'),('node','missing'),('edge','e99'),('metric','a')]:
            b=self.pick();b['facet_bindings'][0]['target_kind']=kind;b['facet_bindings'][0]['target_id']=target
            with self.subTest(kind=kind,target=target),self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_chart_rejects_node_target(self):
        b=self.pick('chart_inventory');b['facet_bindings'][0]['target_kind']='node'
        with self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_tree_rejects_sample_target(self):
        b=self.pick('tree_modules');b['facet_bindings'][0]['target_kind']='sample'
        with self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_duplicate_facet(self):
        b=self.pick();b['facet_bindings'].append(copy.deepcopy(b['facet_bindings'][0]))
        with self.assertRaisesRegex(LensError,'duplicate'):P.validate(b,PROFILES[0])

    def test_unknown_facet_lens(self):
        b=self.pick();b['facet_bindings'][0]['lens']='cube.lens.security'
        with self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_missing_lens_focus_is_not_inferred(self):
        b=self.pick();b['facet_bindings']=[x for x in b['facet_bindings'] if x['lens']!='cube.lens.epistemology']
        with self.assertRaisesRegex(LensError,'no explicit'):P.validate(b,'cube.lens.epistemology')

    def test_invalid_facet_source(self):
        for bad in ['', 'https://source.example/item', 'evidence:trusted', 'not-a-pointer']:
            b=self.pick();b['facet_bindings'][0]['declaration_ref']=bad
            with self.subTest(value=bad),self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_unverified_only(self):
        for status in ('verified','admitted','PASS','authorized',None):
            b=self.pick();b['facet_bindings'][0]['basis']=status
            with self.subTest(status=status),self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_no_control_char_notes(self):
        b=self.pick();b['facet_bindings'][0]['note']='ok\nspoofed truth'
        with self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_no_more_than_75_bindings(self):
        b=self.pick();b['facet_bindings']=b['facet_bindings']*8
        with self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_escaped_xml_in_label(self):
        b=self.pick();b['view_plan']['nodes'][0]['label']='Artifact & Resource'
        b['source_view_sha256']=source_digest(b['view_plan'])
        svg=P.render(b,PROFILES[0]);root=ET.fromstring(svg)
        self.assertTrue(any('Artifact & Resource' in (x.text or '') for x in root.iter(f'{{{NS}}}text')))
        self.assertNotIn(b'<script',svg)

    def test_view_plan_neutral_preserved(self):
        b=self.pick();b['view_plan']['lens']='cube.lens.semantics'
        b['source_view_sha256']=source_digest(b['view_plan'])
        with self.assertRaises(LensError):P.render(b,PROFILES[0])

    def test_no_view_renaming(self):
        b=self.pick();b['view_plan']['view']='flow'
        b['source_view_sha256']=source_digest(b['view_plan'])
        with self.assertRaises(LensError):P.render(b,PROFILES[0])

    def test_unknown_facet_extra_fields(self):
        b=self.pick();b['facet_bindings'][0]['grants_authority']=True
        with self.assertRaises(LensError):P.validate(b,PROFILES[0])

    def test_cli_output_report(self):
        bundle=ROOT/'lens_bundles/flow_migration.json'
        with tempfile.TemporaryDirectory() as t:
            svg=Path(t)/'out.svg';rep=Path(t)/'out.json'
            run=subprocess.run([sys.executable,'-m','vplenses','--input',str(bundle),'--lens',PROFILES[0],'--output',str(svg),'--report',str(rep)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            result=json.loads(rep.read_text('utf8'))
            self.assertEqual(result['svg_sha256'],hashlib.sha256(svg.read_bytes()).hexdigest())

    def test_cli_rejects_duplicate_json_fields(self):
        with tempfile.TemporaryDirectory() as t:
            bad=Path(t)/'bad.json';bad.write_text('{"format":"x","format":"y"}',encoding='utf8')
            output=Path(t)/'no.svg'
            run=subprocess.run([sys.executable,'-m','vplenses','--input',str(bad),'--lens',PROFILES[0],'--output',str(output)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            self.assertNotEqual(run.returncode,0);self.assertFalse(output.exists())

if __name__=='__main__':unittest.main()
