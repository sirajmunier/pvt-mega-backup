import subprocess 
import re 
import sys 
 
UNION_REMOTE_NAME = "mega_union" 
MOUNT_DRIVE_LETTER = "X:" 
 
def get_all_mega_remotes(): 
    try: 
        # List all rclone remotes 
        result = subprocess.run(['rclone', 'listremotes'], capture_output=True, text=True, check=True) 
        remotes = result.stdout.strip().splitlines() 
        # Filter remotes that start with "mega" and exclude mega_union 
        mega_remotes = [r.rstrip(':') for r in remotes if r.lower().startswith('mega') and r.lower() != 'mega_union:'] 
        if not mega_remotes: 
            print("❌ No Mega remotes found in rclone config.") 
            sys.exit(1) 
        print(f"Found Mega remotes: {mega_remotes}") 
        return mega_remotes 
    except subprocess.CalledProcessError as e: 
        print(f"❌ Error listing rclone remotes: {e}") 
        sys.exit(1) 
 
def create_union_remote(remotes): 
    # Each upstream should have a colon at the end, separated by spaces
    union_remotes_str = " ".join(f"{r.rstrip(':')}:" for r in remotes)
 
    print(f"Creating/Updating union remote '{UNION_REMOTE_NAME}' combining: {union_remotes_str}") 
    try: 
        subprocess.run([ 
            'rclone', 'config', 'create', UNION_REMOTE_NAME, 'union', 
            f'remotes={union_remotes_str}' 
        ], check=True) 
        print(f"✅ Union remote '{UNION_REMOTE_NAME}' created/updated successfully.") 
    except subprocess.CalledProcessError as e: 
        print(f"❌ Error creating union remote: {e}") 
        sys.exit(1) 
 
 
def mount_union_remote(): 
    print(f"Mounting '{UNION_REMOTE_NAME}:' to drive '{MOUNT_DRIVE_LETTER}'...") 
    try: 
        # rclone mount mega_union: X: --vfs-cache-mode writes 
        # Use --vfs-cache-mode writes for better compatibility with media playback 
        mount_cmd = [ 
            'rclone', 'mount', f'{UNION_REMOTE_NAME}:', MOUNT_DRIVE_LETTER, 
            '--vfs-cache-mode', 'writes',
            '--network-mode',  # Windows-specific flag for network drive
            '--volname', 'MegaUnion',  # Set volume name for Windows
            '--file-perms', '0777',  # Set file permissions
            '--dir-perms', '0777'    # Set directory permissions
        ] 
        # Run as a blocking process, so it keeps running until user stops it 
        print("Press Ctrl+C to unmount and exit.") 
        subprocess.run(mount_cmd) 
    except KeyboardInterrupt: 
        print("\nUnmount requested by user.") 
    except Exception as e: 
        print(f"❌ Error mounting union remote: {e}") 
 
def main(): 
    mega_remotes = get_all_mega_remotes() 
    create_union_remote(mega_remotes) 
    mount_union_remote() 
 
if __name__ == "__main__": 
    main()