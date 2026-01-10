# Phase 6: Frontend (React TypeScript)

**Status:** Pending

## Overview

Build the frontend UI for managing profiles, searches, and viewing detected signals.

## Tech Stack

- React 19
- TypeScript
- TanStack Router (code-based routing)
- TanStack Query (data fetching)
- TailwindCSS (styling)

## Planned Pages

### Profile Management

**File:** `webapp/src/pages/profiles/index.tsx`

- List of monitored profiles with status indicators
- Add profile form (URL, type, display name)
- Edit profile settings
- Toggle active/inactive
- Manual crawl trigger button

### Search Management

**File:** `webapp/src/pages/searches/index.tsx`

- List of saved searches
- Add search form (term, type: keyword/hashtag)
- Edit search settings
- Toggle active/inactive
- Manual crawl trigger button

### Signal Feed

**File:** `webapp/src/pages/signals/index.tsx`

- List of detected signals with filters
- Filter by: event type, timing, relevance, date range
- Signal cards showing:
  - Event type badge
  - Summary
  - Companies/people mentioned
  - Relevance score
  - Link to original post
- Pagination

### Dashboard

**File:** `webapp/src/pages/dashboard/index.tsx`

- Overview statistics cards
- Recent signals preview
- Quick actions (add profile, add search)
- Activity timeline

## API Integration

**Files to create:**

```
webapp/src/integrations/api/
├── profiles.ts    # Profile CRUD operations
├── searches.ts    # Search CRUD operations
├── signals.ts     # Signal listing and filtering
└── dashboard.ts   # Dashboard stats
```

**Example:**

```typescript
// webapp/src/integrations/api/profiles.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export function useProfiles() {
  return useQuery({
    queryKey: ["profiles"],
    queryFn: () => fetch("/api/profiles").then(r => r.json()),
  });
}

export function useCreateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProfileCreate) =>
      fetch("/api/profiles", {
        method: "POST",
        body: JSON.stringify(data),
      }).then(r => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profiles"] });
    },
  });
}
```

## Routes

```typescript
// webapp/src/routes.ts
const profilesRoute = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: "/profiles",
  component: ProfilesPage,
});

const searchesRoute = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: "/searches",
  component: SearchesPage,
});

const signalsRoute = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: "/signals",
  component: SignalsPage,
});

const dashboardRoute = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: "/dashboard",
  component: DashboardPage,
});
```

## Tasks

- [ ] Create profile management page
- [ ] Create search management page
- [ ] Create signal feed page with filters
- [ ] Create dashboard page
- [ ] Set up API integration hooks
- [ ] Add TanStack Router routes
- [ ] Style with TailwindCSS
- [ ] Add loading and error states
- [ ] Add form validation
- [ ] Add toast notifications

## Component Library

Consider using a component library compatible with TailwindCSS:
- shadcn/ui (recommended - copy-paste components)
- Headless UI
- Radix UI primitives
