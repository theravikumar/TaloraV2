"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { uploadResume, getResumeStatus, matchResume } from "../lib/api";
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
  const [jobId, setJobId] = useState(""); // ParsingJob ID
  const [resumeId, setResumeId] = useState(""); // Actual Resume ID
  const [status, setStatus] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");
  const [matches, setMatches] = useState([]);
  const [matchLoading, setMatchLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [checkStatusInterval, setCheckStatusInterval] = useState(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth?redirect=/resume");
    }
  }, [isAuthenticated, authLoading, router]);

  // Auto-check status periodically
  useEffect(() => {
    if (status?.status === "pending" && jobId) {
      const interval = setInterval(() => {
        checkStatus();
      }, 2000);
      setCheckStatusInterval(interval);
      return () => clearInterval(interval);
    }
    return () => checkStatusInterval && clearInterval(checkStatusInterval);
  }, [status?.status, jobId]);

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) {
      setError("Please select a resume file to upload");
      return;
    }

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt'];
    
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
      setError(`Invalid file type. Supported formats: PDF, DOC, DOCX, TXT`);
      setFile(null);
      return;
    }

    // Validate file size (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
      setError(`File is too large (${sizeMB}MB). Maximum allowed size is 5MB.`);
      setFile(null);
      return;
    }

    // Validate minimum file size (100 bytes)
    if (file.size < 100) {
      setError("File is too small. Please upload a valid resume.");
      setFile(null);
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");
    setStatus(null);
    setMatches([]);
    setResumeId(""); // Reset resume ID

    try {
      const res = await uploadResume(file);
      
      setStatus(res);
      setJobId(res.job_id || "");
      // Extract resume ID if already completed
      if (res.resume?.resume_id) {
        setResumeId(res.resume.resume_id);
      }
      setStatusMessage(STATUS_MESSAGES[res.status]);
      
      if (res.status === "completed") {
        setSuccess("Resume uploaded and processed successfully!");
      } else {
        setStatusMessage("Processing your resume... This may take a minute.");
      }
    } catch (err) {
      console.error("Upload error:", err);
      
      // Provide specific error messages
      let errorMessage = "Failed to upload resume. Please try again.";
      if (err.message.includes("413")) {
        errorMessage = "File is too large. Maximum size is 5MB.";
      } else if (err.message.includes("400")) {
        errorMessage = "Invalid file format. Please upload a valid resume.";
      } else if (err.message.includes("401")) {
        errorMessage = "Your session has expired. Please log in again.";
      } else if (err.message.includes("timeout")) {
        errorMessage = "Upload took too long. Please try again.";
      } else if (err.message.includes("network")) {
        errorMessage = "Network error. Please check your connection.";
      } else {
        errorMessage = err.message || errorMessage;
      }
      
      setError(errorMessage);
    } finally {
      setUploading(false);
      setFile(null);
    }
  }

  async function checkStatus() {
    if (!jobId) {
      setError("Job ID not found. Please upload a resume first.");
      return;
    }
    
    setError("");
    
    try {
      const res = await getResumeStatus(jobId);
      
      if (!res) {
        throw new Error("Invalid response from server");
      }
      
      setStatus(res);
      setStatusMessage(STATUS_MESSAGES[res.status] || "Processing...");
      
      // Extract resume_id when parsing completes
      if (res.status === "completed" && res.resume?.resume_id && !resumeId) {
        setResumeId(res.resume.resume_id);
      }
      
      if (res.status === "completed" && !success) {
        setSuccess("Resume processing complete!");
      }
      
      if (res.status === "failed") {
        const errorDetail = res.error || "Resume processing failed. Please check your file and try uploading again.";
        setError(errorDetail);
      }
    } catch (err) {
      console.error("Status check error:", err);
      
      // Only show error if it's not a network timeout (which happens during polling)
      if (!err.message.includes("timeout")) {
        const errorMessage = err.message.includes("404") 
          ? "Resume processing job not found. Please upload again."
          : err.message || "Failed to check status. Please try again.";
        
        setError(errorMessage);
      }
    }
  }

  async function handleMatch() {
    if (!resumeId) {
      setError("Resume ID not found. Please ensure resume processing is complete. Try uploading your resume again.");
      return;
    }

    if (!status || status.status !== "completed") {
      setError("Resume is not ready for matching. Please wait for processing to complete.");
      return;
    }

    setError("");
    setMatchLoading(true);
    
    try {
      const res = await matchResume(resumeId, {}, 10);
      const matchList = res.matches || [];
      setMatches(matchList);
      
      if (matchList.length === 0) {
        setStatusMessage("No matching jobs found at the moment. Try searching manually in the Jobs section or upload an updated resume.");
      } else {
        setSuccess(`Found ${matchList.length} matching job${matchList.length === 1 ? '' : 's'}!`);
      }
    } catch (err) {
      console.error("Match error:", err);
      
      // Provide specific error messages
      let errorMessage = "Failed to find matching jobs. Please try again.";
      if (err.message.includes("401")) {
        errorMessage = "Your session has expired. Please log in again.";
      } else if (err.message.includes("404")) {
        errorMessage = "Resume not found. Please upload your resume again.";
      } else if (err.message.includes("500")) {
        errorMessage = "Server error. Please try again later.";
      } else if (err.message.includes("timeout")) {
        errorMessage = "Request timed out. Please try again.";
      } else if (err.message.includes("network")) {
        errorMessage = "Network error. Please check your connection.";
      } else {
        errorMessage = err.message || errorMessage;
      }
      
      setError(errorMessage);
    } finally {
      setMatchLoading(false);
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
                accept=".pdf,.doc,.docx,.txt"
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
                    PDF, DOC, DOCX, or TXT (Max 5MB)
                  </p>
                </div>
              </label>
            </div>

            {/* Upload Button */}
            {uploading ? (
              <LoadingSpinner />
            ) : (
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!file || uploading}
              >
                {uploading ? "Uploading..." : "Upload Resume"}
              </button>
            )}
          </form>

          <p className="text-xs text-slate-400 text-center mt-4">
            Your resume will be analyzed using AI to understand your skills, experience, and qualifications.
          </p>
        </div>

        {/* Status Section */}
        {status && (
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-8 mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Step 2: Processing Status</h2>
            
            <div className="space-y-4">
              {/* Status Indicator */}
              <div className="flex items-center gap-4 p-4 bg-white/5 rounded-lg">
                <div className="text-3xl">
                  {status.status === "pending" && "⏳"}
                  {status.status === "processing" && "⚙️"}
                  {status.status === "completed" && "✅"}
                  {status.status === "failed" && "❌"}
                </div>
                <div>
                  <p className="text-white font-semibold capitalize">{status.status}</p>
                  <p className="text-slate-400 text-sm">{statusMessage}</p>
                </div>
              </div>

              {/* Job ID */}
              <p className="text-xs text-slate-400">
                Job ID: <span className="font-mono text-slate-300">{jobId}</span>
              </p>

              {/* Action Buttons */}
              <div className="flex gap-3">
                {status.status === "pending" && (
                  <button
                    onClick={checkStatus}
                    className="px-4 py-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition"
                  >
                    Check Status Now
                  </button>
                )}

                {status.status === "completed" && (
                  <>
                    {matches.length === 0 && (
                      <button
                        onClick={handleMatch}
                        className="flex-1 bg-gradient-to-r from-cyan-500 to-purple-600 text-white py-2 rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50"
                        disabled={matchLoading}
                      >
                        {matchLoading ? "Finding Matches..." : "Find Matching Jobs"}
                      </button>
                    )}
                  </>
                )}

                {status.status === "failed" && (
                  <button
                    onClick={() => {
                      setStatus(null);
                      setFile(null);
                      setJobId("");
                    }}
                    className="px-4 py-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition"
                  >
                    Try Again
                  </button>
                )}
              </div>

              {/* Parsed Resume Preview */}
              {status.resume && status.status === "completed" && (
                <div className="mt-6 p-4 bg-white/5 rounded-lg border border-white/10">
                  <p className="text-sm text-slate-300 font-semibold mb-2">Resume Summary:</p>
                  <div className="text-xs text-slate-400 space-y-1">
                    {Object.entries(status.resume).map(([key, value]) => (
                      <p key={key}>
                        <span className="text-slate-300 font-medium capitalize">{key}:</span>{" "}
                        {typeof value === "object" ? JSON.stringify(value) : String(value)}
                      </p>
                    ))}
                  </div>
                </div>
              )}
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
                        {Math.round((match.match_score || 0) * 100)}%
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

                  {match.matched_count !== undefined && match.total_requirements !== undefined && (
                    <div className="mb-4 p-3 bg-white/5 rounded border border-white/10">
                      <p className="text-xs text-slate-300 font-semibold mb-2">
                        Requirements Match: {match.matched_count} / {match.total_requirements}
                      </p>
                      <div className="w-full bg-white/10 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-cyan-500 to-purple-600 h-2 rounded-full"
                          style={{
                            width: `${(match.matched_count / match.total_requirements) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {match.gaps && match.gaps.length > 0 && (
                    <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded">
                      <p className="text-xs text-yellow-300 font-semibold mb-2">Skill Gaps:</p>
                      <ul className="text-xs text-yellow-200 space-y-1">
                        {match.gaps.slice(0, 3).map((gap, i) => (
                          <li key={i}>• {gap.skill || gap.requirement || "Unknown"}</li>
                        ))}
                        {match.gaps.length > 3 && (
                          <li className="text-yellow-300">and {match.gaps.length - 3} more...</li>
                        )}
                      </ul>
                    </div>
                  )}

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
        {!status && (
          <InfoMessage message="Upload your resume to get started with intelligent job matching!" />
        )}
      </div>
    </div>
  );
}
