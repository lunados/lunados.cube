"""Build only authored VP-02 examples. Not part of production rendering."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def node(id,anchor,label,form,ref=None,accent=None):
    a={'id':id,'anchor_id':anchor,'label':label,'form_id':form}
    if ref:a['semantic_ref']=ref
    if accent:a['color_token']=accent
    return a

def edge(a,b,predicate,ref):
    return {'from':a,'to':b,'predicate_id':predicate,'declaration_ref':ref,'arrow_anchor_id':'relation-arrows.reference'}

def basis(view,title,subtitle):
    return {'printer_profile':'P2-VP-VIEWS/0.2.0','reference_version':'v9.4','view':view,'lens':'neutral','granularity':'standard','title':title,'subtitle':subtitle}

f=basis('cube.flow','Artifact → Resource · Migration','Fixture: P1 migration relation · typing must be checked separately')
f.update(nodes=[node('artifact','resource-objects.artifact','Artifact · migration A','form.resource-card','Y:α:Artifact["migration-artifact"]'),node('resource','resource-objects.resource','Resource · migration R','form.resource-card','Y:α:Resource["migration-resource"]')],order=['artifact','resource'],edges=[edge('artifact','resource','references','P1.1:fixture/migration.binding-context.json#predicate_contracts/references')],direction='left-to-right',declaration_status='declared_unverified')

f2=basis('cube.flow','Annotation links · Research','Illustrative extension of P1 metaphysics fixture · declarations unverified')
f2.update(nodes=[node('annotation-a','resource-objects.evidence','Annotation / Claim A','form.resource-card','fixture:metaphysics/annotation-a'),node('annotation-b','resource-objects.evidence','Annotation / Claim B','form.resource-card','fixture:metaphysics/annotation-b'),node('annotation-c','resource-objects.source','Source / Claim C','form.resource-card','fixture:metaphysics/source-c')],order=['annotation-a','annotation-b','annotation-c'],edges=[edge('annotation-a','annotation-b','related','fixture:VP02/relations/e1'),edge('annotation-b','annotation-c','references','fixture:VP02/relations/e2')],direction='top-down',declaration_status='declared_unverified')

c1=basis('cube.diagramm','Resource inventory · Declared sample','Synthetic planning counts · NOT observations of any repository')
c1.update(plot='bar',metric={'id':'fixture.resource_count','unit':'items','scale':'linear_zero_based','declaration_ref':'fixture:VP02/measurements/resource-counts-v1','evidence_status':'declared_unverified'},samples=[{'id':'artifact','label':'Artifacts','value':12},{'id':'source','label':'Sources','value':7},{'id':'evidence','label':'Evidence','value':9},{'id':'revisions','label':'Revisions','value':4}])

c2=basis('cube.diagramm','Comparative latency · Declared sample','Synthetic latency values · array order is not verified time order')
c2.update(plot='line',metric={'id':'fixture.latency','unit':'ms','scale':'linear_zero_based','declaration_ref':'fixture:VP02/measurements/latency-v1','evidence_status':'declared_unverified'},samples=[{'id':'s1','label':'Sample A','value':16.2},{'id':'s2','label':'Sample B','value':13.75},{'id':'s3','label':'Sample C','value':9.5},{'id':'s4','label':'Sample D','value':12.1},{'id':'s5','label':'Sample E','value':8.25}])

t1=basis('cube.tree','Module containment · Illustration','Authored hierarchy · not a discovered or admitted runtime architecture')
t1.update(nodes=[node('core','module-bodies.core','Core (declared root)','form.module-block'),node('runtime','module-bodies.runtime','Runtime','form.module-block'),node('adapter','module-bodies.adapter','Adapter','form.module-block'),node('connector','module-bodies.connector','Connector','form.module-block'),node('toolbox','module-bodies.toolbox','Toolbox','form.module-block')],order=['core','runtime','adapter','connector','toolbox'],root_id='core',declaration_status='declared_unverified',edges=[edge('core','runtime','contains','fixture:VP02/tree/t1'),edge('core','adapter','contains','fixture:VP02/tree/t2'),edge('core','connector','contains','fixture:VP02/tree/t3'),edge('core','toolbox','contains','fixture:VP02/tree/t4')])

t2=basis('cube.tree','Resource family · Illustration','Explicitly authored grouping · no universal containment signature claimed')
t2.update(nodes=[node('resource','resource-objects.resource','Resource collection','form.resource-card'),node('artifact','resource-objects.artifact','Artifact','form.resource-card'),node('source','resource-objects.source','Source','form.resource-card'),node('revision','resource-objects.revision','Revision','form.resource-card'),node('evidence','resource-objects.evidence','Evidence','form.resource-card'),node('cache','resource-objects.cache','Cache','form.resource-card')],order=['resource','artifact','source','cache','revision','evidence'],root_id='resource',declaration_status='declared_unverified',edges=[edge('resource','artifact','groups','fixture:VP02/tree/t2.1'),edge('resource','source','groups','fixture:VP02/tree/t2.2'),edge('resource','cache','groups','fixture:VP02/tree/t2.3'),edge('artifact','revision','groups','fixture:VP02/tree/t2.4'),edge('artifact','evidence','groups','fixture:VP02/tree/t2.5')])

fixtures=[('01_cube_flow_migration',f),('02_cube_flow_research',f2),('03_cube_diagramm_bar',c1),('04_cube_diagramm_line',c2),('05_cube_tree_modules',t1),('06_cube_tree_resources',t2)]
for name,content in fixtures:(R/'view_fixtures'/f'{name}.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n','utf8')
print('Authored',len(fixtures),'VP-02 fixtures')
