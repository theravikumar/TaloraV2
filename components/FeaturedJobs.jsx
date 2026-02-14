"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getJobs } from "@/lib/api";
import { LoadingSpinner, ErrorMessage } from "./UI";

export default function FeaturedJobs({ filters = {} }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const hasFilters = (filters.keywords && filters.keywords.length > 0) || (filters.locations && filters.locations.length > 0);

  useEffect(() => {
    fetchJobs();
  }, [filters]);

  async function fetchJobs() {
    setLoading(true);
    try {
      const params = {
        limit: hasFilters ? 20 : 6,
        keywords: filters.keywords?.join(","),
        location: filters.locations?.join(","),
      };

      const response = await getJobs(params);
      setJobs(response.jobs || []);
    } catch (err) {
      console.error("Error fetching jobs:", err);
      setError(err.message || "Failed to load jobs");
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="px-10 pb-20">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">
          {hasFilters ? "Search Results" : "Featured Jobs"}
        </h2>
        <Link href="/jobs" className="text-cyan-400 hover:text-cyan-300 transition">
          View All →
        </Link>
      </div>

      {error && (
        <ErrorMessage
          message={error}
          onDismiss={() => setError("")}
        />
      )}

      {loading ? (
        <LoadingSpinner />
      ) : jobs.length > 0 ? (
        <div className="space-y-4">
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
      ) : (
        <div className="text-center py-12">
          <p className="text-slate-400">No jobs found matching your criteria.</p>
          {!hasFilters && (
            <Link href="/jobs" className="text-cyan-400 hover:text-cyan-300 mt-4 inline-block">
              Browse all jobs →
            </Link>
          )}
        </div>
      )}
    </section>
  );
}
