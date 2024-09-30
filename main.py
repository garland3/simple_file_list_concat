from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import toml
import requests  # Add this import for making HTTP requests
import json

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

def get_files_recursive(base_dir, max_depth, current_depth=0, file_count=0, current_path=''):
    items = []
    if current_depth > max_depth or file_count >= MAX_FILES:
        return items, file_count
    try:
        for item in sorted(os.listdir(base_dir)):
            if file_count >= MAX_FILES:
                break
            item_path = os.path.join(base_dir, item)
            relative_path = os.path.join(current_path, item)
            file_ext = os.path.splitext(item)[1].lower()
            if file_ext in IGNORE_EXTENSIONS:
                continue
            if os.path.isfile(item_path):
                items.append({
                    'name': item,
                    'type': 'file',
                    'path': relative_path
                })
                file_count += 1
            elif os.path.isdir(item_path):
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
async def concatenate_files(request: Request,
                           selected_files: list = Form(...),
                             version_number: str = Form(...)):
    print("Version number from form:", version_number)
    content = ""
    print("Starting to concatenate files...")
    print(selected_files)
    for file in selected_files:
        file_path = BASE_DIR / file
        print(f"Processing file: {file}")
        if file_path.is_file():
            content += f"--- {file} ---\n"
            try:
                lines = file_path.read_text().splitlines()
                print(f"File {file} has {len(lines)} lines.")
                for i, line in enumerate(lines, 1):
                    content += f"{i:4d} | {line}\n"
                print(f"Length of file {file}: {len(lines)} lines.")
            except Exception as e:
                content += f"Error reading file: {str(e)}\n"
                print(f"Error reading file {file}: {str(e)}")
            content += "\n\n"
    print("Finished concatenating files.")
    return templates.TemplateResponse("result.html", {
        "request": request,
        "content": content,
        "selected_files": ','.join(selected_files),
        "version_number": version_number
    })

# This is a test for code 200
@app.get("/test_endpoint")
async def test_endpoint():
    return {"message": "Endpoint is working"}


# Route to Process Q&A in Concat V2
@app.post("/process_qa", response_class=JSONResponse)
async def process_qa(request: Request):
    data = await request.json()
    api_key = data.get("api_key")
    model = data.get("model")
    question = data.get("question")
    content = data.get("content")

    if not api_key or not model or not question:
        return JSONResponse({"error": "API key, model, and question are required."}, status_code=400)

    # Prepare the payload for GROQ API
    payload = {
        "messages": [
            {"role": "user", "content": f"{question}\n\nConcatenated Code:\n{content}"}
        ],
        "model": model
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_data = response.json()
        answer = response_data.get("choices")[0].get("message").get("content")
        return JSONResponse({"response": answer})
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return JSONResponse({"error": f"HTTP error occurred: {http_err}"}, status_code=500)
    except Exception as err:
        print(f"Other error occurred: {err}")
        return JSONResponse({"error": f"An error occurred: {err}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)