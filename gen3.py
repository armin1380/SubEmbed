import os
import subprocess
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SubtitleEmbedderApp:
    def __init__(self, master):
        self.master = master
        master.title("MKV Subtitle Embedder")
        master.geometry("1100x950") # Increased height for bigger log

        # --- NEW: Settings and Config Variables ---
        self.config_file = "config.json"
        self.mkvmerge_path = "mkvmerge" # Default value, relies on system PATH
        self.language_map = {
            "Persian": "per",
            "English": "eng",
            "French": "fre",
            "Spanish": "spa",
            "Portuguese": "por",
            "Hebrew": "heb"
        }
        self.selected_language_code = tk.StringVar(value="Persian")


        self.raw_video_files = []
        self.raw_subtitle_files = []

        self.paired_files = {}
        self.next_pair_id = 1

        self.selected_raw_video_path = None
        self.selected_raw_subtitle_path = None
        self.selected_paired_id_for_removal = None

        self.load_settings()
        self.create_widgets()

    # --- NEW: Settings Management ---
    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.mkvmerge_path = config.get("mkvmerge_path", "mkvmerge")
                    # Update the entry widget if it exists
                    if hasattr(self, 'mkvmerge_path_entry'):
                        self.mkvmerge_path_entry.delete(0, tk.END)
                        self.mkvmerge_path_entry.insert(0, self.mkvmerge_path)
        except (json.JSONDecodeError, FileNotFoundError):
            self.mkvmerge_path = "mkvmerge" # Reset to default on error
        self.log_message(f"Loaded mkvmerge path: {self.mkvmerge_path}", is_startup=True)


    def save_settings(self):
        config = {"mkvmerge_path": self.mkvmerge_path}
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        self.log_message(f"Settings saved. New mkvmerge path: {self.mkvmerge_path}")

    def select_mkvmerge_path(self):
        path = filedialog.askopenfilename(
            title="Select mkvmerge.exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        if path and "mkvmerge.exe" in os.path.basename(path):
            self.mkvmerge_path = path
            self.mkvmerge_path_entry.delete(0, tk.END)
            self.mkvmerge_path_entry.insert(0, self.mkvmerge_path)
            self.save_settings()
            messagebox.showinfo("Success", f"mkvmerge path set to:\n{self.mkvmerge_path}")
        elif path:
            messagebox.showwarning("Warning", "The selected file does not appear to be mkvmerge.exe. Please select the correct file.")


    def create_widgets(self):
        # --- NEW: Tab View ---
        self.tabview = ctk.CTkTabview(self.master)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.processing_tab = self.tabview.add("Processing")
        self.settings_tab = self.tabview.add("Settings")

        self.create_processing_tab_widgets()
        self.create_settings_tab_widgets()

        # --- Log Section (outside tabs) ---
        log_frame = ctk.CTkFrame(self.master)
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.log_label = ctk.CTkLabel(log_frame, text="Processing Details:", font=ctk.CTkFont(weight="bold"))
        self.log_label.pack(pady=5, padx=10, anchor="w")
        self.log_text = ctk.CTkTextbox(log_frame, state="disabled", wrap="word", font=("Courier New", 9))
        self.log_text.pack(pady=5, padx=10, fill="both", expand=True)

    def create_settings_tab_widgets(self):
        settings_frame = ctk.CTkFrame(self.settings_tab)
        settings_frame.pack(padx=20, pady=20, fill="x")

        ctk.CTkLabel(settings_frame, text="MKVToolNix Path Configuration", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(settings_frame, text="Please specify the location of 'mkvmerge.exe' on your system.", wraplength=500).pack(pady=5)

        path_frame = ctk.CTkFrame(settings_frame)
        path_frame.pack(fill="x", expand=True, pady=10)

        self.mkvmerge_path_entry = ctk.CTkEntry(path_frame, font=("Arial", 12), width=500)
        self.mkvmerge_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.mkvmerge_path_entry.insert(0, self.mkvmerge_path)


        browse_button = ctk.CTkButton(path_frame, text="Browse for mkvmerge.exe", command=self.select_mkvmerge_path)
        browse_button.pack(side="left")

    def create_processing_tab_widgets(self):
        # Header and Output Folder Selection
        header_frame = ctk.CTkFrame(self.processing_tab)
        header_frame.pack(pady=10, padx=10, fill="x")
        self.title_label = ctk.CTkLabel(header_frame, text="MKV Subtitle Embedder Tool", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)

        output_folder_frame = ctk.CTkFrame(self.processing_tab)
        output_folder_frame.pack(pady=5, padx=10, fill="x")
        self.btn_select_output = ctk.CTkButton(output_folder_frame, text="Select Output Folder", command=self.select_output_folder)
        self.btn_select_output.grid(row=0, column=0, pady=5, padx=10, sticky="w")
        self.lbl_output_folder = ctk.CTkLabel(output_folder_frame, text="Output Folder: Not selected", wraplength=500, justify="left")
        self.lbl_output_folder.grid(row=0, column=1, sticky="w", padx=5)
        output_folder_frame.grid_columnconfigure(1, weight=1)

        # Main Selection and Controls Frame
        selection_frame = ctk.CTkFrame(self.processing_tab)
        selection_frame.pack(pady=10, padx=10, fill="both", expand=True)
        selection_frame.grid_columnconfigure((0, 2), weight=1)
        selection_frame.grid_columnconfigure(1, weight=0)
        selection_frame.grid_rowconfigure(0, weight=1)

        # Video Column
        video_col_frame = ctk.CTkFrame(selection_frame)
        video_col_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(video_col_frame, text="Available Video Files:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.btn_select_videos = ctk.CTkButton(video_col_frame, text="Select Video Files", command=self.select_video_files)
        self.btn_select_videos.pack(pady=5)
        self.video_listbox = ctk.CTkTextbox(video_col_frame, wrap="word", state="disabled", font=("Courier New", 9))
        self.video_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.video_listbox.bind("<ButtonRelease-1>", lambda event: self.on_listbox_item_click(event, self.video_listbox, self.raw_video_files, 'video'))

        # Controls Column
        controls_col_frame = ctk.CTkFrame(selection_frame)
        controls_col_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ns")

        # --- NEW: Language Selection ---
        ctk.CTkLabel(controls_col_frame, text="Subtitle Language:", font=ctk.CTkFont(weight="bold")).pack(pady=(10,0))
        self.language_menu = ctk.CTkOptionMenu(controls_col_frame, values=list(self.language_map.keys()), variable=self.selected_language_code)
        self.language_menu.pack(pady=(5,20))

        ctk.CTkLabel(controls_col_frame, text="Pairing Actions", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.btn_pair_selected = ctk.CTkButton(controls_col_frame, text="Pair Selected Files >>", command=self.pair_selected_files, fg_color="#336699", hover_color="#2A537A")
        self.btn_pair_selected.pack(pady=10)
        self.btn_pair_all_auto = ctk.CTkButton(controls_col_frame, text="Pair All Automatically >>", command=self.pair_all_automatically, fg_color="#6A5ACD", hover_color="#5642B0")
        self.btn_pair_all_auto.pack(pady=10)
        self.btn_clear_lists = ctk.CTkButton(controls_col_frame, text="Clear All Selections", command=self.clear_all_selections, fg_color="#D32F2F", hover_color="#B71C1C")
        self.btn_clear_lists.pack(pady=10)

        # Subtitle Column
        subtitle_col_frame = ctk.CTkFrame(selection_frame)
        subtitle_col_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(subtitle_col_frame, text="Available Subtitle Files:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.btn_select_subtitles = ctk.CTkButton(subtitle_col_frame, text="Select Subtitle Files", command=self.select_subtitle_files)
        self.btn_select_subtitles.pack(pady=5)
        self.subtitle_listbox = ctk.CTkTextbox(subtitle_col_frame, wrap="word", state="disabled", font=("Courier New", 9))
        self.subtitle_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.subtitle_listbox.bind("<ButtonRelease-1>", lambda event: self.on_listbox_item_click(event, self.subtitle_listbox, self.raw_subtitle_files, 'subtitle'))

        # Paired Files List and Final Process Button
        bottom_frame = ctk.CTkFrame(self.processing_tab)
        bottom_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(bottom_frame, text="Paired Files (ID | Video File | Subtitle File | Status):", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.paired_list_text = ctk.CTkTextbox(bottom_frame, wrap="word", state="disabled", font=("Courier New", 10))
        self.paired_list_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.paired_list_text.bind("<ButtonRelease-1>", self.on_paired_list_click)

        control_buttons_frame = ctk.CTkFrame(bottom_frame)
        control_buttons_frame.pack(fill="x", pady=10)
        self.btn_remove_paired = ctk.CTkButton(control_buttons_frame, text="Remove Selected Pair", command=self.remove_selected_paired_entry, fg_color="#CC3300", hover_color="#A32900")
        self.btn_remove_paired.pack(side="left", padx=10)
        self.btn_start_process = ctk.CTkButton(control_buttons_frame, text="Start Subtitle Embedding", command=self.start_processing, fg_color="#4CAF50", hover_color="#368039", font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_start_process.pack(side="right", padx=10)


    def log_message(self, message, is_error=False, is_startup=False):
        if not hasattr(self, 'log_text') and not is_startup: return # Guard against logging before widget creation
        if is_startup and not hasattr(self, 'log_text'): return # Don't log startup if widgets aren't there

        self.log_text.configure(state="normal")
        if is_error:
            self.log_text.insert(tk.END, message + "\n", "error_tag")
            self.log_text.tag_config("error_tag", foreground="red")
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.master.update_idletasks()

    def start_processing(self):
        # ... (rest of the functions remain largely the same, but with updated mkvmerge command)
        if not self.paired_files:
            messagebox.showwarning("Error", "No video-subtitle pairs have been added for processing.")
            return
        if not self.output_folder:
            messagebox.showwarning("Error", "Please select an output folder.")
            return
        
        # --- NEW: Check for mkvmerge path
        if not os.path.exists(self.mkvmerge_path):
            messagebox.showerror("Error", f"'{os.path.basename(self.mkvmerge_path)}' not found at the specified path:\n{self.mkvmerge_path}\n\nPlease set the correct path in the Settings tab.")
            self.tabview.set("Settings") # Switch to settings tab
            return

        response = messagebox.askyesno(
            "Confirm Processing",
            f"Are you sure you want to start embedding subtitles for {len(self.paired_files)} files?"
        )
        if not response:
            self.log_message("Processing cancelled by user.")
            return

        os.makedirs(self.output_folder, exist_ok=True)
        self.log_message(f"\n--- Starting Subtitle Embedding Process ---")
        
        # --- MODIFIED: Get selected language
        lang_code = self.language_map.get(self.selected_language_code.get(), 'eng')
        self.log_message(f"Using subtitle language: {self.selected_language_code.get()} ({lang_code})")

        processed_count = 0
        for pair_id in sorted(self.paired_files.keys()):
            data = self.paired_files[pair_id]
            video_file_path = data['video']
            original_subtitle_path = data['subtitle']

            self.log_message(f"\nProcessing Pair ID {pair_id}:")
            # ... (log messages)

            output_filename = os.path.basename(video_file_path)
            output_file_path = os.path.join(self.output_folder, output_filename)

            # --- MODIFIED: Use configured path and language ---
            mkvmerge_command = [
                self.mkvmerge_path,
                "-o", output_file_path,
                "-S",
                video_file_path,
                "--language", f"0:{lang_code}",
                "--default-track", "0:yes",
                "--sub-charset", "0:cp1256",
                original_subtitle_path
            ]

            try:
                subprocess.run(mkvmerge_command, check=True, capture_output=True, text=True, encoding='utf-8')
                self.log_message(f"  Successfully processed Pair ID {pair_id}.")
                self.paired_files[pair_id]['status'] = 'success'
                processed_count += 1
            except subprocess.CalledProcessError as e:
                self.log_message(f"  Error running mkvmerge for Pair ID {pair_id}:", is_error=True)
                self.log_message(f"  stderr: {e.stderr.strip()}", is_error=True)
                self.log_message(f"  stdout: {e.stdout.strip()}")
                self.paired_files[pair_id]['status'] = 'failed'
            except FileNotFoundError:
                self.log_message(f"  Error: '{os.path.basename(self.mkvmerge_path)}' not found.", is_error=True)
                self.log_message(f"  Please set the correct path in the Settings tab.", is_error=True)
                messagebox.showerror("Error", f"'{os.path.basename(self.mkvmerge_path)}' not found. Please set the correct path in the Settings tab.")
                self.tabview.set("Settings")
                break
            except Exception as e:
                self.log_message(f"  Unknown error for Pair ID {pair_id}: {e}", is_error=True)
                self.paired_files[pair_id]['status'] = 'failed'
            
            self.display_paired_files()

        self.log_message(f"\n--- Processing Complete ---")
        self.log_message(f"{processed_count} files processed successfully.")
        messagebox.showinfo("Processing Complete", f"Processing complete. {processed_count} files processed successfully.")

    # --- All other helper functions (select_output_folder, on_listbox_item_click, etc.) remain the same ---
    # (The full code for these functions is omitted for brevity, but should be kept from your previous version)

    def update_listbox(self, listbox_widget, file_paths):
        listbox_widget.configure(state="normal")
        listbox_widget.delete(1.0, tk.END)
        if not file_paths:
            listbox_widget.insert(tk.END, "No files selected.")
        else:
            self.clear_listbox_highlights(listbox_widget)

            for idx, path in enumerate(file_paths):
                filename = os.path.basename(path)
                display_text = f"{idx+1}. {filename}"
                listbox_widget.insert(tk.END, display_text + "\n")
        listbox_widget.configure(state="disabled")

    def on_listbox_item_click(self, event, listbox_widget, raw_file_list, file_type_str):
        self.clear_listbox_highlights(listbox_widget)
        try:
            index = listbox_widget.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])
            list_index = line_num - 1
            if 0 <= list_index < len(raw_file_list):
                selected_path = raw_file_list[list_index]
                highlight_tag = f"highlight_{line_num}"
                listbox_widget.tag_add(highlight_tag, f"{line_num}.0", f"{line_num}.end")
                listbox_widget.tag_config(highlight_tag, background="gray20")
                if file_type_str == 'video':
                    self.selected_raw_video_path = selected_path
                    self.log_message(f"Selected Video: {os.path.basename(selected_path)}")
                elif file_type_str == 'subtitle':
                    self.selected_raw_subtitle_path = selected_path
                    self.log_message(f"Selected Subtitle: {os.path.basename(selected_path)}")
            else:
                self.selected_raw_video_path = None if file_type_str == 'video' else self.selected_raw_video_path
                self.selected_raw_subtitle_path = None if file_type_str == 'subtitle' else self.selected_raw_subtitle_path
        except tk.TclError:
            self.selected_raw_video_path = None if file_type_str == 'video' else self.selected_raw_video_path
            self.selected_raw_subtitle_path = None if file_type_str == 'subtitle' else self.selected_raw_subtitle_path

    def on_paired_list_click(self, event):
        self.clear_listbox_highlights(self.paired_list_text, prefix="paired_highlight_")
        try:
            index = self.paired_list_text.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])
            if line_num <= 2:
                self.selected_paired_id_for_removal = None
                return
            line_text = self.paired_list_text.get(f"{line_num}.0", f"{line_num}.end")
            match = re.match(r"(\S+)\s+\|", line_text)
            if match and match.group(1).isdigit():
                self.selected_paired_id_for_removal = int(match.group(1))
                self.log_message(f"Selected Pair ID for removal: {self.selected_paired_id_for_removal}")
                highlight_tag = f"paired_highlight_{line_num}"
                self.paired_list_text.tag_add(highlight_tag, f"{line_num}.0", f"{line_num}.end")
                self.paired_list_text.tag_config(highlight_tag, background="gray20")
            else:
                self.selected_paired_id_for_removal = None
        except tk.TclError:
            self.selected_paired_id_for_removal = None

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder = folder_selected
            self.lbl_output_folder.configure(text=f"Output Folder: {self.output_folder}")
            self.log_message(f"Output folder selected: {self.output_folder}")

    def select_video_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Video Files", filetypes=[("Video files", "*.mkv *.mp4 *.avi *.webm *.flv"), ("All files", "*.*")])
        if file_paths:
            self.raw_video_files.extend(list(file_paths))
            self.raw_video_files = sorted(list(set(self.raw_video_files)))
            self.update_listbox(self.video_listbox, self.raw_video_files)
            self.log_message(f"Selected {len(file_paths)} video files. Total unique videos: {len(self.raw_video_files)}")
            self.selected_raw_video_path = None

    def select_subtitle_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Subtitle Files", filetypes=[("Subtitle files", "*.ass *.srt *.sub *.idx"), ("All files", "*.*")])
        if file_paths:
            self.raw_subtitle_files.extend(list(file_paths))
            self.raw_subtitle_files = sorted(list(set(self.raw_subtitle_files)))
            self.update_listbox(self.subtitle_listbox, self.raw_subtitle_files)
            self.log_message(f"Selected {len(file_paths)} subtitle files. Total unique subtitles: {len(self.raw_subtitle_files)}")
            self.selected_raw_subtitle_path = None

    def clear_all_selections(self):
        if not self.raw_video_files and not self.raw_subtitle_files:
            messagebox.showinfo("Info", "Lists are already empty.")
            return
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear both the video and subtitle selection lists?"):
            self.raw_video_files.clear()
            self.raw_subtitle_files.clear()
            self.selected_raw_video_path = None
            self.selected_raw_subtitle_path = None
            self.update_listbox(self.video_listbox, self.raw_video_files)
            self.update_listbox(self.subtitle_listbox, self.raw_subtitle_files)
            self.clear_listbox_highlights(self.video_listbox)
            self.clear_listbox_highlights(self.subtitle_listbox)
            self.log_message("Video and subtitle selection lists have been cleared.")

    def pair_selected_files(self):
        if not self.selected_raw_video_path or not self.selected_raw_subtitle_path:
            messagebox.showwarning("Warning", "Please select one video file and one subtitle file to pair.")
            return
        self.paired_files[self.next_pair_id] = {'video': self.selected_raw_video_path, 'subtitle': self.selected_raw_subtitle_path, 'status': 'pending'}
        self.log_message(f"Paired ID {self.next_pair_id}: '{os.path.basename(self.selected_raw_video_path)}' with '{os.path.basename(self.selected_raw_subtitle_path)}'")
        self.next_pair_id += 1
        self.raw_video_files.remove(self.selected_raw_video_path)
        self.raw_subtitle_files.remove(self.selected_raw_subtitle_path)
        self.selected_raw_video_path = None
        self.selected_raw_subtitle_path = None
        self.update_listbox(self.video_listbox, self.raw_video_files)
        self.update_listbox(self.subtitle_listbox, self.raw_subtitle_files)
        self.display_paired_files()
        self.clear_listbox_highlights(self.video_listbox)
        self.clear_listbox_highlights(self.subtitle_listbox)

    def pair_all_automatically(self):
        if not self.raw_video_files or not self.raw_subtitle_files:
            messagebox.showwarning("Warning", "Video and/or subtitle lists are empty.")
            return
        if len(self.raw_video_files) != len(self.raw_subtitle_files):
            messagebox.showwarning("Warning", "File counts do not match. Manual pairing is recommended.")
        self.raw_video_files.sort()
        self.raw_subtitle_files.sort()
        for i in range(min(len(self.raw_video_files), len(self.raw_subtitle_files))):
            self.paired_files[self.next_pair_id] = {'video': self.raw_video_files[i], 'subtitle': self.raw_subtitle_files[i], 'status': 'pending'}
            self.log_message(f"Auto-Paired ID {self.next_pair_id}: '{os.path.basename(self.raw_video_files[i])}' with '{os.path.basename(self.raw_subtitle_files[i])}'")
            self.next_pair_id += 1
        self.raw_video_files.clear()
        self.raw_subtitle_files.clear()
        self.update_listbox(self.video_listbox, self.raw_video_files)
        self.update_listbox(self.subtitle_listbox, self.raw_subtitle_files)
        self.display_paired_files()

    def display_paired_files(self):
        self.paired_list_text.configure(state="normal")
        self.paired_list_text.delete(1.0, tk.END)
        if not self.paired_files:
            self.paired_list_text.insert(tk.END, "No pairs added yet.")
        else:
            self.clear_listbox_highlights(self.paired_list_text, prefix="paired_highlight_")
            self.paired_list_text.insert(tk.END, f"{'Pair ID':<10} | {'Video File':<50} | {'Subtitle File':<40} | {'Status'}\n")
            self.paired_list_text.insert(tk.END, "-" * 115 + "\n")
            for pair_id, data in sorted(self.paired_files.items()):
                video_name = os.path.basename(data.get('video', '---'))[:48]
                subtitle_name = os.path.basename(data.get('subtitle', '---'))[:38]
                status_icon = "⚪"
                if data['status'] == 'success': status_icon = "✅"
                elif data['status'] == 'failed': status_icon = "❌"
                self.paired_list_text.insert(tk.END, f"{pair_id:<10} | {video_name:<50} | {subtitle_name:<40} | {status_icon}\n")
        self.paired_list_text.configure(state="disabled")

    def remove_selected_paired_entry(self):
        if self.selected_paired_id_for_removal is None:
            messagebox.showwarning("Warning", "Please select a pair to remove.")
            return
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove Pair ID {self.selected_paired_id_for_removal}?"):
            removed_data = self.paired_files.pop(self.selected_paired_id_for_removal)
            self.raw_video_files.append(removed_data['video'])
            self.raw_subtitle_files.append(removed_data['subtitle'])
            self.raw_video_files.sort()
            self.raw_subtitle_files.sort()
            self.log_message(f"Pair ID {self.selected_paired_id_for_removal} removed.")
            self.update_listbox(self.video_listbox, self.raw_video_files)
            self.update_listbox(self.subtitle_listbox, self.raw_subtitle_files)
            self.display_paired_files()
            self.selected_paired_id_for_removal = None

    def clear_listbox_highlights(self, listbox_widget, prefix="highlight_"):
        for tag in listbox_widget.tag_names():
            if tag.startswith(prefix):
                listbox_widget.tag_delete(tag)

if __name__ == "__main__":
    root = ctk.CTk()
    app = SubtitleEmbedderApp(root)
    root.mainloop()
