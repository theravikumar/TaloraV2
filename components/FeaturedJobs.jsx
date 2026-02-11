"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getJobs } from "@/lib/api";
import JobCard from "./JobCard";
import { LoadingSpinner, ErrorMessage } from "./UI";

export default function FeaturedJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchFeaturedJobs();
  }, []);

  async function fetchFeaturedJobs() {
    try {
      const response = await getJobs({ limit: 6 });
      setJobs(response.jobs || []);
    } catch (err) {
      console.error("Error fetching featured jobs:", err);
      setError(err.message || "Failed to load featured jobs");
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="px-10 pb-20">
      <div className="flex justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Featured Jobs</h2>
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
        <div className="grid md:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <Link key={job.job_id || job.id} href={`/jobs/${job.job_id || job.id}`}>
              <JobCard job={job} />
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-slate-400">No featured jobs available at the moment.</p>
          <Link href="/jobs" className="text-cyan-400 hover:text-cyan-300 mt-4 inline-block">
            Browse all jobs →
          </Link>
        </div>
      )}
    </section>
  );
}
