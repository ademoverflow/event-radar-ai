import {
	createRootRoute,
	createRoute,
	createRouter,
	RouterProvider,
} from "@tanstack/react-router";
import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import * as TanStackQueryProvider from "./integrations/tanstack-query/root-provider.tsx";

import "./styles.css";

import { Layout } from "./components/Layout.tsx";
import { ProtectedRoute } from "./components/ProtectedRoute.tsx";
import About from "./pages/About.tsx";
import { Dashboard } from "./pages/Dashboard.tsx";
import { LoginPage } from "./pages/Login.tsx";

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

const routeTree = rootRoute.addChildren([
	loginRoute,
	protectedRoute.addChildren([indexRoute, aboutRoute]),
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
				<RouterProvider router={router} />
			</TanStackQueryProvider.Provider>
		</StrictMode>,
	);
}
