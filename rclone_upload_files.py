import subprocess
import os
import shutil
import json

# === CONFIGURATION ===
LOCAL_DOWNLOAD_FOLDER = r'C:\Users\HP\Downloads\Squid.Game.S03.720p.ITA-KOR-ENG.MULTI.WEBRip.x265.AAC-V3SP4EV3R'  # ✅ CHANGE THIS
UPLOAD_TARGET_FOLDER = 'torrent_uploads'            # Target folder inside Mega
MIN_FREE_SPACE_GB = 1                                # Add buffer for safe uploads

# === HELPERS ===

def get_mega_remotes():
    try:
        result = subprocess.run(
            ['rclone', 'config', 'dump'],
            capture_output=True, text=True, check=True
        )
        config = json.loads(result.stdout)
        mega_remotes = [name + ':' for name, details in config.items() if details.get('type') == 'mega']
        print(f"✅ Detected Mega remotes: {mega_remotes}")
        return mega_remotes
    except Exception as e:
        print(f"❌ Error reading rclone config: {e}")
        return []
def get_free_space_gb(remote):
    try:
        result = subprocess.run(
            ['rclone', 'about', remote],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if 'Free:' in line:
                free_str = line.split('Free:')[1].strip()
                if free_str.endswith('GiB'):
                    return float(free_str.replace('GiB', '').strip())
                elif free_str.endswith('G'):
                    return float(free_str.replace('G', '').strip())
                elif free_str.endswith('MiB'):
                    return float(free_str.replace('MiB', '').strip()) / 1024
                elif free_str.endswith('M'):
                    return float(free_str.replace('M', '').strip()) / 1024
                elif free_str.endswith('KiB'):
                    return float(free_str.replace('KiB', '').strip()) / (1024 * 1024)
                elif free_str.endswith('K'):
                    return float(free_str.replace('K', '').strip()) / (1024 * 1024)
                else:
                    # If no known suffix, try parsing as raw number
                    return float(free_str.split()[0])
        return 0.0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking free space on {remote}: {e}")
        return 0.0
    except Exception as e:
        print(f"❌ Unexpected error parsing free space on {remote}: {e}")
        return 0.0


def upload_file_to_mega(remote, local_file, remote_folder):
    remote_path = f"{remote}{remote_folder}"
    print(f"🚀 Uploading: {local_file} → {remote_path}/")
    try:
        subprocess.run(
            ['rclone', 'copyto', local_file, f"{remote_path}/{os.path.basename(local_file)}", '--progress'],
            check=True
        )
        print(f"✅ Uploaded: {local_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upload {local_file} to {remote}: {e}")
        return False

def delete_local_file(path):
    try:
        os.remove(path)
        print(f"🗑️ Deleted local file: {path}")
    except Exception as e:
        print(f"⚠️ Failed to delete file {path}: {e}")

def clean_empty_folders(base_folder):
    try:
        for root, dirs, _ in os.walk(base_folder, topdown=False):
            for d in dirs:
                dir_path = os.path.join(root, d)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
        print("🧹 Cleaned up empty folders.")
    except Exception as e:
        print(f"⚠️ Error cleaning folders: {e}")

# === MAIN ===

def main():
    mega_remotes = get_mega_remotes()
    if not mega_remotes:
        print("❌ No Mega remotes found. Exiting.")
        return

    # Gather all files to upload
    files_to_upload = []
    for dirpath, _, filenames in os.walk(LOCAL_DOWNLOAD_FOLDER):
        for f in filenames:
            files_to_upload.append(os.path.join(dirpath, f))

    if not files_to_upload:
        print("📁 No files to upload.")
        return

    remote_index = 0

    for file_path in files_to_upload:
        file_size_bytes = os.path.getsize(file_path)
        file_size_gb = file_size_bytes / (1024 ** 3)

        uploaded = False

        while remote_index < len(mega_remotes):
            remote = mega_remotes[remote_index]
            free_gb = get_free_space_gb(remote)
            print(f"📦 {remote} has {free_gb:.2f} GB free.")

            if free_gb > file_size_gb + MIN_FREE_SPACE_GB:
                success = upload_file_to_mega(remote, file_path, UPLOAD_TARGET_FOLDER)
                if success:
                    delete_local_file(file_path)
                    uploaded = True
                break
            else:
                print(f"⚠️ Not enough space on {remote}, trying next.")
                remote_index += 1

        if not uploaded:
            print(f"❌ No Mega remote could fit the file: {file_path}")
            break

    # Clean up empty folders after uploading
    clean_empty_folders(LOCAL_DOWNLOAD_FOLDER)

if __name__ == '__main__':
    main()
