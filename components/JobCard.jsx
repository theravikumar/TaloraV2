export default function JobCard({ job }) {
  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl hover:bg-white/20 transition duration-200 cursor-pointer h-full">
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
      <p className="text-slate-300 text-sm mb-3">{job.company_name || job.company}</p>
      <div className="flex items-center gap-2 text-slate-400 text-sm mb-3">
        <span>📍</span>
        <span>{job.location}</span>
      </div>
      {job.requirements_count && (
        <div className="flex items-center gap-2 text-slate-400 text-sm">
          <span>📋</span>
          <span>{job.requirements_count} requirements</span>
        </div>
      )}
    </div>
  );
}