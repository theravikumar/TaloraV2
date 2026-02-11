// import { Briefcase } from "lucide-react"

export default function Footer() {
  return (
    <footer className="relative mt-20">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0b1220] via-[#0e1729] to-[#020617]" />

      <div className="relative z-10 px-6 md:px-12 lg:px-20 py-16">
        {/* Top section */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 text-white text-lg font-semibold mb-4">
              <span className="bg-gradient-to-r from-cyan-400 to-purple-500 p-2 rounded-lg">
                {/* <Briefcase size={18} /> */}
              </span>
              Telora
            </div>
            <p className="text-sm text-slate-400 leading-relaxed max-w-sm">
              Your gateway to global career opportunities. Discover jobs from
              top companies worldwide.
            </p>
          </div>

          {/* Job Seekers */}
          <div>
            <h4 className="text-white font-semibold mb-4">
              For Job Seekers
            </h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li className="hover:text-white cursor-pointer">Browse Jobs</li>
              <li className="hover:text-white cursor-pointer">Career Advice</li>
              <li className="hover:text-white cursor-pointer">Resume Builder</li>
              <li className="hover:text-white cursor-pointer">Salary Guide</li>
            </ul>
          </div>

          {/* Employers */}
          <div>
            <h4 className="text-white font-semibold mb-4">
              For Employers
            </h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li className="hover:text-white cursor-pointer">Post a Job</li>
              <li className="hover:text-white cursor-pointer">Browse Candidates</li>
              <li className="hover:text-white cursor-pointer">Pricing</li>
              <li className="hover:text-white cursor-pointer">Employer Solutions</li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-white font-semibold mb-4">
              Company
            </h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li className="hover:text-white cursor-pointer">About Us</li>
              <li className="hover:text-white cursor-pointer">Contact</li>
              <li className="hover:text-white cursor-pointer">Privacy Policy</li>
              <li className="hover:text-white cursor-pointer">Terms of Service</li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="mt-12 border-t border-white/10" />

        {/* Bottom bar */}
        <div className="mt-6 text-center text-sm text-slate-500">
          © {new Date().getFullYear()} Telora. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
