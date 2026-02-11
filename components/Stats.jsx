const stats = [
{ value: '10K+', label: 'Active Jobs' },
{ value: '5K+', label: 'Companies' },
{ value: '50+', label: 'Countries' },
{ value: '100K+', label: 'Job Seekers' },
]


export default function Stats() {
return (
<section className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center py-10 border-y border-white/10">
{stats.map((item) => (
<div key={item.label}>
<p className="text-3xl font-bold">{item.value}</p>
<p className="text-slate-400">{item.label}</p>
</div>
))}
</section>
)
}