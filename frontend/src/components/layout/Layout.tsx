import type { ReactNode } from "react";
import { BackgroundFX } from "./BackgroundFX";
import { Footer } from "./Footer";
import { Header } from "./Header";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex min-h-screen flex-col">
      <BackgroundFX />
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
