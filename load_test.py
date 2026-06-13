import socket
import threading
import json
import time
import queue
from datetime import datetime

from protocol import *

HOST = "127.0.0.1"
PORT = 5000

JUMLAH_CLIENT = 10
PESAN_PER_CLIENT = 5
ROOM_NAME = "loadtest_room"

results = []
results_lock = threading.Lock()


def client_worker(client_id):
    username = f"loadtest_user_{client_id}"
    password = "password123"
    latencies = []

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.settimeout(10)

        # Register
        packet = create_packet(REGISTER, sender=username, data={"password": password})
        sock.send(serialize(packet).encode())
        sock.recv(4096)

        # Login
        packet = create_packet(LOGIN, sender=username, data={"password": password})
        sock.send(serialize(packet).encode())
        sock.recv(4096)

        # Join room
        packet = create_packet(JOIN_ROOM, sender=username, room=ROOM_NAME)
        sock.send(serialize(packet).encode())
        sock.recv(4096)

        # Kirim beberapa broadcast dan ukur latency
        for i in range(PESAN_PER_CLIENT):
            msg = f"Pesan {i+1} dari {username}"
            packet = create_packet(
                BROADCAST,
                sender=username,
                room=ROOM_NAME,
                data={"message": msg}
            )

            start = time.time()
            sock.send(serialize(packet).encode())

            # Baca semua response yang datang sampai dapat SUCCESS
            while True:
                try:
                    data = sock.recv(4096)
                    response = deserialize(data.decode())
                    if response["type"] in [SUCCESS, ERROR]:
                        break
                except:
                    break

            end = time.time()
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)

            time.sleep(0.1)

        sock.close()

        with results_lock:
            results.append({
                "client_id": client_id,
                "username": username,
                "latencies": latencies,
                "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
                "status": "OK"
            })

        print(f"[Client {client_id}] Selesai. Avg latency: {sum(latencies)/len(latencies):.2f} ms")

    except Exception as e:
        print(f"[Client {client_id}] ERROR: {e}")
        with results_lock:
            results.append({
                "client_id": client_id,
                "username": username,
                "latencies": latencies,
                "avg_latency": 0,
                "status": f"ERROR: {e}"
            })


def print_summary():
    print("\n" + "="*50)
    print("HASIL LOAD TEST")
    print("="*50)

    ok_results = [r for r in results if r["status"] == "OK"]
    error_results = [r for r in results if r["status"] != "OK"]

    all_latencies = []
    for r in ok_results:
        all_latencies.extend(r["latencies"])

    print(f"Total client  : {JUMLAH_CLIENT}")
    print(f"Berhasil      : {len(ok_results)}")
    print(f"Gagal         : {len(error_results)}")
    print(f"Pesan/client  : {PESAN_PER_CLIENT}")
    print(f"Total pesan   : {len(all_latencies)}")

    if all_latencies:
        print(f"\nLatency:")
        print(f"  Min  : {min(all_latencies):.2f} ms")
        print(f"  Max  : {max(all_latencies):.2f} ms")
        print(f"  Avg  : {sum(all_latencies)/len(all_latencies):.2f} ms")

    if error_results:
        print(f"\nError:")
        for r in error_results:
            print(f"  {r['username']}: {r['status']}")

    print("="*50)


def main():
    print(f"=== COTASK LOAD TEST ===")
    print(f"Target  : {HOST}:{PORT}")
    print(f"Clients : {JUMLAH_CLIENT}")
    print(f"Pesan   : {PESAN_PER_CLIENT} per client")
    print(f"Room    : {ROOM_NAME}")
    print("========================\n")

    # Buat room dulu pakai 1 client khusus
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.settimeout(5)

        packet = create_packet(REGISTER, sender="room_creator", data={"password": "admin123"})
        sock.send(serialize(packet).encode())
        sock.recv(4096)

        packet = create_packet(LOGIN, sender="room_creator", data={"password": "admin123"})
        sock.send(serialize(packet).encode())
        sock.recv(4096)

        packet = create_packet(CREATE_ROOM, sender="room_creator", room=ROOM_NAME)
        sock.send(serialize(packet).encode())
        sock.recv(4096)

        sock.close()
        print(f"[SETUP] Room '{ROOM_NAME}' siap.\n")
    except Exception as e:
        print(f"[SETUP] Room mungkin sudah ada: {e}\n")

    # Spawn semua client thread serentak
    threads = []
    start_time = time.time()

    for i in range(1, JUMLAH_CLIENT + 1):
        t = threading.Thread(target=client_worker, args=(i,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    total_time = time.time() - start_time
    print(f"\n[INFO] Total waktu: {total_time:.2f} detik")

    print_summary()


if __name__ == "__main__":
    main()