import { ChatHistoryMessage } from "./chat-history-message.model";
import { ChatHistory } from "./chat-history.model";
import { ChatMessageModel } from "./chat-message.model";

export interface ChatRequestModel {
    session_id: string;
    message: string;
    history: ChatHistory;
}

export const mapToChatRequestModel = (session_id: string, message: string, historyList: ChatMessageModel[]): ChatRequestModel => ({
    session_id,
    message,
    history: {
        messages: historyList.filter(o => !o.hasError).map((o) => ({
            role: o.role,
            message: o.text
        } as ChatHistoryMessage))
    }
});