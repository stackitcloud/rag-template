import { DocumentAPI } from "./document.api";
import { MockDocumentAPI } from "./document.api.mock";
import { settings } from "@shared/settings";

// Get the appropriate API implementation
export function getDocumentAPI() {
  // Check if we should use mock data
  // This could be controlled by:
  // 1. An environment variable (preferred)
  // 2. A setting in the settings.ts file
  // 3. Detecting if the backend is unreachable
  const useMockAPI =
    import.meta.env.VITE_USE_MOCK_API === "true" ||
    settings.features?.useMockData === true;

  return useMockAPI ? MockDocumentAPI : DocumentAPI;
}
