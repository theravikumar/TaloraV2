"use client";
import { useEffect, useState } from "react";
import { getJob } from "../../lib/api";
import { useParams, useRouter } from "next/navigation";
import { LoadingSpinner, ErrorMessage } from "../../components/UI";
import Link from "next/link";

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params?.id || (Array.isArray(params) ? params[0] : "");
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!jobId) return;
    fetchJob();
  }, [jobId]);

  async function fetchJob() {
    setLoading(true);
    setError("");
    try {
      if (!jobId) {
        throw new Error("Invalid job ID");
      }
      
      const data = await getJob(jobId);
      
      if (!data) {
        throw new Error("Job not found");
      }
      
      setJob(data);
    } catch (err) {
      console.error("Error fetching job:", err);
      
      // Provide specific error messages
      let errorMessage = "Failed to load job. Please try again.";
      if (err.message.includes("404") || err.message.includes("not found")) {
        errorMessage = "Job not found. It may have been removed.";
      } else if (err.message.includes("401")) {
        errorMessage = "Your session has expired. Please log in again.";
      } else if (err.message.includes("500")) {
        errorMessage = "Server error. Please try again later.";
      } else if (err.message.includes("network")) {
        errorMessage = "Network error. Please check your connection.";
      } else {
        errorMessage = err.message || errorMessage;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  if (loading)
    return (
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );

  if (error)
    return (
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen py-8 px-4">
        <div className="max-w-2xl mx-auto">
          <ErrorMessage message={error} onDismiss={() => setError("")} />
          <Link href="/jobs" className="text-cyan-400 hover:text-cyan-300 block mt-4">
            ← Back to jobs
          </Link>
        </div>
      </div>
    );

  if (!job)
    return (
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen py-8 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <p className="text-slate-300 text-lg mb-4">Job not found.</p>
          <Link href="/jobs" className="text-cyan-400 hover:text-cyan-300">
            ← Back to jobs
          </Link>
        </div>
      </div>
    );

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen py-8">
      <div className="max-w-3xl mx-auto px-4">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="text-cyan-400 hover:text-cyan-300 mb-6 transition flex items-center gap-2"
        >
          ← Back
        </button>

        {/* Job Header */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-8 mb-8">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-white mb-2">{job.job_title}</h1>
              <p className="text-xl text-slate-300 mb-4">{job.company_name}</p>
            </div>
            {job.domain && (
              <div className="px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-300 text-sm font-semibold">
                {job.domain}
              </div>
            )}
          </div>

          {/* Meta Information */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-2 text-slate-300">
              <span className="text-xl">📍</span>
              <span>{job.location || "Remote"}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <span className="text-xl">📋</span>
              <span>{job.requirements_count} Requirements</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <span className="text-xl">⏰</span>
              <span>Full-time</span>
            </div>
          </div>
        </div>

        {/* Description */}
        {job.description && (
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-white mb-4">About the Role</h2>
            <div className="text-slate-300 whitespace-pre-wrap leading-relaxed">
              {job.description}
            </div>
          </div>
        )}

        {/* Requirements */}
        {job.requirements && job.requirements.length > 0 && (
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-white mb-6">Requirements</h2>
            <div className="space-y-3">
              {job.requirements.map((req, index) => (
                <div
                  key={index}
                  className="flex gap-3 p-3 bg-white/5 rounded-lg border border-white/10"
                >
                  <span className="text-cyan-400 font-semibold flex-shrink-0">✓</span>
                  <div className="flex-1">
                    <p className="text-white font-medium">
                      {req.skill || req.name || req.requirement || "Unknown Requirement"}
                    </p>
                    {(req.proficiency || req.level) && (
                      <p className="text-xs text-slate-400">
                        Level: {req.proficiency || req.level}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Call to Action */}
        <div className="bg-gradient-to-r from-cyan-500/20 to-purple-600/20 border border-cyan-500/50 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold text-white mb-4">Ready to Apply?</h3>
          <p className="text-slate-300 mb-6">
            Upload your resume to see how well it matches this role and get personalized recommendations.
          </p>
          <Link
            href="/resume"
            className="inline-block px-8 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition"
          >
            Upload Your Resume
          </Link>
        </div>

        {/* Job ID */}
        <p className="text-xs text-slate-500 text-center mt-8">
          Job ID: {jobId}
        </p>
      </div>
    </div>
  );
}
