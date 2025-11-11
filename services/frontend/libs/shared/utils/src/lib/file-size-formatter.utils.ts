export const formatFileSizeToString = (bytes: number | undefined, decimals = 2) => {
    if (!bytes) {
        return '-';
    }

    const prefix = ['B', 'KB', 'MB'];
    let index = 0;
    let size = bytes;
    while (size > 1024) {
        size /= 1024;
        index++;
    }
    return `${size.toFixed(decimals)} ${prefix[index]}`;
}