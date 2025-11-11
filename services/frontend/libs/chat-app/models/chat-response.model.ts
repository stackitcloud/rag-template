export interface ChatResponseModel {
    answer: string;
    finish_reason: string;
    citations: InformationPiece[];
}

export interface KeyValuePair {
    key: string;
    value: string;
}

export interface InformationPiece {
    page_content: string;
    metadata: KeyValuePair[];
}
