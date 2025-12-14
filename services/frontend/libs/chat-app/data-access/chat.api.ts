import axios from 'axios';
import { ChatRequestModel } from "../models/chat-request.model";
import { ChatResponseModel } from "../models/chat-response.model";

const parseBooleanEnv = (value: unknown): boolean => String(value).trim().toLowerCase() === "true";
const isPlaceholderEnvValue = (value: unknown): boolean =>
  typeof value === "string" && /^VITE_[A-Z0-9_]+$/.test(value.trim());

const apiUrl = import.meta.env.VITE_API_URL;
axios.defaults.baseURL = !apiUrl || isPlaceholderEnvValue(apiUrl) ? "/api" : apiUrl;

const chatAuthEnabledEnv = import.meta.env.VITE_CHAT_AUTH_ENABLED;
const authUsername = import.meta.env.VITE_AUTH_USERNAME;
const authPassword = import.meta.env.VITE_AUTH_PASSWORD;
const hasExplicitAuthCredentials =
  !!authUsername &&
  !!authPassword &&
  !isPlaceholderEnvValue(authUsername) &&
  !isPlaceholderEnvValue(authPassword);

const chatAuthEnabled =
  chatAuthEnabledEnv === undefined || isPlaceholderEnvValue(chatAuthEnabledEnv)
    ? hasExplicitAuthCredentials
    : parseBooleanEnv(chatAuthEnabledEnv);

if (chatAuthEnabled && hasExplicitAuthCredentials) {
  axios.defaults.auth = {
    username: authUsername,
    password: authPassword,
  };
}

export class ChatAPI {
    static async callInference(request: ChatRequestModel): Promise<ChatResponseModel> {
        const response = await axios.post<ChatResponseModel>(`/chat/${request.session_id}`, request);
        return response.data;
    }
}
