"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart2, 
  FilePlus, 
  List, 
  Settings, 
  Sparkles, 
  CheckCircle2,
  UploadCloud 
} from "lucide-react";
import clsx from "clsx";

const menuItems = [
  { name: "Dashboard", href: "/", icon: BarChart2 },
  { name: "Pautas", href: "/pautas", icon: List },
  { name: "Nova Pauta", href: "/pautas/nova", icon: FilePlus },
  { name: "Importar Planilha", href: "/import", icon: UploadCloud },
  { name: "Templates", href: "/templates", icon: Sparkles },
  { name: "Configurações", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-slate-200 bg-white">
      <div className="flex h-16 items-center border-bottom border-slate-200 px-6">
        <Link href="/" className="flex items-center gap-2 font-bold text-slate-800">
          <Sparkles className="h-6 w-6 text-green-600" />
          <span>Easy Artigos</span>
        </Link>
      </div>

      <nav className="flex flex-col gap-1 p-4">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive 
                  ? "bg-green-50 text-green-700" 
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <Icon className={clsx("h-5 w-5", isActive ? "text-green-600" : "text-slate-400")} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer / Status simples */}
      <div className="absolute bottom-0 w-full p-4 border-t border-slate-200 bg-slate-50">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <CheckCircle2 className="h-4 w-4 text-green-500" />
          <span>Backend Conectado</span>
        </div>
      </div>
    </aside>
  );
}
