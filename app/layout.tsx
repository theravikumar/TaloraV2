import './globals.css'
import Header from '../components/Header'
import Footer from '../components/Footer'
import { AuthProvider } from '../context/AuthContext'

export const metadata = {
	title: 'Telora | Find Your Dream Job Anywhere',
	description: 'Global job opportunities for professionals worldwide',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
	return (
		<html lang="en">
			<body>
				<AuthProvider>
					<Header />
					<main>{children}</main>
					<Footer />
				</AuthProvider>
			</body>
		</html>
	)
}