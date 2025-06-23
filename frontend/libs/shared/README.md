# Shared Libraries

This directory contains reusable components, utilities, and configurations used across the frontend application.

## Contents

### Configuration & Theming
- **settings.ts** - Application settings with environment variable support
- **theme.store.ts** - Pinia store for theme management
- **global.css** - Global styles and Tailwind configuration

### UI Components
- **NavigationContainer** - Top navigation bar with theme toggle
- **LogoContainer** - Container for displaying logos
- **SideBarContainer** - Sidebar layout component with header and scrollable content
- **ThemeToggle** - Dark/light mode toggle button

### Utilities
- Date formatting
- UUID generation
- File size formatting
- Markdown rendering
- Empty checks

## Environment Configuration

Settings can be customized using environment variables in a `.env` file:

```
VITE_BOT_NAME=My Custom Bot
VITE_UI_LOGO_PATH=/assets/custom-logo.svg
VITE_UI_THEME_DEFAULT=dark
VITE_UI_THEME_OPTIONS=light,dark
```

## Usage Example

```vue
<script setup>
import { NavigationContainer, SideBarContainer } from '@/libs/shared/ui';
import { settings } from '@/libs/shared/settings';
</script>

<template>
  <NavigationContainer>
    <!-- Navigation content -->
  </NavigationContainer>
  
  <SideBarContainer header="Documents" count="5">
    <!-- Sidebar content -->
  </SideBarContainer>
</template>
```
