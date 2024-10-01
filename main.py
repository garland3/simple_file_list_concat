# main.py

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import toml

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Load settings
SETTINGS_PATH = "settings.toml"

if not Path(SETTINGS_PATH).is_file():
    # Create a default settings.toml if it doesn't exist
    default_settings = {
        "base_dir": "../",
        "max_depth": 3,
        "max_files": 1000,
        "ignore_extensions": [".tmp", ".log", ".bak"]
    }
    with open(SETTINGS_PATH, "w") as f:
        toml.dump(default_settings, f)

with open(SETTINGS_PATH, "r") as f:
    settings = toml.load(f)

# Initial BASE_DIR setting
BASE_DIR = Path(settings["base_dir"]).resolve() if settings.get("base_dir") else Path("../").resolve()
MAX_DEPTH = settings.get("max_depth", 3)
MAX_FILES = settings.get("max_files", 1000)
IGNORE_EXTENSIONS = set(ext.lower() for ext in settings.get("ignore_extensions", []))


def get_files_recursive(base_dir, max_depth, current_depth=0, file_count=0, current_path=''):
    items = []
    if current_depth > max_depth or file_count >= MAX_FILES:
        return items, file_count
    try:
        for item in sorted(os.listdir(base_dir)):
            if file_count >= MAX_FILES:
                break
            item_path = base_dir / item
            relative_path = (Path(current_path) / item).as_posix()
            file_ext = item_path.suffix.lower()
            if file_ext in IGNORE_EXTENSIONS:
                continue
            if item_path.is_file():
                items.append({
                    'name': item,
                    'type': 'file',
                    'path': relative_path
                })
                file_count += 1
            elif item_path.is_dir():
                folder = {
                    'name': item,
                    'type': 'folder',
                    'children': []
                }
                sub_items, file_count = get_files_recursive(item_path, max_depth, current_depth + 1, file_count, relative_path)
                folder['children'] = sub_items
                items.append(folder)
    except PermissionError:
        items.append({
            'name': 'Permission denied',
            'type': 'error'
        })
    except FileNotFoundError:
        items.append({
            'name': 'Directory not found',
            'type': 'error'
        })
    return items, file_count


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/file_structure", response_class=JSONResponse)
async def file_structure():
    files, _ = get_files_recursive(BASE_DIR, MAX_DEPTH)
    return JSONResponse(content=files)


@app.post("/update_base_dir")
async def update_base_dir(request: Request, new_base_dir: str = Form(...)):
    global BASE_DIR
    try:
        new_path = Path(new_base_dir).resolve()
        if not new_path.is_dir():
            raise ValueError("The specified path is not a valid directory.")
        BASE_DIR = new_path
        # Update settings.toml
        settings["base_dir"] = str(BASE_DIR)
        with open(SETTINGS_PATH, "w") as f:
            toml.dump(settings, f)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        error_message = f"Error updating base directory: {str(e)}"
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": error_message
        })


@app.post("/results", response_class=HTMLResponse)
async def concatenate_files(request: Request,
                            selected_files: list = Form(...),
                            include_line_numbers: bool = Form(False)):
    if not selected_files:
        error_message = "No files selected for concatenation."
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": error_message
        })

    content = ""
    for file in selected_files:
        file_path = BASE_DIR / file
        if file_path.is_file():
            content += f"--- {file} ---\n"
            try:
                lines = file_path.read_text(encoding='utf-8', errors='replace').splitlines()
                for i, line in enumerate(lines, 1):
                    if include_line_numbers:
                        content += f"{i:4d} | {line}\n"
                    else:
                        content += f"{line}\n"
                content += "\n\n"
            except Exception as e:
                content += f"Error reading file {file}: {str(e)}\n\n"
        else:
            content += f"File not found: {file}\n\n"

    return templates.TemplateResponse("result.html", {
        "request": request,
        "content": content,
        "selected_files": selected_files,
        "include_line_numbers": include_line_numbers
    })

@app.post("/concat_with_ai", response_class=HTMLResponse)
async def concat_with_ai(request: Request,
                          selected_files: list = Form(...)):
    if not selected_files:
        error_message = "No files selected for concatenation."
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": error_message
        })

    file_data = []
    for file in selected_files:
        file_path = BASE_DIR / file
        if file_path.is_file():
            file_data.append((file_path.name, file_path.read_text(encoding='utf-8', errors='replace')))
        else:
            error_message = f"File not found: {file}"
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": error_message
            })

    return templates.TemplateResponse("results_ai.html", {
        "request": request,
        "file_data": file_data
    })



@app.get("/test_endpoint")
async def test_endpoint():
    return {"message": "Endpoint is working"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
