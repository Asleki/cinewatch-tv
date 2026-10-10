"use client";
import { useEffect,useState,useRef } from "react";
import Link from "next/link";
import { BONANZA } from "@/lib/watch/catalog";
export default function AuthorizePage() {
 const started=useRef(false);
 const [message,setMessage]=useState("Completing sign-in…");
 useEffect(()=>{
  if(started.current)return;started.current=true;
  const params=new URLSearchParams(window.location.hash.slice(1));
  const token=params.get("token"),state=params.get("state");
  window.history.replaceState(null,"","/stream-now/authorize");
  if(!token||!state){queueMicrotask(()=>setMessage("Please sign in again."));return;}
  void fetch("/api/cinewatch/watch/session",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token,state})}).then(r=>{if(!r.ok)throw Error();window.location.replace(BONANZA.path);}).catch(()=>setMessage("Sign-in could not be completed. Please try again."));
 },[]);
 return <section><h1>CineWatch</h1><p role="status">{message}</p><Link href="/api/cinewatch/watch/sign-in">Sign in</Link></section>;
}
