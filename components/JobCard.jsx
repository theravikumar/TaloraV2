export default function JobCard({ job }) {
  // Truncate description if available
  const description = job.job_description
    ? (job.job_description.length > 150 ? job.job_description.substring(0, 150) + "..." : job.job_description)
    : null;

  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl hover:bg-white/20 transition duration-200 cursor-pointer h-full flex flex-col">
      <div className="flex justify-between items-start mb-2">
        <div>
          {job.domain && (
            <span className="inline-block text-xs bg-cyan-500/30 text-cyan-300 px-3 py-1 rounded-full mb-2">
              {job.domain}
            </span>
          )}
          <h3 className="font-semibold text-white text-lg">{job.job_title || job.title}</h3>
        </div>
      </div>

      <p className="text-slate-300 text-sm mb-3 font-medium">{job.company_name || job.company}</p>

      <div className="flex items-center gap-2 text-slate-400 text-sm mb-4">
        <span>📍</span>
        <span>{job.location}</span>
      </div>

      {description && (
        <p className="text-slate-400 text-sm mb-4 flex-grow">
          {description}
        </p>
      )}

      {job.requirements_count && (
        <div className="flex items-center gap-2 text-slate-400 text-sm mb-4">
          <span>📋</span>
          <span>{job.requirements_count} requirements</span>
        </div>
      )}

      <div className="mt-auto pt-4 border-t border-white/10 flex gap-3 items-center">
        {job.job_url && (
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              window.open(job.job_url, '_blank', 'noopener,noreferrer');
            }}
            className="flex-1 text-center py-2 px-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-semibold transition z-10"
          >
            Apply Now ↗
          </button>
        )}
        <div className="flex items-center gap-2 text-slate-500 text-xs ml-auto">
          <span>Posted: {job.posted_date || "Recently"}</span>
        </div>
      </div>
    </div>
  );
}