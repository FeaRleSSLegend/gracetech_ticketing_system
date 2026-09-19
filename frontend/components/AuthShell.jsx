"use client";

import Image from "next/image";

export default function AuthShell({ children }) {
  return (
    <div className="min-h-screen bg-[#F6F7F9] flex items-center justify-center px-4 font-sans">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center justify-center gap-2 mb-8">
          <Image src="/logo.png" alt="Logo" width={200} height={100} className="object-contain" />
          <span className="text-[15px] font-bold text-gray-900 tracking-tight">
            IT Support
          </span>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
          {children}
        </div>
      </div>
    </div>
  );
}
