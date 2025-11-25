const DOCUMENT_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/xml",
    "text/xml",
    "text/html",
    "text/markdown",
    "text/x-markdown",
    "text/mdx",
    "text/x-mdx",
    "text/plain",
    "application/epub+zip",
    "text/csv",
    "application/csv",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/tiff",
    "image/bmp",
] as const;

const DOCUMENT_EXTENSIONS = [
    "pdf",
    "docx",
    "pptx",
    "xlsx",
    "xml",
    "html",
    "md",
    "mdx",
    "asciidoc",
    "adoc",
    "csv",
    "txt",
    "epub",
    "jpeg",
    "jpg",
    "png",
    "tiff",
    "tif",
    "bmp",
] as const;

const DOCUMENT_ACCEPTS = [
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".xml",
    ".html",
    ".md",
    ".mdx",
    ".asciidoc",
    ".adoc",
    ".csv",
    ".txt",
    ".epub",
    ".jpeg",
    ".jpg",
    ".png",
    ".tiff",
    ".tif",
    ".bmp",
] as const;

const DOCUMENT_DISPLAY_NAMES = [
    "PDF",
    "DOCX",
    "PPTX",
    "XLSX",
    "XML",
    "HTML",
    "Markdown (MD, MDX)",
    "AsciiDoc (ADOC)",
    "CSV",
    "Plain text (TXT)",
    "EPUB",
    "Images (JPEG, PNG, TIFF, BMP)"
] as const;

const documentMimeTypeSet = new Set<string>(DOCUMENT_MIME_TYPES);
const documentExtensionSet = new Set<string>(DOCUMENT_EXTENSIONS);

export const allowedDocumentMimeTypes = [...DOCUMENT_MIME_TYPES];
export const allowedDocumentExtensions = [...DOCUMENT_EXTENSIONS];
export const allowedDocumentAccepts = [...DOCUMENT_ACCEPTS];
export const allowedDocumentDisplayNames = [...DOCUMENT_DISPLAY_NAMES];

export const isAllowedDocumentType = (filename: string, mimeType?: string): boolean => {
    const normalizedMimeType = (mimeType ?? "").toLowerCase();
    if (normalizedMimeType && documentMimeTypeSet.has(normalizedMimeType)) {
        return true;
    }

    const extension = filename?.split(".").pop()?.toLowerCase();
    if (!extension) {
        return false;
    }

    return documentExtensionSet.has(extension);
};
