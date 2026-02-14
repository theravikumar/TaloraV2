"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../context/AuthContext";
import { LoadingSpinner, ErrorMessage, SuccessMessage, InfoMessage } from "../components/UI";

const STATUS_MESSAGES = {
  pending: "📋 Your resume is queued for processing...",
  processing: "⚙️ Analyzing your resume...",
  completed: "✅ Resume analyzed successfully!",
  failed: "❌ Failed to process resume",
};

export default function ResumePage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState(null); // { status: "pending" | "processing" | "completed" | "failed", ... }
  const [statusMessage, setStatusMessage] = useState("");
  const [matches, setMatches] = useState([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [parsedSummary, setParsedSummary] = useState("");

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth?redirect=/resume");
    }
  }, [isAuthenticated, authLoading, router]);

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) {
      setError("Please select a resume file to upload");
      return;
    }

    // Validate file type
    if (file.type !== "application/pdf") {
      setError("Please upload a PDF file. Other formats coming soon!");
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");
    setStatus(null);
    setMatches([]);
    setParsedSummary("");

    try {
      // Import API functions dynamically to ensure latest version
      const { searchByResume, getSmartSearchStatus } = await import("../lib/api");

      // 1. Upload and parse resume immediately
      // This uses the new Smart Search API which is more robust
      const result = await searchByResume(file, 10);

      // Handle immediate success (cached or fast processing)
      if (result.status === "completed" && result.matches) {
        setMatches(result.matches);
        setStatus({ status: "completed" });

        let summaryText = "Resume processed successfully.";
        if (result.result && result.result.skills && result.result.skills.length > 0) {
          summaryText += ` Detected skills: ${result.result.skills.join(", ")}.`;
        }
        setParsedSummary(summaryText);
        setSuccess(`Found ${result.matches.length} matching jobs!`);
        setUploading(false);
      }
      // Handle async processing
      else if (result.status === "processing") {
        setStatus({ status: "processing" });
        setStatusMessage("Analyzing your resume... This may take up to 30 seconds.");

        const jobId = result.job_id;
        let attempts = 0;
        const maxAttempts = 30; // 30 seconds max

        const pollInterval = setInterval(async () => {
          attempts++;
          try {
            const statusRes = await getSmartSearchStatus(jobId, 10);

            if (statusRes.status === "completed") {
              clearInterval(pollInterval);

              setMatches(statusRes.matches || []);
              setStatus({ status: "completed" });

              let summaryText = "Resume processed successfully.";
              if (statusRes.result && statusRes.result.skills && statusRes.result.skills.length > 0) {
                summaryText += ` Detected skills: ${statusRes.result.skills.join(", ")}.`;
              }
              setParsedSummary(summaryText);
              setSuccess(`Found ${statusRes.matches?.length || 0} matching jobs!`);
              setUploading(false);

            } else if (statusRes.status === "failed" || attempts >= maxAttempts) {
              clearInterval(pollInterval);
              setError("Resume processing failed or timed out. Please try again.");
              setStatus({ status: "failed" });
              setUploading(false);
            }
          } catch (err) {
            clearInterval(pollInterval);
            console.error("Polling error:", err);
            // Don't fail immediately on polling error, might be temporary
            if (attempts >= maxAttempts) {
              setError("Error checking status: " + err.message);
              setUploading(false);
            }
          }
        }, 1000); // Poll every second
      } else {
        // Fallback for unexpected status
        throw new Error("Unexpected response from server");
      }

    } catch (err) {
      console.error("Upload error:", err);
      let errorMessage = "Failed to upload resume. Please try again.";
      if (err.message) errorMessage = err.message;
      setError(errorMessage);
      setUploading(false);
    }
  }

  if (authLoading) {
    return (
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-300 mb-4">Loading...</p>
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-300 mb-4">Redirecting to login...</p>
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen py-8">
      <div className="max-w-2xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Resume Matching</h1>
          <p className="text-slate-400">
            Upload your resume to find jobs that match your skills and experience
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-8 mb-8">
          <h2 className="text-xl font-semibold text-white mb-6">Step 1: Upload Resume</h2>

          {error && <ErrorMessage message={error} onDismiss={() => setError("")} />}
          {success && (
            <SuccessMessage message={success} onDismiss={() => setSuccess("")} />
          )}

          <form onSubmit={handleUpload} className="space-y-4">
            {/* File Input */}
            <div className="relative">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                id="file-input"
                disabled={uploading}
              />
              <label
                htmlFor="file-input"
                className="flex items-center justify-center w-full p-6 border-2 border-dashed border-white/30 rounded-lg cursor-pointer hover:border-cyan-400 transition"
              >
                <div className="text-center">
                  <p className="text-slate-300 font-medium">
                    {file ? file.name : "📄 Click to upload or drag and drop"}
                  </p>
                  <p className="text-sm text-slate-400">
                    PDF Only (Max 5MB)
                  </p>
                </div>
              </label>
            </div>

            {/* Upload Button */}
            {uploading ? (
              <div className="flex flex-col items-center justify-center py-4">
                <LoadingSpinner />
                <p className="text-slate-300 mt-2">{statusMessage || "Uploading..."}</p>
              </div>
            ) : (
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!file || uploading}
              >
                Upload & Find Matches
              </button>
            )}
          </form>

          <p className="text-xs text-slate-400 text-center mt-4">
            Your resume will be analyzed using AI to understand your skills, experience, and qualifications.
          </p>
        </div>

        {/* Parsed Summary Section */}
        {parsedSummary && (
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-8 mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Resume Analysis</h2>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <p className="text-slate-300 text-sm">{parsedSummary}</p>
            </div>
          </div>
        )}

        {/* Matches Section */}
        {matches.length > 0 && (
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-8">
            <h2 className="text-xl font-semibold text-white mb-6">Step 3: Recommended Jobs</h2>

            <div className="space-y-4">
              {matches.map((match, index) => (
                <div
                  key={index}
                  className="bg-white/5 border border-white/10 rounded-lg p-6 hover:bg-white/10 transition"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white">
                        {match.job?.job_title || "Job Title"}
                      </h3>
                      <p className="text-slate-300 text-sm">
                        {match.job?.company_name || "Company"}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-cyan-400">
                        {Math.round((match.score || match.match_score || 0) * 100)}%
                      </p>
                      <p className="text-xs text-slate-400">Match Score</p>
                    </div>
                  </div>

                  <div className="mb-3 flex gap-2 flex-wrap">
                    <span className="px-2 py-1 text-xs rounded-full bg-cyan-500/20 text-cyan-300">
                      📍 {match.job?.location || "Remote"}
                    </span>
                    {match.job?.domain && (
                      <span className="px-2 py-1 text-xs rounded-full bg-purple-500/20 text-purple-300">
                        {match.job.domain}
                      </span>
                    )}
                  </div>

                  <button
                    onClick={() => {
                      if (match.job?.job_id) {
                        router.push(`/jobs/${match.job.job_id}`);
                      }
                    }}
                    className="mt-4 w-full px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition"
                  >
                    View Job Details
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!uploading && matches.length === 0 && !status && (
          <InfoMessage message="Upload your resume to get started with intelligent job matching!" />
        )}
      </div>
    </div>
  );
}
