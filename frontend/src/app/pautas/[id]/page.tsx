"use client";

import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

interface PautaRedirectPageProps {
  params: Promise<{ id: string }>;
}

export default function PautaRedirectPage({ params }: PautaRedirectPageProps) {
  const { id } = use(params);
  const router = useRouter();

  useEffect(() => {
    router.replace(`/pautas/${id}/review`);
  }, [id, router]);

  return null;
}
