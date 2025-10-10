import { marked } from 'marked';
import { newUid } from "./uuid.util";

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

    const toggleModal = (modalId: string) => {
        const modal: any = document.getElementById(modalId);
        if (modal) {
            modal.showModal();
        }
    };

    document.addEventListener('click', (event: MouseEvent) => {
        const target = event.target as HTMLElement | null;
        if (target && target.matches('.image-modal-trigger')) {
            const modalId = target.getAttribute('data-modal-id');
            if (modalId) toggleModal(modalId);
        }
    });

    const originalImage = anyRenderer['image']?.bind(renderer) as ((...args: any[]) => string) | undefined;
    anyRenderer['image'] = (...args: any[]): string => {
        let href = '' as string | undefined;
        let title = null as string | null;
        let text = '' as string | undefined;
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
        renderer: renderer
    });
}
