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
with open("settings.toml", "r") as f:
    settings = toml.load(f)

# Initial BASE_DIR setting
BASE_DIR = Path(settings["base_dir"]) if settings["base_dir"] else Path("../")
MAX_DEPTH = settings["max_depth"]
MAX_FILES = settings["max_files"]
IGNORE_EXTENSIONS = settings["ignore_extensions"]

def get_files_recursive(base_dir, max_depth, current_depth=0, file_count=0):
    items = []
    if current_depth > max_depth or file_count >= MAX_FILES:
        return items, file_count
    try:
        for item in sorted(os.listdir(base_dir)):
            if file_count >= MAX_FILES:
                break
            item_path = os.path.join(base_dir, item)
            file_ext = os.path.splitext(item)[1].lower()
            if file_ext in IGNORE_EXTENSIONS:
                continue
            if os.path.isfile(item_path):
                items.append({
                    'name': item,
                    'type': 'file'
                })
                file_count += 1
            elif os.path.isdir(item_path):
                folder = {
                    'name': item,
                    'type': 'folder',
                    'children': []
                }
                sub_items, file_count = get_files_recursive(item_path, max_depth, current_depth + 1, file_count)
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
async def update_base_dir(new_base_dir: str = Form(...)):
    global BASE_DIR
    try:
        new_path = Path(new_base_dir)
        if not new_path.is_dir():
            raise ValueError("The specified path is not a valid directory.")
        BASE_DIR = new_path
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        error_message = f"Error updating base directory: {str(e)}"
        return RedirectResponse(url=f"/?error={error_message}", status_code=303)

@app.post("/concatenate", response_class=HTMLResponse)
async def concatenate_files(request: Request, selected_files: list = Form(...)):
    print("Concatenating files:")
    print(selected_files)  # This should now be a list of selected files
    print("BASE_DIR:", BASE_DIR)
    content = ""
    for file in selected_files:
        file_path = BASE_DIR / file
        print(f"Processing file: {file}")
        if file_path.is_file():
            print(f"File found: {file}")
            content += f"--- {file} ---\n"
            try:
                content += file_path.read_text()
                print(f"Successfully read file: {file}")
            except Exception as e:
                content += f"Error reading file: {str(e)}\n"
                print(f"Error reading file: {file}, Error: {str(e)}")
            content += "\n\n"
    return templates.TemplateResponse("result.html", {
        "request": request,
        "content": content,
        "selected_files": ','.join(selected_files)
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)