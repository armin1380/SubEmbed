SubEmbed

A user-friendly desktop application for easily embedding subtitle files (.srt, .ass, etc.) into video files (.mkv, .mp4). This tool is designed for batch processing and handles various languages and text encodings gracefully.

<img width="1920" height="1040" alt="image" src="https://github.com/user-attachments/assets/6ccfdd1c-5c55-41fa-8b8e-5e7b2c5a86a9" />

## Features
Modern GUI: Built with CustomTkinter for a clean, modern look and feel.

Batch Processing: Queue up and process multiple video-subtitle pairs at once.

Flexible File Pairing:

Pair video and subtitle files manually for precise control.

Automatically pair all loaded files based on sorted file names.

Multi-Language Support: Tag subtitle tracks with the correct language, with built-in options for Persian, English, French, Spanish, Portuguese, and Hebrew.

Encoding Detection: Correctly handles legacy text encodings (like cp1256 for Persian/Arabic subtitles) to prevent garbled text (e.g., `` or ÑÇÏíÑ).

Portable Configuration: No need to add MKVToolNix to your system's PATH. Simply point the app to your mkvmerge.exe file via the settings.

Persistent Settings: Your mkvmerge.exe path is saved locally in a config.json file for convenience.

## Installation & Usage
There are two ways to use this application: by downloading the pre-built executable or by running the source code directly.
Notice you need to have MKVtoolnix for this. You can find the latest version here: https://mkvtoolnix.download/downloads.html
### For End-Users (Recommended)
This is the easiest way to get started.

Go to the Releases page of this repository.

Download the .zip file from the latest release (e.g., SubEmbed_v1.0.zip).

Unzip the file to a folder on your computer.

Run the SubtitleEmbedder.exe file.

On the first run, go to the Settings tab, click "Browse," and select the mkvmerge.exe file from your MKVToolNix installation directory. This setting will be saved automatically.

### For Developers (Running from Source)
If you have Python installed and want to run the code directly:

Clone the repository:
```
git clone https://github.com/armin1380/SubEmbed.git
cd YourRepositoryName
```
Install the required libraries:
Bash
```
pip install customtkinter
Run the application:
```
Bash
```
python gen.py
```
(Note: You will still need to set the path to mkvmerge.exe in the Settings tab.)

## Building from Source
If you want to compile the executable (.exe) yourself:

Make sure you have all the necessary libraries installed, including PyInstaller:

Bash
```
pip install customtkinter pyinstaller
```
Navigate to the project directory in your terminal.
Run the pyinstaller command. The following command is recommended for creating a clean, single-file executable with a custom name and icon:

Bash
```
pyinstaller --onefile --windowed --name "SubtitleEmbedder" --icon="path/to/your/icon.ico" gen.py
```
--onefile: Bundles everything into a single .exe.

--windowed: Prevents a console window from opening in the background.

The final executable will be located in the dist folder.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
