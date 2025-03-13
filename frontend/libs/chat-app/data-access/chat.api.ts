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
        async function* getIterableStream(
            body: ReadableStream<Uint8Array>
          ): AsyncIterable<string> {
            const reader = body.getReader()
            const decoder = new TextDecoder()
          
            while (true) {
              const { value, done } = await reader.read()
              if (done) {
                break
              }
              const decodedChunk = decoder.decode(value, { stream: true })
              yield decodedChunk
            }
          }
        const generateStream = async (): Promise<AsyncIterable<string>> => {
            const r = {history: request.history, message: request.message}
        const response = await fetch(
          import.meta.env.VITE_API_URL + `/chat/${request.session_id}`,
          {
            method: 'POST',
            body: JSON.stringify(r),
            headers: {
                'content-type': 'application/json',
                //'X-RapidAPI-Host': 'famous-quotes4.p.rapidapi.com',
            },
          }
        )
        if (response.status !== 200) throw new Error(response.status.toString())
        if (!response.body) throw new Error('Response body does not exist')
        return getIterableStream(response.body)
      }
      const stream = await generateStream()
      return stream
    }
}
