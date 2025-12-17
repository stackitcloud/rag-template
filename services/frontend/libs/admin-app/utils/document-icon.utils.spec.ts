import {
  iconBook,
  iconFile,
  iconFileArchive,
  iconFileGlobe,
  iconFilePdf,
  iconFileText,
  iconPicture,
} from '@sit-onyx/icons';

import { getDocumentIcon } from './document-icon.utils';

describe('getDocumentIcon', () => {
  it('maps source prefixes', () => {
    expect(getDocumentIcon('confluence:Some Page')).toBe(iconBook);
    expect(getDocumentIcon('sitemap:https://example.com/sitemap.xml')).toBe(iconFileGlobe);
    expect(getDocumentIcon('other:whatever')).toBe(iconFileGlobe);
  });

  it('maps file prefix extensions', () => {
    expect(getDocumentIcon('file:report.pdf')).toBe(iconFilePdf);
    expect(getDocumentIcon('file:archive.tar.gz')).toBe(iconFileArchive);
    expect(getDocumentIcon('file:image.svg')).toBe(iconPicture);
    expect(getDocumentIcon('file:README.md')).toBe(iconFileText);
  });

  it('maps plain filenames', () => {
    expect(getDocumentIcon('report.pdf')).toBe(iconFilePdf);
    expect(getDocumentIcon('archive.zip')).toBe(iconFileArchive);
  });

  it('defaults to the generic file icon for unknown extensions', () => {
    expect(getDocumentIcon('file:unknown.bin')).toBe(iconFile);
  });

  it('handles missing or malformed extensions', () => {
    expect(getDocumentIcon('noextension')).toBe(iconFile);
    expect(getDocumentIcon('.hiddenfile')).toBe(iconFile);
    expect(getDocumentIcon('trailing.')).toBe(iconFile);
    expect(getDocumentIcon('file:')).toBe(iconFile);
  });
});

