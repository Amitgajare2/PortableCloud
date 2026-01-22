document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const folderInput = document.getElementById("folder");
    const progressBar = document.getElementById("progressBar");
    const status = document.getElementById("status");
    const previewModal = document.getElementById("previewModal");

    // file upload with multiple files support
    uploadForm.addEventListener("submit", e => {
        e.preventDefault();

        const files = fileInput.files;
        if (files.length === 0) return;

        status.textContent = `Uploading ${files.length} file(s)...`;
        progressBar.style.width = "0%";

        let completedUploads = 0;
        const totalFiles = files.length;

        // Upload files sequentially to avoid overwhelming the server
        const uploadFile = (index) => {
            if (index >= totalFiles) {
                status.textContent = "Upload complete!";
                setTimeout(() => {
                    // Preserve search parameters when reloading
                    window.location.href = preserveSearchParams();
                }, 1000);
                return;
            }

            const file = files[index];
            const fd = new FormData();
            fd.append("file", file);
            fd.append("folder", folderInput.value);

            const xhr = new XMLHttpRequest();
            xhr.open("POST", "/upload", true);

            xhr.upload.onprogress = e => {
                const fileProgress = (e.loaded / e.total) * 100;
                const totalProgress = ((completedUploads + (fileProgress / 100)) / totalFiles) * 100;
                progressBar.style.width = totalProgress + "%";
                status.textContent = `Uploading ${file.name} (${Math.round(fileProgress)}%)`;
            };

            xhr.onload = () => {
                if (xhr.status === 204) {
                    completedUploads++;
                    uploadFile(index + 1);
                } else {
                    status.textContent = `Error uploading ${file.name}`;
                }
            };

            xhr.onerror = () => {
                status.textContent = `Error uploading ${file.name}`;
            };

            xhr.send(fd);
        };

        uploadFile(0);
    });

    // Update file input label with selected files
    fileInput.addEventListener("change", () => {
        const label = document.querySelector(".upload-text");
        const files = fileInput.files;

        if (files.length === 0) {
            label.textContent = "Choose Files";
        } else if (files.length === 1) {
            label.textContent = files[0].name;
        } else {
            label.textContent = `${files.length} files selected`;
        }
    });

    // Search functionality
    const searchForm = document.querySelector('.search-form');
    const typeFilter = document.querySelector('.type-filter');

    // Auto-submit on type filter change
    if (typeFilter) {
        typeFilter.addEventListener('change', () => {
            searchForm.submit();
        });
    }

    // Preserve search parameters when uploading
    const preserveSearchParams = () => {
        const urlParams = new URLSearchParams(window.location.search);
        const searchQuery = urlParams.get('search') || '';
        const typeFilter = urlParams.get('type') || 'all';
        const currentPage = urlParams.get('page') || '1';

        let newUrl = window.location.pathname;
        const params = [];

        if (searchQuery) params.push(`search=${encodeURIComponent(searchQuery)}`);
        if (typeFilter !== 'all') params.push(`type=${encodeURIComponent(typeFilter)}`);
        params.push(`page=${currentPage}`);

        if (params.length > 0) {
            newUrl += '?' + params.join('&');
        }

        return newUrl;
    };

    // Preview modal functionality
    window.openModal = function (src, type) {
        const modalContent = document.getElementById("modalContent");

        if (type === "image") {
            modalContent.innerHTML = `<img src="${src}" alt="Preview" style="max-width: 100%; max-height: 100%; border-radius: 12px;">`;
        } else if (type === "video") {
            modalContent.innerHTML = `<video src="${src}" controls autoplay style="max-width: 100%; max-height: 100%; border-radius: 12px;"></video>`;
        }

        previewModal.classList.add("show");
    };

    window.closeModal = function () {
        previewModal.classList.remove("show");
        // Stop any playing video
        const video = previewModal.querySelector("video");
        if (video) {
            video.pause();
            video.currentTime = 0;
        }
    };

    // Close modal when clicking outside
    previewModal.addEventListener("click", (e) => {
        if (e.target === previewModal) {
            closeModal();
        }
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            if (previewModal.classList.contains("show")) {
                closeModal();
            }
        }
    });

    // Drag and drop functionality
    const uploadSection = document.querySelector(".upload-section");
    let dragCounter = 0;

    uploadSection.addEventListener("dragenter", (e) => {
        e.preventDefault();
        dragCounter++;
        uploadSection.style.background = "rgba(255, 255, 255, 0.4)";
        uploadSection.style.transform = "scale(1.02)";
    });

    uploadSection.addEventListener("dragleave", (e) => {
        e.preventDefault();
        dragCounter--;
        if (dragCounter === 0) {
            uploadSection.style.background = "";
            uploadSection.style.transform = "";
        }
    });

    uploadSection.addEventListener("dragover", (e) => {
        e.preventDefault();
    });

    uploadSection.addEventListener("drop", (e) => {
        e.preventDefault();
        dragCounter = 0;
        uploadSection.style.background = "";
        uploadSection.style.transform = "";

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;

            // Trigger the change event to update the label
            const event = new Event("change", { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    });

    // Auto-hide status messages
    const hideStatus = () => {
        setTimeout(() => {
            if (status.textContent && !status.textContent.includes("...")) {
                status.textContent = "";
            }
        }, 3000);
    };

    // Watch for status changes
    const observer = new MutationObserver(hideStatus);
    observer.observe(status, { childList: true, subtree: true });

    // Smooth pagination navigation
    document.querySelectorAll('.pagination-btn:not(.disabled):not(.pagination-current)').forEach(btn => {
        btn.addEventListener('click', function (e) {
            // Add loading state
            this.style.opacity = '0.7';
            this.style.pointerEvents = 'none';
        });
    });
});

// Server info toggle functionality
window.toggleServerInfo = function() {
    const serverAddresses = document.getElementById('serverAddresses');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (serverAddresses.style.display === 'none') {
        serverAddresses.style.display = 'block';
        toggleIcon.textContent = '▼';
    } else {
        serverAddresses.style.display = 'none';
        toggleIcon.textContent = '▶';
    }
};

// Copy to clipboard functionality
window.copyToClipboard = function(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const copyText = button.querySelector('.copy-text');
        const originalText = copyText.textContent;
        
        copyText.textContent = 'Copied!';
        button.style.background = '#4CAF50';
        
        setTimeout(() => {
            copyText.textContent = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        const copyText = button.querySelector('.copy-text');
        const originalText = copyText.textContent;
        
        copyText.textContent = 'Copied!';
        button.style.background = '#4CAF50';
        
        setTimeout(() => {
            copyText.textContent = originalText;
            button.style.background = '';
        }, 2000);
    });
};
