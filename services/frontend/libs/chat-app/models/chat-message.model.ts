import {ChatRole} from "./chat-role.type";

export interface ChatMessageModel {
    id: string;
    text?: string;
    anchorIds?: number[];
    dateTime?: Date;
    role: ChatRole;
    hasError?: boolean;
    skipAPI?: boolean;
}