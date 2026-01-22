import { iconCheck, iconCopy } from "@sit-onyx/icons";
import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import diff from "highlight.js/lib/languages/diff";
import ini from "highlight.js/lib/languages/ini";
import javascript from "highlight.js/lib/languages/javascript";
import json from "highlight.js/lib/languages/json";
import sql from "highlight.js/lib/languages/sql";
import typescript from "highlight.js/lib/languages/typescript";
import xml from "highlight.js/lib/languages/xml";
import yaml from "highlight.js/lib/languages/yaml";
import { marked } from 'marked';
import { COPY_FEEDBACK_DURATION_MS, copyToClipboard } from "./clipboard.utils";
import { newUid } from "./uuid.util";

const escapeHtml = (value: string): string =>
    value
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/`/g, "&#96;");

const terraformLanguage = (hljsApi: typeof hljs) => ({
    name: "Terraform",
    aliases: ["hcl", "tf", "terraform"],
    keywords: {
        keyword: "terraform provider resource data module variable output locals",
        literal: "true false null",
    },
    contains: [
        hljsApi.HASH_COMMENT_MODE,
        hljsApi.C_LINE_COMMENT_MODE,
        hljsApi.C_BLOCK_COMMENT_MODE,
        hljsApi.APOS_STRING_MODE,
        hljsApi.QUOTE_STRING_MODE,
        {
            className: "number",
            begin: /\b\d+(\.\d+)?\b/,
            relevance: 0,
        },
        {
            className: "attr",
            begin: /^[ \t]*[A-Za-z_][\w-]*(?=\s*=)/m,
            relevance: 0,
        },
    ],
});

hljs.registerLanguage("bash", bash);
hljs.registerLanguage("diff", diff);
hljs.registerLanguage("ini", ini);
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("json", json);
hljs.registerLanguage("sql", sql);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("yaml", yaml);
hljs.registerLanguage("terraform", terraformLanguage);

const normalizeLanguage = (language: string | undefined): string | undefined => {
    if (!language) return undefined;
    const normalized = language.trim().toLowerCase();
    const aliases: Record<string, string> = {
        js: "javascript",
        ts: "typescript",
        sh: "bash",
        shell: "bash",
        zsh: "bash",
        yml: "yaml",
        html: "xml",
    };
    return aliases[normalized] ?? normalized;
};

const highlightCodeBlock = (code: string, language: string | undefined): string => {
    try {
        const normalized = normalizeLanguage(language);
        if (normalized && hljs.getLanguage(normalized)) {
            return hljs.highlight(code, { language: normalized, ignoreIllegals: true }).value;
        }
        return hljs.highlightAuto(code).value;
    } catch (_err) {
        return escapeHtml(code);
    }
};

let isMarkdownClickHandlerRegistered = false;

const showDialog = (modalId: string) => {
    const modal = document.getElementById(modalId) as HTMLDialogElement | null;
    if (modal?.showModal) {
        modal.showModal();
    }
};

const onMarkdownDocumentClick = async (event: MouseEvent) => {
    const target = event.target instanceof Element ? event.target : null;
    if (!target) return;

    const imageTarget = target.closest('.image-modal-trigger') as HTMLElement | null;
    if (imageTarget) {
        const modalId = imageTarget.getAttribute('data-modal-id');
        if (modalId) showDialog(modalId);
        return;
    }

    const copyButton = target.closest('.chat-code-copy-button') as HTMLButtonElement | null;
    if (!copyButton) return;

    const codeBlock = copyButton.closest('.chat-code-block');
    const codeElement = codeBlock?.querySelector('pre > code');
    const codeText = codeElement?.textContent ?? '';

    if (!(await copyToClipboard(codeText))) return;

    const existingTimeout = copyButton.dataset["copyTimeoutId"];
    if (existingTimeout) {
        clearTimeout(Number(existingTimeout));
    }

    copyButton.classList.add('is-copied');
    copyButton.dataset["copyTimeoutId"] = String(
        window.setTimeout(() => {
            copyButton.classList.remove('is-copied');
            delete copyButton.dataset["copyTimeoutId"];
        }, COPY_FEEDBACK_DURATION_MS),
    );
};

export const initializeMarkdown = () => {
    const renderer = new marked.Renderer();

    // Preserve default behavior while injecting our own CSS classes.
    const anyRenderer = renderer as unknown as Record<string, any>;
    const originalTable = anyRenderer['table']?.bind(renderer) as ((...args: any[]) => string) | undefined;
    anyRenderer['table'] = (...args: any[]): string => {
        // Marked >= v16 provides a token argument; older versions pass (header, body)
        if (args.length === 1 && typeof args[0] === 'object') {
            const html = originalTable ? originalTable(args[0]) : '';
            return html
                ? html.replace('<table>', '<table class="table table-xs">')
                : '<table class="table table-xs"></table>';
        }
        const [header, body] = args as [string, string];
        return `<table class="table table-xs">${header ?? ''}${body ?? ''}</table>`;
    };

    renderer.code = (code, infostring) => {
        const language = infostring?.match(/^\s*([\w-]+)/)?.[1];
        const normalizedLanguage = normalizeLanguage(language);
        const highlighted = highlightCodeBlock(code, language);
        const languageClass = normalizedLanguage ? ` language-${escapeHtml(normalizedLanguage)}` : "";
        const languageLabel = normalizedLanguage ? escapeHtml(normalizedLanguage) : "";

        return `<div class="chat-code-block"><div class="chat-code-block__header"><div class="chat-code-block__header-left"><span class="chat-code-block__dots" aria-hidden="true"><span></span><span></span><span></span></span><span class="chat-code-block__lang" aria-hidden="true" data-language="${languageLabel}"></span></div><button type="button" class="chat-code-copy-button" title="Copy to clipboard" aria-label="Copy code to clipboard" data-copied="Copied!"><span class="chat-copy-icon chat-copy-icon--copy" aria-hidden="true">${iconCopy}</span><span class="chat-copy-icon chat-copy-icon--check" aria-hidden="true">${iconCheck}</span></button></div><pre><code class="hljs${languageClass}">${highlighted}</code></pre></div>`;
    };

    if (!isMarkdownClickHandlerRegistered && typeof document !== "undefined") {
        document.addEventListener('click', onMarkdownDocumentClick);
        isMarkdownClickHandlerRegistered = true;
    }

    anyRenderer['image'] = (...args: any[]): string => {
        let href: string | undefined = '';
        let title: string | null = null;
        let text: string | undefined = '';
        // token form
        if (args.length === 1 && typeof args[0] === 'object') {
            const token = args[0] as { href?: string; title?: string | null; text?: string };
            href = token.href;
            title = token.title ?? null;
            text = token.text;
        } else {
            // legacy form (href, title, text)
            [href, title, text] = args as [string, string | null, string];
        }
        const imageId = newUid();
        const titleAttr = title ? ` title="${title}"` : '';
        const src = href ?? '';
        const alt = text ?? '';
        return `
        <div class="py-2 mb-1">
            <img src="${src}" alt="${alt}"${titleAttr} class="cursor-pointer w-full image-modal-trigger" data-modal-id="${imageId}"/>
        </div>
        <dialog id="${imageId}" class="modal" style="width:80%;">
            <div class="modal-box w-full">
            <form method="dialog">
            <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
          </form>
            <img src="${src}" alt="${alt}" class="w-full min-w-96"/>
            </div>
        </dialog>
           `;
    };

    marked.setOptions({
        renderer: renderer,
        gfm: true,
        breaks: true,
    });
}
