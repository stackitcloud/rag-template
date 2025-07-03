import { newUid } from '@shared/utils';

export interface UploadedDocument {
    id: string;
    file: File;
    isCompleted: boolean;
    isProcessing: boolean;
    isFailed: boolean;
    progress?: number;
    total?: number;
}

export const mapToUploadDocument = (file: File): UploadedDocument => ({
    id: newUid(),
    file,
    isCompleted: false,
    isProcessing: false,
    isFailed: false
})