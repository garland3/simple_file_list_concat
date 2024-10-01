// static/script.js

document.addEventListener('DOMContentLoaded', async () => {
    const fileExplorer = document.getElementById('file-explorer');
    if (!fileExplorer) {
        console.warn("No element with id 'file-explorer' found. Skipping file explorer initialization.");
        return; // Exit if the file explorer is not present
    }

    const selectAllBtn = document.getElementById('select-all');
    const deselectAllBtn = document.getElementById('deselect-all');
    const concatenateBtn = document.getElementById('concatenate-btn');

    // Retrieve selected files from local storage
    let selectedFiles = JSON.parse(localStorage.getItem('selectedFiles')) || [];

    // Fetch and render the file structure
    const fileStructure = await fetchFileStructure();
    createFileExplorer(fileStructure, fileExplorer);

    // After rendering, set the checkboxes based on selectedFiles
    setSelectedFiles(selectedFiles);

    // Expand folders that contain selected files
    expandFoldersWithSelectedFiles(fileExplorer);

    // Event listeners for Select All and Deselect All
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            selectAll();
            selectedFiles = getAllFilePaths(fileStructure);
            updateLocalStorage(selectedFiles);
            expandFoldersWithSelectedFiles(fileExplorer);
        });
    }

    if (deselectAllBtn) {
        deselectAll();
        selectedFiles = [];
        updateLocalStorage(selectedFiles);
    }

    // Event listener for Concatenate button
    if (concatenateBtn) {
        concatenateBtn.addEventListener('click', () => {
            selectedFiles = getSelectedFiles();
            const includeLineNumbers = document.getElementById('include-line-numbers').checked;

            if (selectedFiles.length > 0) {
                // Save selected files to local storage
                updateLocalStorage(selectedFiles);

                // Create a form and submit
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/results';

                selectedFiles.forEach(file => {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'selected_files';
                    input.value = file;
                    form.appendChild(input);
                });

                const lineNumberInput = document.createElement('input');
                lineNumberInput.type = 'hidden';
                lineNumberInput.name = 'include_line_numbers';
                lineNumberInput.value = includeLineNumbers;
                form.appendChild(lineNumberInput);

                document.body.appendChild(form);
                form.submit();
            } else {
                alert('Please select at least one file to concatenate.');
            }
        });
    }

    // Update local storage when checkboxes are changed
    fileExplorer.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            if (e.target.checked) {
                if (!selectedFiles.includes(e.target.value)) {
                    selectedFiles.push(e.target.value);
                }
            } else {
                selectedFiles = selectedFiles.filter(file => file !== e.target.value);
            }
            updateLocalStorage(selectedFiles);
            // After selection, expand folders containing the selected file
            if (e.target.checked) {
                expandFoldersContainingFile(fileExplorer, e.target.value);
            }
        }
    });

    // Optional: Clear selected files when base directory is updated
    const baseFolderForm = document.querySelector('.folder-settings form');
    if (baseFolderForm) {
        baseFolderForm.addEventListener('submit', () => {
            localStorage.removeItem('selectedFiles');
        });
    }
});

/**
 * Fetch the file structure from the backend.
 */
async function fetchFileStructure() {
    try {
        const response = await fetch('/file_structure');
        if (!response.ok) {
            alert('Failed to fetch file structure.');
            return [];
        }
        const fileStructure = await response.json();
        return fileStructure;
    } catch (error) {
        console.error('Error fetching file structure:', error);
        alert('An error occurred while fetching the file structure.');
        return [];
    }
}

/**
 * Create the file explorer in the DOM.
 */
/**
 * Create the file explorer in the DOM.
 */
/**
 * Create the file explorer in the DOM.
 */
function createFileExplorer(structure, parentElement, currentPath = '') {
    const ul = document.createElement('ul');
    structure.forEach(item => {
        const li = document.createElement('li');
        li.classList.add(item.type);

        if (item.type === 'file') {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = item.path;
            checkbox.id = `file-${currentPath}/${item.name}`.replace(/\//g, '-'); // Unique ID

            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
            label.textContent = item.name;

            li.appendChild(checkbox);
            li.appendChild(label);
        } else if (item.type === 'folder') {
            const span = document.createElement('span');
            span.textContent = item.name;
            span.classList.add('folder-toggle');
            li.appendChild(span);

            if (item.children && item.children.length > 0) {
                const nestedUl = createFileExplorer(item.children, li, item.path);
                nestedUl.style.display = 'none'; // Initially hide the child items
                li.appendChild(nestedUl);

                // Add click event listener for folder toggle
                span.addEventListener('click', () => {
                    const isOpen = nestedUl.style.display === 'block';
                    nestedUl.style.display = isOpen ? 'none' : 'block'; // Toggle display
                    span.classList.toggle('open', !isOpen); // Optionally add 'open' class for styling
                });
            }
        } else if (item.type === 'error') {
            li.textContent = item.name;
            li.classList.add('error');
        }

        ul.appendChild(li);
    });
    parentElement.appendChild(ul);
    return ul; // Return the created ul element
}



/**
 * Set checkboxes based on selectedFiles array.
 */
function setSelectedFiles(selectedFiles) {
    selectedFiles.forEach(filePath => {
        const checkbox = document.querySelector(`input[type="checkbox"][value="${filePath}"]`);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
}

/**
 * Update local storage with the selected files.
 */
function updateLocalStorage(selectedFiles) {
    localStorage.setItem('selectedFiles', JSON.stringify(selectedFiles));
}

/**
 * Get all file paths from the file structure.
 * Useful for "Select All" functionality.
 */
function getAllFilePaths(structure, currentPath = '') {
    let paths = [];
    structure.forEach(item => {
        const itemPath = currentPath ? `${currentPath}/${item.name}` : item.name;
        if (item.type === 'file') {
            paths.push(itemPath);
        } else if (item.type === 'folder' && item.children) {
            paths = paths.concat(getAllFilePaths(item.children, itemPath));
        }
    });
    return paths;
}

/**
 * Select all checkboxes.
 */
function selectAll() {
    const checkboxes = document.querySelectorAll('#file-explorer input[type="checkbox"]');
    checkboxes.forEach(checkbox => checkbox.checked = true);
}

/**
 * Deselect all checkboxes.
 */
function deselectAll() {
    const checkboxes = document.querySelectorAll('#file-explorer input[type="checkbox"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
}

/**
 * Get selected file paths.
 */
function getSelectedFiles() {
    const checkboxes = document.querySelectorAll('#file-explorer input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(checkbox => checkbox.value);
}

/**
 * Expand all folders that contain the specified file.
 */
function expandFoldersContainingFile(parentElement, filePath) {
    const parts = filePath.split('/');
    let currentPath = '';
    parts.slice(0, -1).forEach(part => {
        currentPath += part + '/';
        const folderName = part;
        const folderSpan = Array.from(parentElement.querySelectorAll('span.folder-toggle')).find(span => span.textContent === folderName);
        if (folderSpan) {
            const parentLi = folderSpan.parentElement;
            parentLi.classList.add('open');
            const nestedUl = parentLi.querySelector('ul');
            if (nestedUl) {
                nestedUl.style.display = 'block';
            }
        }
    });
}

/**
 * Expand all folders that contain any selected files.
 */
function expandFoldersWithSelectedFiles(parentElement) {
    const selectedFiles = JSON.parse(localStorage.getItem('selectedFiles')) || [];
    selectedFiles.forEach(filePath => {
        expandFoldersContainingFile(parentElement, filePath);
    });
}

const concatenateWithAI = document.getElementById('concatenate-with-ai-btn');
if (concatenateWithAI) {
    concatenateWithAI.addEventListener('click', () => {
        const selectedFiles = getSelectedFiles();
        const includeLineNumbers = document.getElementById('include-line-numbers').checked;

        if (selectedFiles.length > 0) {
            // Save selected files to local storage
            updateLocalStorage(selectedFiles);

            // Create a form and submit
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/concat_with_ai';

            selectedFiles.forEach(file => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'selected_files';
                input.value = file;
                form.appendChild(input);
            });

            const lineNumberInput = document.createElement('input');
            lineNumberInput.type = 'hidden';
            lineNumberInput.name = 'include_line_numbers';
            lineNumberInput.value = includeLineNumbers;
            form.appendChild(lineNumberInput);

            document.body.appendChild(form);
            form.submit();
        } else {
            alert('Please select at least one file to concatenate.');
        }
    });
}
