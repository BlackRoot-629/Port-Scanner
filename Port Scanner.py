import socket
import argparse

parser = argparse.ArgumentParser(description="Simple Port Scanner")
parser.add_argument("target", help="Target IP address or domain")
parser.add_argument("-s", "--start", type=int, default=1, help="Start port")
parser.add_argument("-e", "--end", type=int, default=1024, help="End port")

args = parser.parse_args()

# تبدیل دامنه به IP در صورت نیاز
try:
    target_ip = socket.gethostbyname(args.target)
except socket.gaierror:
    print("Invalid domain or IP")
    exit()

print(f"\nScanning {args.target} ({target_ip})...\n")

for port in range(args.start, args.end + 1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex((target_ip, port))
    if result == 0:
        print(f"Port {port} is open")
    s.close()

print("\nScan complete.")