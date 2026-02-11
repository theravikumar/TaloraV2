import categories from '@/data/categories'


export default function Categories() {
return (
<section className="py-20 px-10">
<h2 className="text-3xl font-bold text-center mb-2">Browse by Category</h2>
<p className="text-center text-slate-400 mb-10">Explore opportunities in your field</p>


<div className="grid md:grid-cols-3 gap-6">
{categories.map(cat => (
<div key={cat.title} className="bg-card-bg p-6 rounded-xl hover:bg-white/5 transition">
<h3 className="font-semibold">{cat.title}</h3>
<p className="text-slate-400 text-sm">{cat.count} jobs</p>
</div>
))}
</div>
</section>
)
}