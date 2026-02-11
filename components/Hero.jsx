// import { Search, MapPin } from "lucide-react"
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Hero() {
  const router = useRouter();
  const [keywords, setKeywords] = useState("");
  const [location, setLocation] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!keywords.trim()) return;
    
    setLoading(true);
    const params = new URLSearchParams();
    if (keywords) params.append("keywords", keywords);
    if (location) params.append("location", location);
    
    router.push(`/jobs?${params.toString()}`);
  };

  return (
    <section className="relative py-28 text-center overflow-hidden">
      
      {/* Soft background glow */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-24 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-cyan-400/10 blur-[120px]" />
        <div className="absolute top-40 left-1/3 w-[300px] h-[300px] bg-purple-500/10 blur-[120px]" />
      </div>

      {/* Badge */}
      <span className="inline-flex items-center gap-2 mb-5 px-5 py-1.5 text-xs rounded-full bg-cyan-500/10 text-cyan-500 shadow-sm">
        🌍 Global Job Opportunities
      </span>

      {/* Heading */}
      <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-5">
        Find Your Dream Job{" "}
        <span className="bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
          Anywhere
        </span>
      </h1>

      {/* Sub text */}
      <p className="text-slate-500 max-w-2xl mx-auto mb-14 leading-relaxed">
        Discover thousands of opportunities from companies worldwide.
        Your next career move starts here.
      </p>

      {/* Search Card */}
      <form onSubmit={handleSearch} className="max-w-4xl mx-auto bg-white/70 backdrop-blur-xl border border-slate-200 shadow-xl rounded-2xl p-4 md:p-6 flex flex-col md:flex-row gap-4">
        
        {/* Job Input */}
        <div className="flex items-center gap-3 bg-white rounded-xl px-4 py-3 border focus-within:ring-2 ring-cyan-500/40 transition">
          {/* <Search className="w-5 h-5 text-slate-400" /> */}
          <input
            className="w-full outline-none text-sm"
            placeholder="Job title, keyword, or company"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
          />
        </div>

        {/* Location Input */}
        <div className="flex items-center gap-3 bg-white rounded-xl px-4 py-3 border focus-within:ring-2 ring-purple-500/40 transition">
          {/* <MapPin className="w-5 h-5 text-slate-400" /> */}
          <input
            className="w-full outline-none text-sm"
            placeholder="City, state, or country"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>

        {/* CTA */}
        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-medium shadow-lg hover:shadow-xl hover:scale-[1.02] transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {/* <Search className="w-4 h-4" /> */}
          {loading ? "Searching..." : "Search Jobs"}
        </button>
      </form>

      {/* Filters */}
      <div className="flex justify-center gap-3 mt-10">
        {["All", "Remote", "On-site", "Hybrid"].map((item) => (
          <button
            key={item}
            onClick={() => {
              setKeywords("");
              setLocation("");
              router.push(`/jobs?type=${item.toLowerCase()}`);
            }}
            className="px-5 py-2 text-sm rounded-full border border-slate-200 bg-white/60 backdrop-blur hover:bg-white shadow-sm transition"
          >
            {item}
          </button>
        ))}
      </div>
    </section>
  )
}
