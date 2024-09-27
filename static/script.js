document.addEventListener('DOMContentLoaded', function() {
    const folderToggles = document.querySelectorAll('.folder > span');
    const selectAllBtn = document.getElementById('select-all');
    const deselectAllBtn = document.getElementById('deselect-all');
    const copyContentBtn = document.getElementById('copy-content');

    folderToggles.forEach(folder => {
        folder.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleFolder(folder.parentElement.id);
        });
    });

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', selectAll);
    }

    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', deselectAll);
    }

    if (copyContentBtn) {
        copyContentBtn.addEventListener('click', copyToClipboard);
    }
});

function toggleFolder(id) {
    const folder = document.getElementById(id);
    folder.classList.toggle('open');
    const folderContent = folder.querySelector('.folder-content');
    if (folderContent) {
        folderContent.style.display = folder.classList.contains('open') ? 'block' : 'none';
    }
}

function selectAll() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => checkbox.checked = true);
}

function deselectAll() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
}

function copyToClipboard() {
    const textarea = document.querySelector('textarea');
    textarea.select();
    document.execCommand('copy');
    alert('Content copied to clipboard!');
}