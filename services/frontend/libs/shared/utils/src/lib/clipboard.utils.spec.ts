
import { copyToClipboard } from './clipboard.utils';

describe('copyToClipboard', () => {
    const originalDocumentDescriptor = Object.getOwnPropertyDescriptor(globalThis, 'document');
    const originalNavigatorDescriptor = Object.getOwnPropertyDescriptor(globalThis, 'navigator');

    const setGlobal = <T>(key: string, value: T) => {
        Object.defineProperty(globalThis, key, {
            value,
            configurable: true,
            writable: true,
        });
    };

    const restoreGlobal = (key: string, descriptor: PropertyDescriptor | undefined) => {
        if (descriptor) {
            Object.defineProperty(globalThis, key, descriptor);
            return;
        }
        delete (globalThis as any)[key];
    };

    afterEach(() => {
        restoreGlobal('document', originalDocumentDescriptor);
        restoreGlobal('navigator', originalNavigatorDescriptor);
    });

    it('returns false for empty input', async () => {
        await expect(copyToClipboard('')).resolves.toBe(false);
    });

    it('prefers the execCommand fallback when it succeeds', async () => {
        const execCommand = vi.fn(() => true);

        setGlobal('document', {
            body: { appendChild: vi.fn(), removeChild: vi.fn() },
            activeElement: null,
            createElement: vi.fn(() => ({
                value: '',
                setAttribute: vi.fn(),
                style: {},
                focus: vi.fn(),
                select: vi.fn(),
                setSelectionRange: vi.fn(),
            })),
            getSelection: vi.fn(() => null),
            execCommand,
        });

        const writeText = vi.fn(async () => {});
        setGlobal('navigator', { clipboard: { writeText } });

        await expect(copyToClipboard('hello')).resolves.toBe(true);
        expect(execCommand).toHaveBeenCalledWith('copy');
        expect(writeText).not.toHaveBeenCalled();
    });

    it('uses navigator.clipboard.writeText when execCommand fails', async () => {
        const execCommand = vi.fn(() => false);

        setGlobal('document', {
            body: { appendChild: vi.fn(), removeChild: vi.fn() },
            activeElement: null,
            createElement: vi.fn(() => ({
                value: '',
                setAttribute: vi.fn(),
                style: {},
                focus: vi.fn(),
                select: vi.fn(),
                setSelectionRange: vi.fn(),
            })),
            getSelection: vi.fn(() => null),
            execCommand,
        });

        const writeText = vi.fn(async () => {});
        setGlobal('navigator', { clipboard: { writeText } });

        await expect(copyToClipboard('hello')).resolves.toBe(true);
        expect(execCommand).toHaveBeenCalledWith('copy');
        expect(writeText).toHaveBeenCalledWith('hello');
    });

    it('returns false when both strategies fail', async () => {
        const execCommand = vi.fn(() => false);

        setGlobal('document', {
            body: { appendChild: vi.fn(), removeChild: vi.fn() },
            activeElement: null,
            createElement: vi.fn(() => ({
                value: '',
                setAttribute: vi.fn(),
                style: {},
                focus: vi.fn(),
                select: vi.fn(),
                setSelectionRange: vi.fn(),
            })),
            getSelection: vi.fn(() => null),
            execCommand,
        });

        const writeText = vi.fn(async () => {
            throw new Error('blocked');
        });
        setGlobal('navigator', { clipboard: { writeText } });

        await expect(copyToClipboard('hello')).resolves.toBe(false);
        expect(execCommand).toHaveBeenCalledWith('copy');
        expect(writeText).toHaveBeenCalledWith('hello');
    });
});
