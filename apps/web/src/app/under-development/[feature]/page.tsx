import { permanentRedirect } from "next/navigation";
import UnderDevelopmentPanel from "@/components/site/UnderDevelopmentPanel";

export default async function UnderDevelopmentPage({ params }: { params: Promise<{ feature: string }> }) {
  const { feature } = await params;
  if (feature === "stream-now") permanentRedirect("/stream-now");
  return <UnderDevelopmentPanel feature={feature} />;
}
