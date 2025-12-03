import gradio as gr
import os
import time
import shutil
from datetime import datetime

# Configuration
DATA_DIR = "/app/data"
TODO_DIR = os.path.join(DATA_DIR, "todo")
WORKING_DIR = os.path.join(DATA_DIR, "working")
DONE_DIR = os.path.join(DATA_DIR, "done")

# Ensure directories exist
os.makedirs(TODO_DIR, exist_ok=True)
os.makedirs(WORKING_DIR, exist_ok=True)
os.makedirs(DONE_DIR, exist_ok=True)

def get_files_df(directory, sort_by_time=False):
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        if sort_by_time:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        else:
            files.sort()
        # Return list of lists for Dataframe
        return [[f] for f in files]
    except Exception:
        return []

def get_done_files_df(directory, sort_by_time=False):
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        if sort_by_time:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        else:
            files.sort()

        data = []
        for f in files:
            path = os.path.join(directory, f)
            try:
                mtime = os.path.getmtime(path)
                dt_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')

                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read(50).strip().replace('\n', ' ')
                    if len(content) == 50:
                        content += "..."

                data.append([dt_str, f, content])
            except:
                data.append(["", f, "Error reading"])
        return data
    except:
        return []

def read_file_content(directory, filename):
    if not filename or not isinstance(filename, str):
        return ""

    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    return "File not found."

def create_todo_file(text):
    if not text.strip():
        raise gr.Error("Text cannot be empty.")
    filename = f"tts_{int(time.time())}.txt"
    filepath = os.path.join(TODO_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        gr.Info(f"Created {filename}")
        return f"Created {filename}"
    except Exception as e:
        raise gr.Error(f"Error creating file: {e}")

def replay_file(filename):
    if not filename:
        raise gr.Warning("No file selected.")

    source = os.path.join(DONE_DIR, filename)
    dest = os.path.join(TODO_DIR, filename)
    if os.path.exists(source):
        try:
            shutil.move(source, dest)
            gr.Info(f"Moved {filename} to Todo.")
            return f"Moved {filename} to Todo."
        except Exception as e:
            raise gr.Error(f"Error moving file: {e}")
    raise gr.Error("File not found.")

def cancel_processing(filename):
    # In Working tab, filename might be passed from the content view or list
    # But usually we want to cancel the *currently processing* file.
    # If filename is passed, use it. If not, try to find the first file in working.

    target_file = filename
    if not target_file:
        files = os.listdir(WORKING_DIR)
        if files:
            target_file = files[0]

    if not target_file:
        raise gr.Warning("No file to cancel.")

    source = os.path.join(WORKING_DIR, target_file)
    dest = os.path.join(DONE_DIR, target_file)

    if os.path.exists(source):
        try:
            shutil.move(source, dest)
            gr.Info(f"Cancelled {target_file}")
            return f"Cancelled {target_file} (Moved to Done)."
        except Exception as e:
            raise gr.Error(f"Error cancelling file: {e}")
    raise gr.Error("File not found in Working.")

def upload_file(file_obj):
    if file_obj is None:
        raise gr.Warning("No file uploaded.")

    try:
        src_path = file_obj.name if hasattr(file_obj, 'name') else file_obj
        filename = os.path.basename(src_path)
        dest_path = os.path.join(TODO_DIR, filename)
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{int(time.time())}{ext}"
            dest_path = os.path.join(TODO_DIR, filename)

        shutil.copy(src_path, dest_path)
        gr.Info(f"Uploaded {filename}")
        return f"Uploaded {filename}"
    except Exception as e:
        raise gr.Error(f"Error uploading: {e}")

# Event handlers for selection
def on_select_todo(evt: gr.SelectData, df_data):
    try:
        row = evt.index[0]
        item = df_data[row]
        if isinstance(item, list):
            filename = item[0]
        else:
            filename = item
        return read_file_content(TODO_DIR, filename), filename
    except Exception:
        return "", ""

def on_select_working(evt: gr.SelectData, df_data):
    try:
        row = evt.index[0]
        item = df_data[row]
        if isinstance(item, list):
            filename = item[0]
        else:
            filename = item
        return read_file_content(WORKING_DIR, filename), filename
    except Exception:
        return "", ""

def on_select_done(evt: gr.SelectData, df_data):
    try:
        row = evt.index[0]
        item = df_data[row]
        if isinstance(item, list) and len(item) > 1:
            filename = item[1] # Column 1 is filename
        else:
            filename = str(item) # Fallback
        return read_file_content(DONE_DIR, filename), filename
    except Exception:
        return "", ""

# --- UI Definition ---
theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="slate",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"]
)

with gr.Blocks(title="TTS Dashboard") as demo:
    demo.theme = theme
    with gr.Row():
        with gr.Column():
            gr.Markdown(
                """
                # 🎙️ TTS Dashboard
                Manage your text-to-speech queue, monitor processing, and review history.
                """
            )

    # State to hold selected filename for actions
    selected_todo_file = gr.State("")
    selected_working_file = gr.State("")
    selected_done_file = gr.State("")

    with gr.Tabs() as tabs:
        # --- TODO TAB ---
        with gr.TabItem("📝 Queue", id=0):
            with gr.Row():
                # Left Column: List
                with gr.Column(scale=1, variant="panel"):
                    gr.Markdown("### 📋 Pending Files")
                    todo_list = gr.Dataframe(
                        headers=["Filename"],
                        datatype=["str"],
                        value=lambda: get_files_df(TODO_DIR),
                        interactive=False,
                        type="array",
                        elem_id="todo_list"
                    )
                    refresh_todo_btn = gr.Button("🔄 Refresh List", size="sm")

                # Right Column: Content & Actions
                with gr.Column(scale=2):
                    gr.Markdown("### 📄 Content Preview")
                    todo_content = gr.Textbox(label="File Content", lines=10, interactive=False)

                    with gr.Accordion("➕ Add New Content", open=True):
                        with gr.Row():
                            new_text_input = gr.Textbox(label="Enter Text", lines=3, placeholder="Type text here to synthesize...", scale=4)
                            create_btn = gr.Button("🚀 Queue Text", variant="primary", scale=1)

                        gr.Markdown("---")
                        with gr.Row():
                            file_upload = gr.File(label="Upload Text File", scale=4)
                            # upload_status = gr.Label(label="Status", visible=False) # Using gr.Info instead

        # --- WORKING TAB ---
        with gr.TabItem("⚙️ Processing", id=1):
            with gr.Row():
                with gr.Column(scale=1, variant="panel"):
                    gr.Markdown("### ⏳ Active Jobs")
                    working_list = gr.Dataframe(
                        headers=["Filename"],
                        datatype=["str"],
                        value=lambda: get_files_df(WORKING_DIR),
                        interactive=False,
                        type="array"
                    )
                with gr.Column(scale=2):
                    gr.Markdown("### 🔊 Currently Speaking")
                    working_content = gr.Textbox(label="File Content", lines=15, interactive=False)

                    with gr.Row():
                        cancel_btn = gr.Button("🛑 Stop & Cancel", variant="stop", size="lg")

                    # cancel_status = gr.Label(label="Status", visible=False)

        # --- DONE TAB ---
        with gr.TabItem("✅ History", id=2):
            with gr.Row():
                with gr.Column(scale=1, variant="panel"):
                    gr.Markdown("### 📜 Completed")
                    done_list = gr.Dataframe(
                        headers=["Time", "Filename", "Preview"],
                        datatype=["str", "str", "str"],
                        value=lambda: get_done_files_df(DONE_DIR, sort_by_time=True),
                        interactive=False,
                        wrap=True,
                        type="array"
                    )
                    refresh_done_btn = gr.Button("🔄 Refresh List", size="sm")

                with gr.Column(scale=2):
                    gr.Markdown("### 📄 Archived Content")
                    done_content = gr.Textbox(label="File Content", lines=15, interactive=False)
                    replay_btn = gr.Button("🔁 Replay (Move to Queue)", variant="secondary")
                    # replay_status = gr.Label(label="Status", visible=False)

    # --- EVENT WIRING ---

    # Todo Events
    create_btn.click(create_todo_file, inputs=new_text_input, outputs=None) \
        .success(lambda: "", outputs=new_text_input) \
        .success(lambda: get_files_df(TODO_DIR), outputs=todo_list)

    file_upload.upload(upload_file, inputs=file_upload, outputs=None) \
        .success(lambda: get_files_df(TODO_DIR), outputs=todo_list)

    refresh_todo_btn.click(lambda: get_files_df(TODO_DIR), outputs=todo_list)
    todo_list.select(on_select_todo, inputs=[todo_list], outputs=[todo_content, selected_todo_file])

    # Working Events
    working_list.select(on_select_working, inputs=[working_list], outputs=[working_content, selected_working_file])

    cancel_btn.click(cancel_processing, inputs=selected_working_file, outputs=None) \
        .success(lambda: get_files_df(WORKING_DIR), outputs=working_list) \
        .success(lambda: get_done_files_df(DONE_DIR, sort_by_time=True), outputs=done_list)

    # Done Events
    refresh_done_btn.click(lambda: get_done_files_df(DONE_DIR, sort_by_time=True), outputs=done_list)
    done_list.select(on_select_done, inputs=[done_list], outputs=[done_content, selected_done_file])

    replay_btn.click(replay_file, inputs=selected_done_file, outputs=None) \
        .success(lambda: get_done_files_df(DONE_DIR, sort_by_time=True), outputs=done_list)

    # --- TIMER ---
    timer = gr.Timer(1)

    def tick():
        # Check working directory
        w_files = get_files_df(WORKING_DIR)
        t_files = get_files_df(TODO_DIR)
        d_files = get_done_files_df(DONE_DIR, sort_by_time=True)

        if w_files:
            # Auto-select the first file content
            try:
                filename = w_files[0][0]
                content = read_file_content(WORKING_DIR, filename)
                return gr.Tabs(selected=1), t_files, w_files, d_files, content, filename
            except:
                return gr.Tabs(selected=1), t_files, w_files, d_files, "", ""

        return gr.update(), t_files, w_files, d_files, gr.update(), gr.update()

    timer.tick(tick, outputs=[tabs, todo_list, working_list, done_list, working_content, selected_working_file])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
