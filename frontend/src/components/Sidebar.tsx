"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart2, HeartPulse, List, Settings, Sparkles } from "lucide-react";
import clsx from "clsx";

const menuItems = [
  { name: "Dashboard", href: "/", icon: BarChart2 },
  { name: "Pautas", href: "/pautas", icon: List },
  { name: "Saúde", href: "/health", icon: HeartPulse },
  { name: "Configurações", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed bottom-0 left-0 z-40 flex h-16 w-full border-t border-slate-200 bg-white md:bottom-auto md:top-0 md:h-screen md:w-64 md:flex-col md:border-r md:border-t-0">
      <div className="hidden h-16 items-center border-b border-slate-200 px-6 md:flex">
        <Link href="/" className="flex items-center gap-2 font-bold text-slate-800">
          <Sparkles className="h-6 w-6 text-green-600" />
          <span>Motor Editorial</span>
        </Link>
      </div>

      <nav className="flex w-full items-center justify-around gap-1 p-2 md:flex-col md:items-stretch md:justify-start md:p-4">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex min-w-20 flex-col items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors md:flex-row md:gap-3 md:py-2 md:text-sm",
                isActive ? "bg-green-50 text-green-700" : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
              )}
            >
              <Icon className={clsx("h-5 w-5", isActive ? "text-green-600" : "text-slate-400")} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
