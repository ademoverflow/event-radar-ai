import { Outlet } from "@tanstack/react-router";
import { Navbar } from "./Navbar";

export function Layout() {
	return (
		<div className="min-h-screen bg-slate-50">
			<Navbar />
			<main className="max-w-7xl mx-auto px-6 py-8">
				<Outlet />
			</main>
		</div>
	);
}
