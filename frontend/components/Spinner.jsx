"use client";

import { Loader2 } from "lucide-react";

export default function Spinner({ size = 16, className = "" }) {
  return (
    <Loader2
      size={size}
      strokeWidth={2.5}
      className={`animate-spin ${className}`}
    />
  );
}
