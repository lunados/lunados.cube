#!/usr/bin/env python3
"""Derive static MCP Resources list from the signed G4 P0 lock."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'P3/adapters/mcp-local'))
from aiaeao_mcp_local import p0_resources as p0
entries=[{'name':'p0-'+str(i).zfill(2),'uri':e['uri'],
          'mime_type':e['mime_type']}
         for i,e in enumerate(p0.entries(),1)]
entries.append({'name':'p0-index','uri':p0.INDEX_URI,'mime_type':'application/json'})
out=HERE/'gateway/src/p0-registry.json'
out.write_text(json.dumps({'format':'aiaeao.g5-p0-registry/1','resources':entries},indent=2,ensure_ascii=False)+'\n','utf-8')
print('PASS G5 registry:',len(entries),'pinned MCP resources')
