import csv
import subprocess

CSV_FILE = 'accounts.csv'  # Path to your CSV
REMOTE_PREFIX = 'mega'          # Resulting remotes will be mega1, mega2, mega3, ...

def create_rclone_remote(name, email, password):
    print(f"Creating rclone remote: {name}")
    try:
        subprocess.run([
            'rclone', 'config', 'create', name, 'mega',
            'user', email,
            'pass', password
        ], check=True)
        print(f"✅ Remote {name} created successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating remote {name}: {e}")

def main():
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, start=1):
            email = row['Email'].strip()
            password = row['MEGA Password'].strip()
            remote_name = f"{REMOTE_PREFIX}{i}"
            create_rclone_remote(remote_name, email, password)

if __name__ == '__main__':
    main()
