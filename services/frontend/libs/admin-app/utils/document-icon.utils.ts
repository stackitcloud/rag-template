import {
  iconBook,
  iconFile,
  iconFileArchive,
  iconFileAudio,
  iconFileCsv,
  iconFileDoc,
  iconFileGlobe,
  iconFilePdf,
  iconFilePpt,
  iconFileRtf,
  iconFileText,
  iconFileXls,
  iconFileXlsx,
  iconPicture,
} from "@sit-onyx/icons";

const splitSourcePrefix = (documentName: string): { source?: string; rest: string } => {
  const trimmed = String(documentName ?? "").trim();
  const separatorIndex = trimmed.indexOf(":");
  if (separatorIndex === -1) {
    return { rest: trimmed };
  }

  const source = trimmed.slice(0, separatorIndex).toLowerCase();
  const rest = trimmed.slice(separatorIndex + 1);
  return { source, rest };
};

const getFileExtension = (filename: string): string | null => {
  const normalized = String(filename ?? "").trim();
  const lastDot = normalized.lastIndexOf(".");
  if (lastDot <= 0 || lastDot === normalized.length - 1) {
    return null;
  }
  return normalized.slice(lastDot + 1).toLowerCase();
};

export const getDocumentIcon = (documentName: string): string => {
  const { source, rest } = splitSourcePrefix(documentName);

  if (source && source !== "file") {
    if (source === "sitemap") return iconFileGlobe;
    if (source === "confluence") return iconBook;
    return iconFileGlobe;
  }

  const filename = source === "file" ? rest : documentName;
  const extension = getFileExtension(filename);

  switch (extension) {
    case "pdf":
      return iconFilePdf;
    case "doc":
    case "docx":
      return iconFileDoc;
    case "ppt":
    case "pptx":
      return iconFilePpt;
    case "xls":
      return iconFileXls;
    case "xlsx":
      return iconFileXlsx;
    case "csv":
      return iconFileCsv;
    case "rtf":
      return iconFileRtf;
    case "zip":
    case "rar":
    case "7z":
    case "tar":
    case "gz":
    case "tgz":
      return iconFileArchive;
    case "mp3":
    case "wav":
    case "flac":
    case "ogg":
    case "m4a":
      return iconFileAudio;
    case "epub":
      return iconBook;
    case "jpeg":
    case "jpg":
    case "png":
    case "gif":
    case "bmp":
    case "tif":
    case "tiff":
    case "webp":
    case "svg":
      return iconPicture;
    case "xml":
    case "html":
    case "htm":
    case "md":
    case "mdx":
    case "txt":
    case "asciidoc":
    case "adoc":
      return iconFileText;
    default:
      return iconFile;
  }
};

