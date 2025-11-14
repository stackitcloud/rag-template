import { isAllowedDocumentType } from "./document-type.utils";

declare const describe: (name: string, fn: () => void) => void;
declare const it: (name: string, fn: () => void) => void;
declare const expect: (value: unknown) => { toBe: (expected: unknown) => void };

describe("isAllowedDocumentType", () => {
    it("allows matching MIME types", () => {
        expect(isAllowedDocumentType("report.pdf", "application/pdf")).toBe(true);
    });

    it("allows supported extensions when MIME is missing", () => {
        expect(isAllowedDocumentType("notes.MD", "")).toBe(true);
        expect(isAllowedDocumentType("diagram.PNG")).toBe(true);
        expect(isAllowedDocumentType("readme.adoc")).toBe(true);
    });

    it("rejects unsupported files", () => {
        expect(isAllowedDocumentType("archive.zip", "application/zip")).toBe(false);
    });

    it("allows plain text content type", () => {
        expect(isAllowedDocumentType("transcript.txt", "text/plain")).toBe(true);
    });
});
