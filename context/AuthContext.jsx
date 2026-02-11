"use client";
import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch (err) {
        // If parsing fails, clear invalid data
        console.error("Error parsing saved user data:", err);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }
    setLoading(false);
  }, []);

  const login = (userData, tokenValue) => {
    if (!userData || !tokenValue) {
      setError("Invalid user data or token");
      return false;
    }
    try {
      setUser(userData);
      setToken(tokenValue);
      localStorage.setItem("token", tokenValue);
      localStorage.setItem("user", JSON.stringify(userData));
      setError(null);
      return true;
    } catch (err) {
      console.error("Error during login:", err);
      setError("Failed to save login information");
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    try {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    } catch (err) {
      console.error("Error clearing localStorage:", err);
    }
    setError(null);
  };

  const setAuthError = (err) => {
    setError(err);
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    token,
    loading,
    error,
    login,
    logout,
    setAuthError,
    clearError,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}