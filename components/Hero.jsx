"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Autocomplete from "./Autocomplete";

export default function Hero() {
    const router = useRouter();
    const [searchMode, setSearchMode] = useState("resume"); // "resume" or "quick"
    const [keywords, setKeywords] = useState([]);
    const [locations, setLocations] = useState([]);
    const [employmentType, setEmploymentType] = useState("");
    const [resumeFile, setResumeFile] = useState(null);
    const [summary, setSummary] = useState("");
    const [loading, setLoading] = useState(false);
    const [parsing, setParsing] = useState(false);
    const [parsedSummary, setParsedSummary] = useState(""); // Summary extracted from resume

    // Calculate word count
    const wordCount = (parsedSummary || summary).trim().split(/\s+/).filter(Boolean).length;

    const handleResumeUpload = async (e) => {
        const file = e.target.files[0];
        if (!file || file.type !== "application/pdf") {
            alert("Please upload a PDF file");
            return;
        }

        setResumeFile(file);
        setParsing(true);
        setParsedSummary("");

        try {
            // Import API functions
            const { searchByResume, getSmartSearchStatus } = await import("../lib/api");

            // Upload and parse resume immediately
            const result = await searchByResume(file, 20);

            // Check for immediate completion (cache hit or fast processing)
            // Backend now returns { status: "completed", matches: [...], result: {...} }
            if (result.status === "completed" && result.matches) {
                const count = result.matches.length;
                // Use result.result.skills if available for summary
                let summaryText = `Resume processed successfully! Found ${count} matching jobs.`;
                if (result.result && result.result.skills && result.result.skills.length > 0) {
                    summaryText += ` Detected skills: ${result.result.skills.join(", ")}.`;
                }

                setParsedSummary(summaryText);
                setParsing(false);
            } else if (result.status === "processing") {
                // Async processing - poll for results
                const jobId = result.job_id;
                let attempts = 0;
                const maxAttempts = 30; // 30 seconds max

                const pollInterval = setInterval(async () => {
                    attempts++;
                    try {
                        const status = await getSmartSearchStatus(jobId, 20);

                        if (status.status === "completed") {
                            clearInterval(pollInterval);

                            // Backend polling status returns { job_id, status, matches: [...], result: {...} }
                            let summaryText = "Resume processed successfully.";
                            if (status.matches) {
                                summaryText += ` Found ${status.matches.length} matching jobs.`;
                            }
                            if (status.result && status.result.skills && status.result.skills.length > 0) {
                                summaryText += ` Detected skills: ${status.result.skills.join(", ")}.`;
                            }

                            setParsedSummary(summaryText);
                            setParsing(false);
                        } else if (status.status === "failed" || attempts >= maxAttempts) {
                            clearInterval(pollInterval);
                            alert("Resume processing failed or timed out. Please try again.");
                            setParsing(false);
                            setResumeFile(null);
                        }
                    } catch (err) {
                        clearInterval(pollInterval);
                        alert("Error checking status: " + err.message);
                        setParsing(false);
                        setResumeFile(null);
                    }
                }, 1000); // Poll every second
            }
        } catch (error) {
            alert("Resume upload failed: " + error.message);
            setParsing(false);
            setResumeFile(null);
        }
    };

    const handleSmartSearch = async (e) => {
        e.preventDefault();

        try {
            if (searchMode === "resume") {
                setLoading(true);
                // Use parsed summary or manual summary
                const searchSummary = parsedSummary || summary.trim();

                if (!searchSummary) {
                    alert("Please upload a resume or provide a summary");
                    setLoading(false);
                    return;
                }

                const { searchBySummary } = await import("../lib/api");
                const result = await searchBySummary(searchSummary, 20);

                if (result.matches && result.matches.length > 0) {
                    const jobIds = result.matches.map(m => m.job.id).join(",");
                    router.push(`/jobs?mode=smart&summary=${encodeURIComponent(searchSummary)}&match_ids=${jobIds}`);
                } else {
                    alert("No matching jobs found. Try a different description.");
                    setLoading(false);
                }
            } else {
                // Quick keyword search - REDIRECT with all filters
                const params = new URLSearchParams();
                if (keywords.length > 0) params.append("keywords", keywords.join(","));
                if (locations.length > 0) params.append("location", locations.join(","));
                if (employmentType) params.append("employment_type", employmentType);

                router.push(`/jobs?${params.toString()}`);
            }
        } catch (error) {
            alert("Search failed: " + error.message);
            setLoading(false);
        }
    };

    return (
        <section className="relative py-20 text-center overflow-hidden">
            {/* Soft background glow */}
            <div className="absolute inset-0 -z-10">
                <div className="absolute top-24 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-cyan-400/10 blur-[120px]" />
                <div className="absolute top-40 left-1/3 w-[300px] h-[300px] bg-purple-500/10 blur-[120px]" />
            </div>

            <div className="container mx-auto px-4 relative">
                <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight">
                    Find Your Dream Job{" "}
                    <span className="bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
                        Anywhere
                    </span>
                </h1>
                <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto">
                    Unlock global opportunities powered by AI-driven matching. Your skills, matched intelligently.
                </p>

                {/* Search Tabs */}
                <div className="relative max-w-4xl mx-auto bg-slate-800/50 backdrop-blur-md rounded-2xl shadow-2xl overflow-hidden border border-white/10 p-8">
                    {/* Tab switcher */}
                    <div className="flex gap-4 mb-6">
                        <button
                            onClick={() => setSearchMode("resume")}
                            className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${searchMode === "resume"
                                ? "bg-gradient-to-r from-cyan-500 to-purple-600 text-white"
                                : "bg-slate-700/50 text-slate-300 hover:bg-slate-700"
                                }`}
                        >
                            ⚡ Smart Match (Recommended)
                        </button>
                        <button
                            onClick={() => setSearchMode("quick")}
                            className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${searchMode === "quick"
                                ? "bg-gradient-to-r from-cyan-500 to-purple-600 text-white"
                                : "bg-slate-700/50 text-slate-300 hover:bg-slate-700"
                                }`}
                        >
                            🔍 Quick Search
                        </button>
                    </div>

                    {/* Smart Match Tab */}
                    {searchMode === "resume" && (
                        <form onSubmit={handleSmartSearch} className="space-y-6">
                            {/* Resume Upload */}
                            <div className="relative">
                                <input
                                    type="file"
                                    accept=".pdf"
                                    onChange={handleResumeUpload}
                                    className="hidden"
                                    id="resume-upload"
                                    disabled={parsing}
                                />
                                <label
                                    htmlFor="resume-upload"
                                    className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl py-8 px-4 cursor-pointer transition-all ${resumeFile
                                        ? "border-green-500/50 bg-green-500/10"
                                        : "border-slate-600 hover:border-cyan-500 hover:bg-slate-700/30"
                                        } ${parsing ? "opacity-50 cursor-not-allowed" : ""}`}
                                >
                                    <svg className="w-12 h-12 text-cyan-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                    </svg>
                                    <span className="text-white font-medium">
                                        {parsing ? "Parsing Resume..." : resumeFile ? `✓ ${resumeFile.name}` : "Upload Your Resume (PDF)"}
                                    </span>
                                    <span className="text-slate-400 text-sm mt-1">
                                        {parsing ? "Please wait while we analyze your resume" : "Click to change file"}
                                    </span>
                                </label>
                            </div>

                            {/* Show parsed summary */}
                            {parsedSummary && (
                                <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-4">
                                    <div className="flex items-start gap-3">
                                        <span className="text-2xl">💡</span>
                                        <div className="flex-1">
                                            <h4 className="text-white font-semibold mb-1">Resume Parsed!</h4>
                                            <p className="text-slate-300 text-sm">{parsedSummary}</p>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Why upload your resume? */}
                            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-4">
                                <div className="flex items-start gap-3">
                                    <span className="text-2xl">💡</span>
                                    <div>
                                        <h4 className="text-white font-semibold mb-1">Why upload your resume?</h4>
                                        <p className="text-slate-300 text-sm">
                                            Our AI analyzes your full experience and skills to match you with jobs that truly fit your profile—not just keyword matches.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* OR divider */}
                            <div className="relative">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-slate-600"></div>
                                </div>
                                <div className="relative flex justify-center text-sm">
                                    <span className="px-4 bg-slate-800/50 text-slate-400">OR</span>
                                </div>
                            </div>

                            {/* Describe Yourself Text */}
                            <div>
                                <label className="block text-left text-slate-300 font-medium mb-2">
                                    Describe Yourself (100 words)
                                </label>
                                <textarea
                                    value={summary}
                                    onChange={(e) => setSummary(e.target.value)}
                                    placeholder="Example: I'm a Senior Data Scientist with 5 years of experience in ML pipelines, Python, and NLP. Expert in building production AI systems for healthcare. Looking for remote roles at innovative AI companies where I can apply deep learning to solve real-world problems..."
                                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none"
                                    rows="5"
                                    disabled={parsing}
                                />
                                <p className="text-right text-sm mt-2">
                                    <span className={wordCount >= 100 ? "text-green-400" : "text-slate-400"}>
                                        {wordCount}/100 words
                                    </span>
                                    <span className="text-slate-500 ml-2">• Better matches with more details</span>
                                </p>
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading || parsing || (!resumeFile && !summary.trim())}
                                className="w-full py-4 px-6 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none"
                            >
                                {loading ? "Searching..." : parsing ? "Parsing Resume..." : "🎯 Find Smart Matches"}
                            </button>
                        </form>
                    )}

                    {/* Quick Search Tab - REPLICATED FILTERS IN ONE ROW */}
                    {searchMode === "quick" && (
                        <form onSubmit={handleSmartSearch} className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="text-left">
                                    <label className="block text-slate-300 text-sm font-medium mb-2">
                                        Job Role / Skill
                                    </label>
                                    <Autocomplete
                                        placeholder="e.g., React, Java"
                                        apiEndpoint="http://localhost:8000/api/autocomplete/job-titles"
                                        selectedValues={keywords}
                                        onChange={setKeywords}
                                    />
                                </div>
                                <div className="text-left">
                                    <label className="block text-slate-300 text-sm font-medium mb-2">
                                        Locations
                                    </label>
                                    <Autocomplete
                                        placeholder="e.g., Berlin, Remote"
                                        apiEndpoint="http://localhost:8000/api/autocomplete/locations"
                                        selectedValues={locations}
                                        onChange={setLocations}
                                    />
                                </div>
                                <div className="text-left">
                                    <label className="block text-slate-300 text-sm font-medium mb-2">
                                        Employment Type
                                    </label>
                                    <select
                                        value={employmentType}
                                        onChange={(e) => setEmploymentType(e.target.value)}
                                        className="w-full h-[42px] px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
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
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-4 px-6 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? "Searching..." : "🔍 Search Jobs"}
                            </button>
                        </form>
                    )}
                </div>
            </div>

            {/* Stats section */}
            <div className="container mx-auto px-4 mt-20">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
                    <div>
                        <div className="text-4xl font-bold text-white mb-2">10K+</div>
                        <div className="text-slate-400">Active Jobs</div>
                    </div>
                    <div>
                        <div className="text-4xl font-bold text-white mb-2">5K+</div>
                        <div className="text-slate-400">Companies</div>
                    </div>
                    <div>
                        <div className="text-4xl font-bold text-white mb-2">50+</div>
                        <div className="text-slate-400">Countries</div>
                    </div>
                    <div>
                        <div className="text-4xl font-bold text-white mb-2">100K+</div>
                        <div className="text-slate-400">Job Seekers</div>
                    </div>
                </div>
            </div>
        </section>
    );
}
