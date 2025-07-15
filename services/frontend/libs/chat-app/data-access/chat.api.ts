import axios from 'axios';
import { ChatRequestModel } from "../models/chat-request.model";
import { ChatResponseModel } from "../models/chat-response.model";

axios.defaults.baseURL = import.meta.env.VITE_API_URL;
if (import.meta.env.VITE_CHAT_AUTH_ENABLED) {
  axios.defaults.auth = {
      username: import.meta.env.VITE_AUTH_USERNAME,
      password: import.meta.env.VITE_AUTH_PASSWORD
  };
}

export class ChatAPI {
    static async callInference(request: ChatRequestModel): Promise<ChatResponseModel> {
        const response = await axios.post<ChatResponseModel>(`/chat/${request.session_id}`, request);
        return response.data;
    }
}
