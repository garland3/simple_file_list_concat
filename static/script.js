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

    document.getElementById('concat-v2-btn').addEventListener('click', () => {
        const selectedFiles = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
            .map(checkbox => checkbox.value);
        if (selectedFiles.length > 0) {
            // Send selected files as an array and navigate to Concat2
            const formData = new FormData();
            selectedFiles.forEach(file => formData.append('selected_files', file));

            fetch('/concatenate_v2', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(data => {
                document.open();
                document.write(data);
                document.close();
            });
        } else {
            alert('Please select at least one file to concatenate.');
        }
    });
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