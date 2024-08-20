export interface ChatResponseModel {
    answer: string;
    finish_reason: string;
    citations: SourceDocument[];
}

export interface KeyValuePair {
    key: string;
    value: string;
}

export interface SourceDocument {
    content: string;
    metadata: KeyValuePair[];
}