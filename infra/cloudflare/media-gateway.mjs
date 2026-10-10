import ORIGINALS from './registry.mjs';
import RENDITIONS from './renditions.mjs';
export const AUD='97145b7d1ff85af6e9b355598eb35975bd48a10e1a6c04944b6fd7d647bc31f0';
const OWNER='cinewatchtv.stream@gmail.com';
const SITE='https://www.cinewatchtv.com';
const HEADERS={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Cross-Origin-Resource-Policy':'same-origin'};
export function sourceFor(id,quality,derivatives={}) {
 const original=ORIGINALS[id];
 if(!original?.available)return null;
 if(quality==='original')return original;
 const d=derivatives[id];
 if(quality!=='240p'||!d||d.parent_sha256!==original.sha256||d.height!==240||!Number.isSafeInteger(d.bytes)||d.bytes<=0||!/^[0-9a-f]{64}$/.test(d.sha256)||d.key!==`simulated-rights/bonanza/derived/${id}/240p/${d.sha256}.mp4`)return null;
 return d;
}
export function parseRange(value,size) {
 const m=/^bytes=(\d*)-(\d*)$/.exec(value);
 if(!m||(!m[1]&&!m[2]))throw Error('Invalid range');
 let start,end;
 if(!m[1]){const suffix=Number(m[2]);if(!Number.isSafeInteger(suffix)||suffix<=0)throw Error('Invalid suffix');start=Math.max(0,size-suffix);end=size-1;}
 else {start=Number(m[1]);end=m[2]?Number(m[2]):size-1;}
 if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start<0||start>=size||end<start)throw Error('Unsatisfied range');
 end=Math.min(end,size-1);return {offset:start,length:end-start+1};
}
function deny(status=403){return new Response('Playback unavailable',{status,headers:HEADERS});}
export default {async fetch(request,env,ctx){
 try{
  if(!ctx.access||ctx.access.aud!==AUD)return deny();
  const identity=await ctx.access.getIdentity();
  if(identity?.email!==OWNER)return deny();
  const url=new URL(request.url);
  if(!['GET','HEAD'].includes(request.method))return deny(405);
  if(url.pathname==='/identity')return Response.json({email:OWNER,authorized:true},{headers:HEADERS});
  if(url.pathname==='/authorize'){
   const state=url.searchParams.get('state');
   const cookie=/(?:^|;\s*)CF_Authorization=([^;]+)/.exec(request.headers.get('Cookie')||'');
   const jwt=request.headers.get('Cf-Access-Jwt-Assertion')||cookie?.[1];
   if(!/^[0-9a-f]{64}$/.test(state||'')||!jwt||jwt.length>12000||! /^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(jwt))return deny(400);
   // Fragment is never sent to the CineWatch server/logs; nonce-bound session exchange follows.
   return new Response(null,{status:303,headers:{...HEADERS,Location:SITE+'/stream-now/authorize#'+new URLSearchParams({token:jwt,state}).toString()}});
  }
  const match=/^\/media\/(S02E\d{2}|S02_CLIP\d{2})\/(original|240p)$/.exec(url.pathname);
  if(!match||!env.MEDIA)return deny(404);
  const variants=RENDITIONS;
  const item=sourceFor(match[1],match[2],variants);if(!item)return deny(403);
  const head=await env.MEDIA.head(item.key);
  if(!head||head.size!==item.bytes||head.customMetadata?.sha256!==item.sha256)return deny(503);
  const headers=new Headers({...HEADERS,'Content-Type':'video/mp4','Accept-Ranges':'bytes'});
  let range;
  if(request.headers.has('Range')){
   try{range=parseRange(request.headers.get('Range'),item.bytes);}catch{headers.set('Content-Range',`bytes */${item.bytes}`);return new Response(null,{status:416,headers});}
   headers.set('Content-Range',`bytes ${range.offset}-${range.offset+range.length-1}/${item.bytes}`);
  }
  headers.set('Content-Length',String(range?.length??item.bytes));
  if(request.method==='HEAD')return new Response(null,{status:range?206:200,headers});
  const object=await env.MEDIA.get(item.key,range?{range}:undefined);
  if(!object?.body)return deny(503);
  return new Response(object.body,{status:range?206:200,headers});
 }catch{return deny(503);}
}};
