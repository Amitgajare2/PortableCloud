from flask import Flask, render_template, request, send_from_directory, redirect, jsonify
import os
import shutil
import mimetypes
import time
from werkzeug.utils import secure_filename
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB max file size

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg")
VIDEO_EXT = (".mp4", ".webm", ".ogg", ".avi", ".mov", ".mkv")
AUDIO_EXT = (".mp3", ".wav", ".ogg", ".m4a", ".flac")

def file_type(name):
    """Determine file type based on extension"""
    n = name.lower()
    if n.endswith(IMAGE_EXT): 
        return "image"
    if n.endswith(VIDEO_EXT): 
        return "video"
    if n.endswith(AUDIO_EXT): 
        return "audio"
    return "file"

def get_file_size(filepath):
    """Get human readable file size"""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"

def list_items(path, search_query=None, file_type_filter=None):
    """List all items in a directory with metadata and optional filtering, sorted by newest first"""
    items = []
    try:
        # Get current time for "new" badge calculation
        current_time = time.time()
        twenty_four_hours = 24 * 60 * 60  # 24 hours in seconds
        
        # Get all items with their modification times
        items_with_time = []
        for item_name in os.listdir(path):
            full_path = os.path.join(path, item_name)
            is_dir = os.path.isdir(full_path)
            
            try:
                # Get modification time for sorting
                mod_time = os.path.getmtime(full_path)
            except:
                mod_time = 0
            
            # Check if item is new (uploaded in last 24 hours)
            is_new = (current_time - mod_time) < twenty_four_hours
            
            item_data = {
                "name": item_name,
                "is_dir": is_dir,
                "type": "folder" if is_dir else file_type(item_name),
                "mod_time": mod_time,
                "is_new": is_new
            }
            
            if not is_dir:
                item_data["size"] = get_file_size(full_path)
            
            # Apply search filters
            if search_query:
                search_query_lower = search_query.lower()
                if search_query_lower not in item_name.lower():
                    continue
            
            if file_type_filter and file_type_filter != "all":
                if is_dir and file_type_filter != "folder":
                    continue
                elif not is_dir and item_data["type"] != file_type_filter:
                    continue
            
            items_with_time.append(item_data)
        
        # Sort by modification time (newest first), then by name for items with same time
        items_with_time.sort(key=lambda x: (-x["mod_time"], x["name"].lower()))
        
        # Remove mod_time from the final items list but keep is_new
        for item in items_with_time:
            del item["mod_time"]
            items.append(item)
            
    except PermissionError:
        pass
    except Exception as e:
        print(f"Error listing directory {path}: {e}")
    
    return items

@app.route("/")
@app.route("/folder/<path:subpath>")
def index(subpath=""):
    """Main page showing files and folders with pagination"""
    try:
        path = os.path.join(UPLOAD_FOLDER, subpath)
        
        # Security check - ensure path is within upload folder
        if not os.path.abspath(path).startswith(os.path.abspath(UPLOAD_FOLDER)):
            return "Access denied", 403
            
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
        # Get search parameters
        search_query = request.args.get('search', '').strip()
        file_type_filter = request.args.get('type', 'all')
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 6  # Items per page
        
        all_items = list_items(path, search_query, file_type_filter)
        total_items = len(all_items)
        
        # Calculate pagination
        total_pages = (total_items + per_page - 1) // per_page  # Ceiling division
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        items = all_items[start_idx:end_idx]
        
        # Generate page numbers for pagination
        page_numbers = []
        if total_pages <= 6:
            page_numbers = list(range(1, total_pages + 1))
        else:
            if page <= 3:
                page_numbers = list(range(1, 5)) + ['...', total_pages]
            elif page >= total_pages - 2:
                page_numbers = [1, '...'] + list(range(total_pages - 3, total_pages + 1))
            else:
                page_numbers = [1, '...'] + list(range(page - 1, page + 2)) + ['...', total_pages]
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_items,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page < total_pages else None,
            'page_numbers': page_numbers
        }
        
        return render_template(
            "index.html",
            items=items,
            current=subpath,
            pagination=pagination,
            search_query=search_query,
            file_type_filter=file_type_filter
        )
    except Exception as e:
        print(f"Error in index route: {e}")
        return "Internal server error", 500

@app.route("/upload", methods=["POST"])
def upload():
    """Handle file uploads"""
    try:
        file = request.files.get("file")
        folder = request.form.get("folder", "")
        
        if not file or file.filename == "":
            return "No file selected", 400
            
        # Secure the filename
        filename = secure_filename(file.filename)
        if not filename:
            return "Invalid filename", 400
            
        # Create target directory
        target_dir = os.path.join(UPLOAD_FOLDER, folder)
        os.makedirs(target_dir, exist_ok=True)
        
        # Handle duplicate filenames
        target_path = os.path.join(target_dir, filename)
        counter = 1
        base_name, ext = os.path.splitext(filename)
        
        while os.path.exists(target_path):
            new_filename = f"{base_name}_{counter}{ext}"
            target_path = os.path.join(target_dir, new_filename)
            counter += 1
            
        # Save the file
        file.save(target_path)
        return "", 204
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return "Upload failed", 500

@app.route("/delete", methods=["POST"])
def delete():
    """Delete a file or folder"""
    try:
        path = request.form.get("path", "")
        
        if not path:
            return "Path required", 400
            
        full_path = os.path.join(UPLOAD_FOLDER, path)
        
        # Security check
        if not os.path.abspath(full_path).startswith(os.path.abspath(UPLOAD_FOLDER)):
            return "Access denied", 403
            
        if not os.path.exists(full_path):
            return "File not found", 404
            
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
            
        return "", 204
        
    except Exception as e:
        print(f"Error deleting: {e}")
        return "Delete failed", 500

@app.route("/files/<path:filename>")
def files(filename):
    """Serve uploaded files"""
    try:
        # Security check
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.abspath(file_path).startswith(os.path.abspath(UPLOAD_FOLDER)):
            return "Access denied", 403
            
        if not os.path.exists(file_path):
            return "File not found", 404
            
        # Get the directory and filename
        directory = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        
        return send_from_directory(directory, basename)
        
    except Exception as e:
        print(f"Error serving file: {e}")
        return "File not found", 404

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return "File too large. Maximum size is 500MB.", 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return "Page not found", 404

@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    return "Internal server error", 500

if __name__ == "__main__":
    print(f"Starting Portable Cloud server...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Access the application at: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
