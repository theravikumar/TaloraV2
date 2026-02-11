"use client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { login, register } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { LoadingSpinner, ErrorMessage, SuccessMessage } from "../components/UI";

export default function AuthPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams?.get("redirect") || "/";
  const { login: authLogin } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    
    // Validate inputs
    if (!email.trim()) {
      setError("Please enter your email address");
      return;
    }
    
    if (!password.trim()) {
      setError("Please enter your password");
      return;
    }
    
    if (!isLogin && password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address");
      return;
    }
    
    setLoading(true);
    setError("");
    setSuccess("");
    
    try {
      if (isLogin) {
        const response = await login(email, password);
        
        // Validate response structure
        if (!response.user_id || !response.email || !response.token) {
          console.error("Invalid response structure:", response);
          throw new Error("Invalid response from server. Please try again.");
        }

        const loginSuccess = authLogin(
          { 
            id: response.user_id, 
            email: response.email,
            expiresIn: response.expires_in 
          },
          response.token
        );

        if (!loginSuccess) {
          throw new Error("Failed to save login information. Please try again.");
        }

        setSuccess("✓ Logged in successfully! Redirecting...");
        setTimeout(() => router.push(redirect), 1500);
      } else {
        // Register
        const response = await register(email, password);
        
        if (response && response.token) {
          // If registration returns a token, auto-login
          const loginSuccess = authLogin(
            { 
              id: response.user_id, 
              email: response.email,
              expiresIn: response.expires_in 
            },
            response.token
          );
          if (loginSuccess) {
            setSuccess("✓ Account created and logged in! Redirecting...");
            setTimeout(() => router.push(redirect), 1500);
          }
        } else {
          // Just redirect to login
          setSuccess("✓ Account created successfully! Please log in.");
          setEmail("");
          setPassword("");
          setIsLogin(true);
        }
      }
    } catch (err) {
      console.error("Auth error:", err);
      const errorMessage = err.message || "An error occurred. Please try again.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="w-full max-w-md mx-auto px-4">
        <div className="bg-white/10 backdrop-blur-md border border-white/20 p-8 rounded-2xl shadow-2xl">
          <h2 className="text-3xl font-bold mb-6 text-white text-center">
            {isLogin ? "Welcome Back" : "Create Account"}
          </h2>

          {error && <ErrorMessage message={error} onDismiss={() => setError("")} />}
          {success && (
            <SuccessMessage message={success} onDismiss={() => setSuccess("")} />
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="email" className="block text-slate-200 text-sm font-medium mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
                required
                disabled={loading}
                aria-label="Email address"
                aria-required="true"
              />
            </div>

            <div className="mb-6">
              <label htmlFor="password" className="block text-slate-200 text-sm font-medium mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder={isLogin ? "Enter your password" : "Min. 8 characters"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
                required
                minLength={isLogin ? 1 : 8}
                disabled={loading}
                aria-label="Password"
                aria-required="true"
                aria-describedby={!isLogin ? "password-hint" : undefined}
              />
              {!isLogin && (
                <p id="password-hint" className="text-xs text-slate-400 mt-1">
                  Password must be at least 8 characters
                </p>
              )}
            </div>

            {loading ? (
              <LoadingSpinner />
            ) : (
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white py-2 rounded-lg font-semibold hover:shadow-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
                aria-busy={loading}
              >
                {isLogin ? "Login" : "Register"}
              </button>
            )}
          </form>

          <div className="mt-6 text-center">
            <p className="text-slate-400 text-sm mb-4">
              {isLogin ? "Don't have an account?" : "Already have an account?"}
            </p>
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError("");
                setSuccess("");
              }}
              className="text-cyan-400 hover:text-cyan-300 font-semibold transition"
              disabled={loading}
            >
              {isLogin ? "Create one now" : "Sign in instead"}
            </button>
          </div>
        </div>

        <p className="text-center text-slate-400 text-xs mt-8">
          By signing up, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}

