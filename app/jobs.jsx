"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getJobs } from "../lib/api";
import { LoadingSpinner, ErrorMessage } from "../components/UI";
import Autocomplete from "../components/Autocomplete";

export default function JobsPage() {
  const searchParams = useSearchParams();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Check for smart search mode
  const smartMode = searchParams.get("mode") === "smart";
  const matchIds = searchParams.get("match_ids")?.split(",").filter(Boolean) || [];
  const summary = searchParams.get("summary") || "";

  // Initialize filters directly from URL to avoid initial "All jobs" fetch
  const [filters, setFilters] = useState(() => {
    const keywordsParam = searchParams.get("keywords");
    const locationParam = searchParams.get("location");
    const employmentParam = searchParams.get("employment_type");

    return {
      keywords: keywordsParam ? keywordsParam.split(",") : [],
      locations: locationParam ? locationParam.split(",") : [],
      employmentType: employmentParam || "",
    };
  });

  const [pagination, setPagination] = useState({
    limit: 20,
    offset: 0,
    total: 0,
  });

  // Sync state when URL params change (e.g. back/forward button)
  useEffect(() => {
    const keywordsParam = searchParams.get("keywords");
    const locationParam = searchParams.get("location");
    const employmentParam = searchParams.get("employment_type");

    const newFilters = {
      keywords: keywordsParam ? keywordsParam.split(",") : [],
      locations: locationParam ? locationParam.split(",") : [],
      employmentType: employmentParam || "",
    };

    // Only update if different to avoid infinite loops or unnecessary re-renders
    if (JSON.stringify(newFilters) !== JSON.stringify(filters)) {
      setFilters(newFilters);
    }
  }, [searchParams]);

  useEffect(() => {
    fetchJobs();
  }, [filters, pagination.offset, smartMode, matchIds.join(",")]);

  async function fetchJobs() {
    setLoading(true);
    setError("");
    try {
      // In smart search mode, filter by match_ids
      if (smartMode && matchIds.length > 0) {
        const params = {
          ids: matchIds.join(","),
          limit: pagination.limit,
          offset: pagination.offset,
        };

        Object.keys(params).forEach(
          (key) => params[key] === undefined && delete params[key]
        );

        const response = await getJobs(params);

        if (!response) {
          throw new Error("Invalid response from server");
        }

        setJobs(response.jobs || []);
        setPagination((prev) => ({
          ...prev,
          total: response.total || matchIds.length,
        }));
      } else {
        // Regular search mode
        const params = {
          keywords: filters.keywords.length > 0 ? filters.keywords.join(",") : undefined,
          location: filters.locations.length > 0 ? filters.locations.join(",") : undefined,
          employment_type: filters.employmentType || undefined,
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
          if (filters.keywords.length > 0 || filters.locations.length > 0 || filters.employmentType) {
            setError(
              `No jobs found matching your filters. Try adjusting your search criteria.`
            );
          }
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
            {filters.keywords.length > 0 && `for "${filters.keywords.join(", ")}"`}
          </p>
        </div>

        {/* Smart Search Mode Banner */}
        {smartMode && matchIds.length > 0 && (
          <div className="bg-gradient-to-r from-cyan-500/20 to-purple-600/20 border border-cyan-500/30 rounded-lg p-4 mb-6 backdrop-blur">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🎯</span>
              <div>
                <h3 className="text-white font-semibold mb-1">Smart Match Results</h3>
                <p className="text-slate-300 text-sm">
                  Showing {matchIds.length} AI-matched jobs based on your {summary ? "profile" : "resume"}.
                  {summary && <span className="block mt-1 text-slate-400 italic">"{summary.slice(0, 100)}{summary.length > 100 ? "..." : ""}"</span>}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Employment Type Filter Buttons */}
        <div className="flex justify-center gap-3 mb-6">
          {["All", "Full-time", "Contract", "Freelance", "Working student"].map((item) => (
            <button
              key={item}
              onClick={() => {
                setFilters((prev) => ({ ...prev, employmentType: item === "All" ? "" : item }));
                setPagination((prev) => ({ ...prev, offset: 0 }));
              }}
              className={`px-5 py-2 text-sm rounded-full border border-white/20 backdrop-blur transition shadow-sm ${(item === "All" && !filters.employmentType) || filters.employmentType === item
                ? "bg-cyan-500 text-white border-cyan-400"
                : "bg-white/10 hover:bg-white/20 text-white"
                }`}
            >
              {item}
            </button>
          ))}
        </div>

        {/* Filters */}
        <div className="relative z-10 bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6 mb-8 overflow-visible">
          <h3 className="text-white font-semibold mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Job Role / Skill
              </label>
              <Autocomplete
                placeholder="Select job titles or skills..."
                apiEndpoint="http://localhost:8000/api/autocomplete/job-titles"
                selectedValues={filters.keywords}
                onChange={(values) => {
                  setFilters(prev => ({ ...prev, keywords: values }));
                  setPagination(prev => ({ ...prev, offset: 0 }));
                }}
              />
            </div>
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Locations
              </label>
              <Autocomplete
                placeholder="Select locations..."
                apiEndpoint="http://localhost:8000/api/autocomplete/locations"
                selectedValues={filters.locations}
                onChange={(values) => {
                  setFilters(prev => ({ ...prev, locations: values }));
                  setPagination(prev => ({ ...prev, offset: 0 }));
                }}
              />
            </div>
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Employment Type
              </label>
              <select
                name="employmentType"
                value={filters.employmentType}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
              >
                <option value="" className="bg-slate-800">All Types</option>
                <option value="full-time" className="bg-slate-800">Full-time</option>
                <option value="Contract" className="bg-slate-800">Contract</option>
                <option value="Freelance" className="bg-slate-800">Freelance</option>
                <option value="Working student" className="bg-slate-800">Working Student</option>
                <option value="Internship" className="bg-slate-800">Internship</option>
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
                  <div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-lg hover:bg-white/20 transition duration-200 cursor-pointer relative group">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="text-lg font-semibold text-white group-hover:text-cyan-400 transition">
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
                    <div className="flex gap-4 text-slate-400 text-sm mt-2 mb-4">
                      <span>📍 {job.location || "Remote"}</span>
                      <span>📋 {job.requirements_count || "N/A"} requirements</span>
                    </div>

                    <div className="flex justify-between items-center mt-4 border-t border-white/10 pt-4">
                      <span className="text-xs text-slate-500">Posted {new Date(job.posted_date || Date.now()).toLocaleDateString()}</span>

                      {/* Apply Button - Stops propagation to prevent navigation */}
                      {job.job_url ? (
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            window.open(job.job_url, "_blank", "noopener,noreferrer");
                          }}
                          className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white text-sm font-semibold rounded-lg hover:shadow-lg hover:shadow-cyan-500/30 transition-all transform hover:-translate-y-0.5"
                        >
                          Apply Now ↗
                        </button>
                      ) : (
                        <span className="text-sm text-slate-500 italic">No direct apply link</span>
                      )}
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
