export type DocumentStatus = "UPLOADING" | "PROCESSING" | "READY" | "ERROR";

export interface DocumentModel {
    name: string;
    status: DocumentStatus;
}
