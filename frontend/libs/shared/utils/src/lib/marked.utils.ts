import { marked } from 'marked';
import { newUid } from "./uuid.util";

export const initializeMarkdown = () => {
    const renderer = new marked.Renderer();

    renderer.table = (header, body) => {
        return `<table class="table table-xs">${header}${body}</table>`;
    };

    const toggleModal = (modalId: string) => {
        const modal: any = document.getElementById(modalId);
        if (modal) {
            modal.showModal();
        }
    };

    document.addEventListener('click', (event: any) => {
        if (event?.target?.matches('.image-modal-trigger')) {
            const modalId = event.target.getAttribute('data-modal-id');
            toggleModal(modalId);
        }
    });

    renderer.image = (href, title, text) => {
        const imageId = newUid();
        return `
        <div class="py-2 mb-1">
            <img src="${href}" alt="${text}" title="${title}" class="cursor-pointer w-full image-modal-trigger" data-modal-id="${imageId}"/>
        </div>
        <dialog id="${imageId}" className="modal" style="width:80%;">
            <div className="modal-box w-full">
            <form method="dialog">
            <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
          </form>
            <img src="${href}" alt="${text}" class="w-full min-w-96"/>
            </div>
        </dialog>
           `;
    };

    marked.setOptions({
        renderer: renderer
    });
}
