import Image from "next/image";
import { useState } from "react";
import type React from "react";

declare module "react" {
  interface HTMLAttributes<T> {
    src?: string;
    autoplay?: boolean;
    loop?: boolean;
  }
}

declare module "react/jsx-runtime" {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace JSX {
    interface IntrinsicElements {
      "dotlottie-wc": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement>,
        HTMLElement
      >;
    }
  }
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace JSX {
    interface IntrinsicElements {
      "dotlottie-wc": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement>,
        HTMLElement
      > & {
        src?: string;
        autoplay?: boolean;
        loop?: boolean;
      };
    }
  }
}

export function HeaderBar() {
  const [showMomoBubble, setShowMomoBubble] = useState(false);

  return (
    <header className="flex items-center justify-between px-6 py-4 backdrop-blur-md bg-[var(--background)]/80 border-b border-[var(--surface-border)]/50">
      <div className="flex items-center gap-3">
        <div
          className="relative"
          onMouseEnter={() => setShowMomoBubble(true)}
          onMouseLeave={() => setShowMomoBubble(false)}
        >
          <div className="relative w-16 h-16 rounded-full overflow-hidden bg-[var(--surface)] border border-[var(--surface-border)] shadow-[0_0_15px_var(--primary-glow)] cursor-pointer hover:scale-110 transition-transform">
            <Image
              src="/momo_.png"
              alt="Momo the cat mascot"
              fill
              className="object-cover"
              sizes="64px"
              priority
            />
          </div>

          {showMomoBubble && (
            <div className="absolute top-12 left-0 z-50 animate-scale-in">
              <div className="relative px-5 py-4 shadow-lg rounded-[1.5rem] rounded-tl-sm bg-[var(--forest)] border-2 border-[var(--forest-border)] text-gray-100 max-w-xs w-max">
                <p className="text-sm leading-relaxed">Hi! I am Momo 🐱</p>
                <div className="absolute -top-2 left-4 w-4 h-4 bg-[var(--forest)] border-t-2 border-l-2 border-[var(--forest-border)] rotate-45"></div>
              </div>
            </div>
          )}
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Lowkey</h1>
      </div>
      <div className="hidden sm:flex items-center justify-center rounded-full bg-[var(--surface)] border border-[var(--surface-border)] px-4 py-1.5">
        <span className="text-xs font-bold text-gray-300 tracking-wide uppercase">
          hidden gems only
        </span>
      </div>
    </header>
  );
}
