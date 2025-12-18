# RAG - Frontend

## Table of Contents

 - [Introduction](#introduction)
 - [How to run it](#how-to-run-it)
    - [Prepare](#prepare)
    - [Serve](#serve)
    - [Test](#test)
 - [Dependencies](#dependencies)
 - [Folder Structure](#folder-structure)
 - [Theming](#theme)
 - [Environment variables](#env)

## Introduction

This repository contains the frontend applications built using Vue 3 within an NX monorepo architecture.
Seperated in 2 appilcations `chat-app` and `admin-app`

## How to run it

### Prepare

- Node : Version >22.12.0
- Fomatter : Vue-Official & Basic Ts formatter

Install all dependencies for both apps
```shell
npm install
```

### Serve

To serve one of the application, you can run this command at the root of your workspace.

```shell
// runs the chat app on http://localhost:4200
npx nx serve chat-app:serve

// runs the admin app on http://localhost:4300
npx nx serve admin-app:serve
```

### Live updates with Tilt

When running via Tilt, the frontend containers use Nginx and Tilt syncs the built assets (Vite `dist/`) directly into `/usr/share/nginx/html` inside the pod. For live updates while editing code, run a build in watch mode and Tilt will sync changes automatically:

```bash
# From services/frontend
npx nx run admin-app:build --watch
npx nx run chat-app:build --watch
```

### Test

To run unit test, you can run this command at the root of your workspace.

```shell
npm run test
```

## Dependencies

- **@vueuse/core**: Utility functions
- **pinia**: State management
- **vue-i18n**: Internationalization
- **vue-router**: Routing
- **daisyUI**: Tailwind based CSS framework
- **@sit-onyx/icons**: Icon set (used via `OnyxIcon`)
- **cypress**: End-to-end testing framework
- **vite**: Local development server

## Folder Structure
[Simple Nx Monorepo Concept](https://nx.dev/concepts/more-concepts/monorepo-nx-enterprise#scope-where-a-library-lives-who-owns-it)


- `apps/`: Base of the apps chat & administration
- `libs/`: main logic at feature-* folders, shared dumb ui components and utils. See [Library Types in Nx](https://nx.dev/concepts/more-concepts/library-types)
- `i18n`: For localization, each app has its own folder: `i18n/chat` and `i18n/admin`

## Theming

To change the theme, edit `libs/ui-styles/src/tailwind.css` (Tailwind v4 + daisyUI v5 via CSS `@plugin` blocks).

## Environment variables

### Application URLs
- VITE_API_URL = The URL for the backend
- VITE_ADMIN_URL = The URL where the admin frontend is running
- VITE_CHAT_URL = The URL where the chat frontend is running

### UI Customization
- VITE_BOT_NAME = The AI assistant's display name (default: "Knowledge Agent")
- VITE_UI_LOGO_PATH = Common path to the main navigation logo (fallback for both light/dark, default: "/assets/navigation-logo.svg")
- VITE_UI_LOGO_PATH_LIGHT = Path to the logo used in light mode (fallbacks to VITE_UI_LOGO_PATH, default: "/assets/navigation-logo-light.svg")
- VITE_UI_LOGO_PATH_DARK = Path to the logo used in dark mode (fallbacks to VITE_UI_LOGO_PATH, default: "/assets/navigation-logo-dark.svg")
- VITE_UI_THEME_DEFAULT = Default theme when user first visits (default: "dark")
- VITE_UI_THEME_OPTIONS = Available theme options, comma-separated (default: "light,dark")

For detailed UI customization instructions, see [UI Customization Guide](../../docs/UI_Customization.md).

> Important:
>
> Vite `VITE_*` env vars are build-time by default. The provided Docker images (see `apps/chat-app/Dockerfile` and `apps/admin-app/Dockerfile`) use placeholder replacement at runtime via `env.sh`.
> To apply runtime env vars, copy the built files from `/app/frontend` to `/usr/share/nginx/html` and run `/app/env.sh` before nginx serves the files.
>
> This can be done with the following command:
>
> ```bash
> cp -r /app/frontend/. /usr/share/nginx/html
> /bin/sh /app/env.sh
> ```
>
> This is a workaround for the inability of Vite to use env-vars at runtime.
