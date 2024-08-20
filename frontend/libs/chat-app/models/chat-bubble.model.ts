export interface ChatBubbleModel {
    id: string;
    text?: string;
    time?: string;
    avatarSrc: string;
    name: string;
    align: "left" | "right";
    backgroundColor: string;
    textColor: string;
    anchorIds: number[] | undefined;
}