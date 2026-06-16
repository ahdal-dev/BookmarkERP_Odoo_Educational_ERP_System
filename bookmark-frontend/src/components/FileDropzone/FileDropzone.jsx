import { useRef, useState, useCallback } from 'react';
import styles from './FileDropzone.module.css';

/* ============================================================
   FILE DROPZONE — Dashed-border drop area with cloud icon,
   accepted formats, and browse button.
   ============================================================ */

export default function FileDropzone({
  onFileSelect,
  acceptedFormats = 'PDF, JPEG, PNG',
  maxSize = '10MB',
  files = [],
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = useCallback((fileList) => {
    if (fileList?.length) {
      onFileSelect?.(Array.from(fileList));
    }
  }, [onFileSelect]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  return (
    <div
      className={`${styles.dropzone} ${isDragging ? styles.dragging : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={() => setIsDragging(false)}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        className={styles.fileInput}
        multiple
        onChange={(e) => handleFiles(e.target.files)}
        accept={acceptedFormats.split(',').map(f => `.${f.trim().toLowerCase()}`).join(',')}
      />

      {/* Cloud upload icon */}
      <div className={styles.iconWrap}>
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="var(--color-lime)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M32 32l-8-8-8 8" />
          <path d="M24 24v18" />
          <path d="M40.78 35.61A8 8 0 0036 20H33.51A12.79 12.79 0 108 28.54" />
          <path d="M32 32l-8-8-8 8" />
        </svg>
      </div>

      <p className={styles.mainText}>Drag and drop files here</p>
      <p className={styles.subText}>{acceptedFormats} · Max {maxSize}</p>
      <button
        type="button"
        className={styles.browseBtn}
        onClick={(e) => { e.stopPropagation(); inputRef.current?.click(); }}
      >
        Browse Files
      </button>

      {/* Show uploaded files */}
      {files.length > 0 && (
        <div className={styles.fileList}>
          {files.map((f, i) => (
            <div key={i} className={styles.fileItem}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-lime)" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>
              <span>{f.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
