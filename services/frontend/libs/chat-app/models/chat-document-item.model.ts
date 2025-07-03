import { ChatDocumentModel } from "./chat-document.model";

export interface ChatDocumentItemModel {
    title: string;
    text: string;
    index: number;
    anchorId: string;
    source: string;
}

export const mapToDocumentItem = (document: ChatDocumentModel): ChatDocumentItemModel => ({
    index: document.index,
    source: document.url,
    text: document.chunk,
    title: document.name,
    anchorId: document.messageId
});
