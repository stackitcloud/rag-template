import { ChatDocumentModel } from "./chat-document.model";

export interface ChatDocumentItemModel {
    title: string;
    text: string;
    index: number;
    anchorId: string;
    source: string;
}

export const mapToDocumentItem = (index: number, document: ChatDocumentModel): ChatDocumentItemModel => ({
    index,
    source: document.url,
    text: document.chunk,
    title: document.name,
    anchorId: document.messageId
});