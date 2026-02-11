"use client";
import { useAuth } from "@/context/AuthContext";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { LoadingSpinner } from "./UI";

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted || loading) return;

    if (!isAuthenticated) {
      const redirect = searchParams?.get("redirect") || "/";
      router.push(`/auth?redirect=${encodeURIComponent(redirect)}`);
    }
  }, [isAuthenticated, loading, mounted, router, searchParams]);

  if (!mounted || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return children;
}
