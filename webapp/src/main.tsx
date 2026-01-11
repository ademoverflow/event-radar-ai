import {
	createRootRoute,
	createRoute,
	createRouter,
	RouterProvider,
} from "@tanstack/react-router";
import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import { Toaster } from "sonner";
import * as TanStackQueryProvider from "./integrations/tanstack-query/root-provider.tsx";

import "./styles.css";

import { Layout } from "./components/Layout.tsx";
import { ProtectedRoute } from "./components/ProtectedRoute.tsx";
import About from "./pages/About.tsx";
import { Dashboard } from "./pages/Dashboard.tsx";
import { LoginPage } from "./pages/Login.tsx";
import { ProfilesPage } from "./pages/Profiles.tsx";
import { SearchesPage } from "./pages/Searches.tsx";
import { SignalsPage } from "./pages/Signals.tsx";

const rootRoute = createRootRoute({
	component: Layout,
});

const loginRoute = createRoute({
	getParentRoute: () => rootRoute,
	path: "/login",
	component: LoginPage,
});

const protectedRoute = createRoute({
	getParentRoute: () => rootRoute,
	id: "protected",
	component: ProtectedRoute,
});

const indexRoute = createRoute({
	getParentRoute: () => protectedRoute,
	path: "/",
	component: Dashboard,
});

const aboutRoute = createRoute({
	getParentRoute: () => protectedRoute,
	path: "/about",
	component: About,
});

const profilesRoute = createRoute({
	getParentRoute: () => protectedRoute,
	path: "/profiles",
	component: ProfilesPage,
});

const searchesRoute = createRoute({
	getParentRoute: () => protectedRoute,
	path: "/searches",
	component: SearchesPage,
});

const signalsRoute = createRoute({
	getParentRoute: () => protectedRoute,
	path: "/signals",
	component: SignalsPage,
});

const routeTree = rootRoute.addChildren([
	loginRoute,
	protectedRoute.addChildren([
		indexRoute,
		aboutRoute,
		profilesRoute,
		searchesRoute,
		signalsRoute,
	]),
]);

const TanStackQueryProviderContext = TanStackQueryProvider.getContext();
const router = createRouter({
	routeTree,
	context: {
		...TanStackQueryProviderContext,
	},
	defaultPreload: "intent",
	scrollRestoration: true,
	defaultStructuralSharing: true,
	defaultPreloadStaleTime: 0,
});

declare module "@tanstack/react-router" {
	interface Register {
		router: typeof router;
	}
}

const rootElement = document.getElementById("app");
if (rootElement && !rootElement.innerHTML) {
	const root = ReactDOM.createRoot(rootElement);
	root.render(
		<StrictMode>
			<TanStackQueryProvider.Provider {...TanStackQueryProviderContext}>
				<Toaster position="top-right" richColors closeButton />
				<RouterProvider router={router} />
			</TanStackQueryProvider.Provider>
		</StrictMode>,
	);
}
