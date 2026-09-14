import UnderDevelopmentPanel from "@/components/site/UnderDevelopmentPanel";

export default async function UnderDevelopmentPage({ params }: { params: Promise<{ feature: string }> }) {
  const { feature } = await params;
  return <UnderDevelopmentPanel feature={feature} />;
}
