"""Validate bounded source facts without running application code or delivery helpers."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def stable(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def blob(ref,path):return subprocess.check_output(['git','-C',str(REPO),'show',ref+':'+path])
def git_tree(entries):
 node={}
 for path,(mode,oid) in entries.items():
  d=node;parts=path.split('/')
  for part in parts[:-1]:d=d.setdefault(part,{})
  d[parts[-1]]=(mode,oid)
 def visit(d):
  b=b''
  for name,v in sorted(d.items(),key=lambda item:(item[0]+('/' if isinstance(item[1],dict) else '')).encode()):
   mode,oid=('40000',visit(v)) if isinstance(v,dict) else v
   b+=mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(oid)
  return hashlib.sha1(b'tree '+str(len(b)).encode()+b'\0'+b).hexdigest()
 return visit(node)
def flat(ref):
 out={}
 for line in subprocess.check_output(['git','-C',str(REPO),'ls-tree','-rz',ref]).split(b'\0'):
  if line:
   meta,path=line.split(b'\t',1);mode,kind,oid=meta.decode().split();out[path.decode()]=(mode,oid)
 return out
parser=argparse.ArgumentParser();parser.add_argument('--evidence-root',type=Path);args=parser.parse_args()
expected={}
for line in (ROOT/'checksums.sha256').read_text().splitlines():
 h,name=line.split('  ',1);p=ROOT/name
 assert not Path(name).is_absolute() and '..' not in Path(name).parts and p.is_file() and not p.is_symlink()
 assert sha(p.read_bytes())==h,name;expected[name]=h
assert set(expected)=={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name!='checksums.sha256' and '__pycache__' not in p.parts}
rows=[json.loads(x) for x in (ROOT/'records.jsonl').read_text().splitlines()];assert len(rows)==7
assert len({r['record_id'] for r in rows})==len(rows)
refs=0
for r in rows:
 assert re.fullmatch('CWTV-FACT-20261010-[0-9]{3}',r['record_id'])
 assert r['evidence_status']=='FULLY_SUPPORTED_WITHIN_SCOPE' and r['evidence_support_percent']==100
 assert r['training_eligibility']=='REFERENCE_ONLY' and r['rights_review_status']=='REVIEW_REQUIRED' and r['training_release'] is False
 assert r['ingested_at'] is None and r['human_review_status']=='NOT_INDIVIDUALLY_ADJUDICATED'
 assert sha(stable(r['payload']))==r['content_sha256']
 for ref in r['source_references']:
  if ref['kind']=='GitHub':
   assert sha(blob(ref['containing_commit'],ref['source_path']))==ref['original_content_sha256'];refs+=1
pin=rows[0]['source_commit']
title='apps/web/src/app/title/[mediaType]/[providerId]/trailers/page.tsx';metadata='apps/web/src/lib/watch/metadata.ts';catalog='apps/web/src/lib/watch/catalog.ts';registry='apps/web/src/lib/watch/registry.json';events='docs/progress/activity/engineering-events.jsonl'
assert 'loadCatalogVideos(mediaType, providerId, selection)' in blob(pin,title).decode()
assert 'primaryTrailer:BONANZA.primaryTrailer' in blob(pin,metadata).decode() and 'primaryTrailer: "S02_CLIP03"' in blob(pin,catalog).decode()
reg=json.loads(blob(pin,registry));assert all(reg[k]['available'] is False for k in ['S02E15','S02E16','S02E17'])
assert 'available:!!source?.available' in blob(pin,metadata).decode()
last=json.loads(blob(pin,events).decode().splitlines()[-1]);assert last['event_id']=='CWTV-EVT-000494' and last['event_type']=='DELIVERY_INSTALLATION_PENDING' and last['result']=='BLOCKED'
assert rows[-1]['source_effective_at']==last['occurred_at'] and all(r['source_effective_at'] is None for r in rows[:-1])
proof=json.loads((ROOT/'artifact-verification.json').read_text());source=flat(proof['qualified_source_commit']);base=flat(proof['base_commit']);red=dict(base);green=dict(base)
for e in proof['payload_inventory']:
 assert source[e['path']]==(e['git_mode'],e['git_blob'])
 assert sha(blob(proof['qualified_source_commit'],e['path']))==e['sha256']
 red[e['path']]=('100644',e['git_blob']);green[e['path']]=(e['git_mode'],e['git_blob'])
assert len(proof['payload_inventory'])==53 and green==source
assert git_tree(red)==proof['delivery']['reconstructed_D003_forced0644_tree']
assert git_tree(green)==proof['qualified_source_tree']==proof['delivery']['reconstructed_D004_explicit_mode_tree']
original_check='NOT_RERUN_ARCHIVES_NOT_PROVIDED'
if args.evidence_root:
 for version in ['D003','D004']:
  root=args.evidence_root/version;m=json.loads((root/'DELIVERY_MANIFEST.json').read_text())
  for entries,prefix in [(m['files'],'payload'),(m['supporting_files'],'')]:
   for e in entries:
    b=(root/prefix/e['path']).read_bytes();assert len(b)==e['bytes'] and sha(b)==e['sha256']
 for e in proof['payload_inventory']:
  b=(args.evidence_root/'D004/payload'/e['path']).read_bytes();assert b==(args.evidence_root/'D003/payload'/e['path']).read_bytes() and sha(b)==e['sha256']
 assert 'os.chmod(name,0o644)' in (args.evidence_root/'D003/apply_003.py').read_text()
 assert 'git_mode' in (args.evidence_root/'D004/apply_004.py').read_text()
 original_check='PASS_ALL_PAYLOAD_AND_SUPPORT_HASHES_AND_53_IDENTICAL_PAYLOADS'
print(json.dumps({'status':'PASS','records':len(rows),'git_references_verified':refs,'static_predicates':'PASS','source_and_reconstructed_trees':'PASS','original_artifact_recheck':original_check,'training_release':False,'helpers_executed':False},sort_keys=True))
