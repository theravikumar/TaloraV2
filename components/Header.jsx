"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";

export default function Header() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      logout();
      setShowDropdown(false);
      router.push("/");
    } finally {
      setLoggingOut(false);
    }
  };

  return (
    <header className="flex items-center justify-between px-10 py-5 border-b border-white/10 bg-gradient-to-r from-slate-900 to-slate-800">
      <Link 
        href="/" 
        className="flex items-center gap-2 text-xl font-semibold hover:opacity-80 transition"
        aria-label="Telora Home"
      >
        <span className="bg-gradient-to-r from-cyan-400 to-purple-500 p-2 rounded-lg">📘</span>
        <span className="text-white">Telora</span>
      </Link>

      <nav className="flex gap-8 text-sm text-slate-300" aria-label="Main navigation">
        <Link 
          href="/jobs" 
          className="hover:text-white transition"
          aria-label="Browse available jobs"
        >
          Find Jobs
        </Link>
        <Link 
          href="/resume" 
          className="hover:text-white transition"
          aria-label="Upload resume and find matching jobs"
        >
          Resume Match
        </Link>

        {isAuthenticated ? (
          <div className="relative">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition"
              aria-label="User account menu"
              aria-expanded={showDropdown}
              aria-haspopup="menu"
            >
              <span className="text-white">{user?.email || "Account"}</span>
              <span className="text-xs">▼</span>
            </button>

            {showDropdown && (
              <div 
                className="absolute right-0 mt-2 w-48 bg-slate-800 border border-white/20 rounded-lg shadow-lg z-50"
                role="menu"
              >
                <div className="px-4 py-3 border-b border-white/10">
                  <p className="text-xs text-slate-400">Signed in as</p>
                  <p className="text-white font-medium truncate">{user?.email}</p>
                </div>
                <button
                  onClick={handleLogout}
                  disabled={loggingOut}
                  className="w-full text-left px-4 py-2 text-slate-300 hover:text-white hover:bg-white/10 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  role="menuitem"
                  aria-busy={loggingOut}
                >
                  {loggingOut ? "Logging out..." : "Logout"}
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link 
            href="/auth" 
            className="hover:text-white transition"
            aria-label="Login or register account"
          >
            Login/Register
          </Link>
        )}
      </nav>
    </header>
  );
}