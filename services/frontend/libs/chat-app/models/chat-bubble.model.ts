export interface ChatBubbleModel {
    id: string;
    text?: string;
    rawText?: string;
    time?: string;
    avatarSrc: string;
    name: string;
    align: "left" | "right";
    backgroundColor: string;
    textColor: string;
    proseDark: "prose-dark" | "";
    anchorIds: number[] | undefined;
}
