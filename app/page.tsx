import Hero from '@/components/Hero'
import Stats from '@/components/Stats'
import Categories from '@/components/Categories'
import FeaturedJobs from '@/components/FeaturedJobs'

export default function Home() {
	return (
		<>
			<Hero />
			<Stats />
			<Categories />
			<FeaturedJobs />
		</>
	)
}