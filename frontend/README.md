# rag - Frontend

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
- Node : Version >18.0.0
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
- **heroicons**: Hand-crafted SVG icons (by Tailwind CSS) 
- **cypress**: End-to-end testing framework
- **vite**: Local development server 

## Folder Structure
[Simple Nx Monorepo Concept](https://nx.dev/concepts/more-concepts/monorepo-nx-enterprise#scope-where-a-library-lives-who-owns-it)


- `apps/`: Base of the apps chat & administration
- `libs/`: main logic at feature-* folders, shared dumb ui components and utils. See [Library Types in Nx](https://nx.dev/concepts/more-concepts/library-types)
- `i18n`: For localization, each app has its own folder: `i18n/chat` and `i18n/admin`

## Theming

To change the theme, open the `tailwind.config.js` file and refer to the available color configuration options for DaisyUI at https://daisyui.com/docs/colors/

## Environment variables

### Application URLs
- VITE_API_URL = The URL for the backend
- VITE_ADMIN_URL = The URL where the admin frontend is running
- VITE_CHAT_URL = The URL where the chat frontend is running

### UI Customization
- VITE_BOT_NAME = The AI assistant's display name (default: "Knowledge Agent")
- VITE_UI_LOGO_PATH = Path to the main navigation logo (default: "/assets/navigation-logo.svg")
- VITE_UI_THEME_DEFAULT = Default theme when user first visits (default: "dark")
- VITE_UI_THEME_OPTIONS = Available theme options, comma-separated (default: "light,dark")

For detailed UI customization instructions, see [UI Customization Guide](../docs/UI_Customization.md).

> Important: 
>
> The environment variables are not used after the docker-image is build. 
> When using the `Dockerfile` to run the frontend you have to copy the build frontend  from `/app/frontend` to `/usr/share/nginx/html` and run the `/app/env.sh` script. 
>This can be done with the following command:
> ```bash
>cp -r /app/frontend/. /usr/share/nginx/html
>/bin/sh -c /app/env.sh
>```
>This is a workaround for the inability of *VITE* to use env-vars at runtime.
