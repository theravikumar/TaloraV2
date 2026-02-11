"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getJobs } from "../lib/api";
import { LoadingSpinner, ErrorMessage } from "../components/UI";

export default function JobsPage() {
  const searchParams = useSearchParams();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({
    keywords: searchParams.get("keywords") || "",
    location: searchParams.get("location") || "",
    domain: searchParams.get("domain") || "",
  });
  const [pagination, setPagination] = useState({
    limit: 20,
    offset: 0,
    total: 0,
  });

  useEffect(() => {
    fetchJobs();
  }, [filters, pagination.offset]);

  async function fetchJobs() {
    setLoading(true);
    setError("");
    try {
      const params = {
        keywords: filters.keywords || undefined,
        location: filters.location || undefined,
        domain: filters.domain || undefined,
        limit: pagination.limit,
        offset: pagination.offset,
      };

      // Remove undefined values
      Object.keys(params).forEach(
        (key) => params[key] === undefined && delete params[key]
      );

      const response = await getJobs(params);
      
      // Validate response structure
      if (!response) {
        throw new Error("Invalid response from server");
      }
      
      setJobs(response.jobs || []);
      setPagination((prev) => ({
        ...prev,
        total: response.total || 0,
      }));
      
      // Provide feedback if no results
      if (!response.jobs || response.jobs.length === 0) {
        if (filters.keywords || filters.location || filters.domain) {
          setError(
            `No jobs found matching your filters. Try adjusting your search criteria.`
          );
        }
      }
    } catch (err) {
      console.error("Error fetching jobs:", err);
      
      // Provide specific error messages
      let errorMessage = "Failed to load jobs. Please try again.";
      if (err.message.includes("401")) {
        errorMessage = "Your session has expired. Please log in again.";
      } else if (err.message.includes("500")) {
        errorMessage = "Server error. Please try again later.";
      } else if (err.message.includes("network")) {
        errorMessage = "Network error. Please check your connection.";
      } else {
        errorMessage = err.message || errorMessage;
      }
      
      setError(errorMessage);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    
    // Validate input length for keyword searches
    if (name === "keywords" && value.trim().length > 100) {
      setError("Search term cannot exceed 100 characters");
      return;
    }
    
    // Clear error when user starts typing
    if (value.trim()) {
      setError("");
    }
    
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
    setPagination((prev) => ({ ...prev, offset: 0 }));
  };

  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Job Listings</h1>
          <p className="text-slate-400">
            {pagination.total} jobs found{" "}
            {filters.keywords && `for "${filters.keywords}"`}
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6 mb-8">
          <h3 className="text-white font-semibold mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Keywords
              </label>
              <input
                type="text"
                name="keywords"
                value={filters.keywords}
                onChange={handleFilterChange}
                placeholder="Job title, skills..."
                className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
              />
            </div>
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Location
              </label>
              <input
                type="text"
                name="location"
                value={filters.location}
                onChange={handleFilterChange}
                placeholder="City, country..."
                className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
              />
            </div>
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Domain
              </label>
              <select
                name="domain"
                value={filters.domain}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
              >
                <option value="">All Domains</option>
                <option value="engineering">Engineering</option>
                <option value="design">Design</option>
                <option value="product">Product</option>
                <option value="sales">Sales</option>
                <option value="marketing">Marketing</option>
                <option value="data">Data Science</option>
                <option value="finance">Finance</option>
                <option value="hr">Human Resources</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && <ErrorMessage message={error} onDismiss={() => setError("")} />}

        {/* Jobs List */}
        {loading ? (
          <LoadingSpinner />
        ) : jobs.length > 0 ? (
          <>
            <div className="space-y-4 mb-8">
              {jobs.map((job) => (
                <Link
                  key={job.job_id || job.id}
                  href={`/jobs/${job.job_id || job.id}`}
                  className="block"
                >
                  <div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-lg hover:bg-white/20 transition duration-200 cursor-pointer">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="text-lg font-semibold text-white">
                          {job.job_title}
                        </h3>
                        <p className="text-slate-300 text-sm">
                          {job.company_name}
                        </p>
                      </div>
                      {job.domain && (
                        <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 text-xs font-medium">
                          {job.domain}
                        </span>
                      )}
                    </div>
                    <div className="flex gap-4 text-slate-400 text-sm">
                      <span>📍 {job.location || "Remote"}</span>
                      <span>📋 {job.requirements_count || "N/A"} requirements</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2">
                <button
                  onClick={() =>
                    setPagination((prev) => ({
                      ...prev,
                      offset: Math.max(0, prev.offset - prev.limit),
                    }))
                  }
                  disabled={currentPage === 1}
                  className="px-4 py-2 rounded-lg bg-white/10 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20 transition"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-white">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() =>
                    setPagination((prev) => ({
                      ...prev,
                      offset:
                        currentPage < totalPages
                          ? prev.offset + prev.limit
                          : prev.offset,
                    }))
                  }
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 rounded-lg bg-white/10 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20 transition"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-slate-400 text-lg">No jobs found matching your criteria.</p>
            <Link href="/" className="text-cyan-400 hover:text-cyan-300 mt-4 inline-block">
              ← Back to home
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
