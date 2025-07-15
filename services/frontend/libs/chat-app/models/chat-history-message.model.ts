import { ChatRole } from "./chat-role.type";

export interface ChatHistoryMessage {
    role: ChatRole;
    message: string;
}