import { redirect } from "next/navigation";

interface PautaRedirectPageProps {
  params: Promise<{ id: string }>;
}

export default async function PautaRedirectPage({ params }: PautaRedirectPageProps) {
  const { id } = await params;
  redirect(`/pautas/${id}/review`);
}
