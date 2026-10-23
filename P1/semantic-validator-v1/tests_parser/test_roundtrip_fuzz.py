"""Seeded metamorphic testing against an independently generated AST corpus."""
import random
import sys
from pathlib import Path
import unittest
from decimal import Decimal

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cube_parser import canonical_acg, parse_acg_bytes, validate_ast, json_dump, load_ast_bytes

class MetamorphicRoundTrip(unittest.TestCase):
    def test_seeded_generated_ast_roundtrips(self):
        rng = random.Random(94012026)
        scalar_values=['plain','"quoted"','multi\nline','π','e\u0301',True,False,None,Decimal('12e-30'),Decimal('-0.00'),Decimal('9e80')]
        keys=['Actor','Resource','Artifact','Claim','Wizard','Π','∑','CaseSensitive','Café']
        homes=['X','Y','Z']
        layers=['α','β','ζ']
        qualifiers=['T','F','M','O']
        names=['parent','references','causedBy','related','unknown']
        def params():
            return {f'v{i}':rng.choice(scalar_values) for i in range(rng.randrange(4))}
        def expr(depth):
            if depth>=4: which=0
            else: which=rng.randrange(4)
            if which==0:
                node={'kind':'reference','address':{'home':rng.choice(homes), 'layer':rng.choice(layers),'concept_key':rng.choice(keys)}, 'referent_ref':rng.choice(['a','b','x:y','ü','😀'])}
            elif which==1:
                node={'kind':'relation','predicate_id':rng.choice(names), 'subject':expr(depth+1), 'object':expr(depth+1), 'parameters':params()}
            elif which==2:
                node={'kind':'application','method_id':'audio.duck/v1', 'arguments':[expr(depth+1) for _ in range(rng.randrange(3))], 'parameters':params()}
            else:
                node={'kind':'reference','address':{'home':'Y','layer':'α','concept_key':'Artifact'}, 'referent_ref':'r'}
            if depth<3 and rng.random() < 0.35:
                node={'kind':'qualified','expression':node,'qualifiers':[{'coordinate':rng.choice(qualifiers),'parameters':params()} for _ in range(rng.randint(1,3))]}
            return node
        for i in range(300):
            ast=expr(0)
            with self.subTest(i=i):
                validate_ast(ast)
                acg=canonical_acg(ast)
                back=parse_acg_bytes(acg.encode('utf-8'))
                self.assertEqual(ast,back)
                self.assertEqual(load_ast_bytes(json_dump(ast,indent=None).encode('utf-8')),ast)

if __name__=='__main__':
    unittest.main()
