import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { watchMetadata } from "@/lib/watch/metadata";
import { BONANZA } from "@/lib/watch/catalog";
import WatchExperience from "@/components/watch/WatchExperience";
export const metadata:Metadata={title:"Watch Bonanza · Season 2",robots:{index:false,follow:false}};
export const dynamic="force-dynamic";
export default async function WatchPage({params}:{params:Promise<{seasonId:string}>}) {
 const {seasonId}=await params;if(seasonId!==BONANZA.id)notFound();
 const details=await watchMetadata();if(!details)return <section><h1>Bonanza</h1><p>This title could not be loaded. Please try again.</p></section>;
 return <WatchExperience details={details}/>;
}
