# CoTask — Multi-Chat Room dengan Task Board

Aplikasi chat berbasis jaringan dengan fitur manajemen task, dibangun menggunakan Python socket programming untuk Final Project Pemrograman Jaringan ITS 2025/2026.

---

## Fitur

- **Authentication** — Register dan login dengan password ter-hash (SHA-256)
- **Multi-Room Chat** — Buat, join, dan masuk ke banyak room sekaligus
- **Real-time Broadcast** — Pesan langsung muncul di semua client dalam room tanpa perlu refresh
- **Private Message** — Kirim pesan langsung ke user lain beserta notifikasi real-time
- **Chat History** — Riwayat pesan per room tersimpan
- **Task Board** — Buat, assign, update status, dan hapus task per room
- **Notifikasi Task** — Notifikasi otomatis saat di-assign task, task selesai, atau task dihapus
- **Online Users** — Lihat siapa saja yang sedang online
- **State Persistence** — Rooms, tasks, dan chat history tersimpan ke file JSON, tidak hilang saat server restart

---

## Arsitektur Sistem

```
┌─────────────┐         TCP Socket          ┌─────────────────┐
│   Client 1  │ ◄─────────────────────────► │                 │
├─────────────┤                             │                 │
│   Client 2  │ ◄─────────────────────────► │   SERVER        │
├─────────────┤                             │  (Multithreaded)│
│   Client 3  │ ◄─────────────────────────► │                 │
└─────────────┘                             └─────────────────┘
                                                     │
                                            ┌────────┴────────┐
                                            │   Penyimpanan   │
                                            │  users.json     │
                                            │  state.json     │
                                            └─────────────────┘
```

- Setiap client yang connect ditangani oleh **thread terpisah** di server
- Client menggunakan **background receiver thread** + **response_queue** untuk memisahkan broadcast real-time dari response command
- Semua komunikasi menggunakan **serialisasi JSON**

---

## Struktur File

```
cotask/
├── server.py         # Server utama, handler semua packet
├── client.py         # Client CLI interaktif
├── protocol.py       # Definisi packet type dan fungsi serialisasi
├── server_state.py   # State global server (rooms, tasks, dll)
├── load_test.py      # Script pengujian beban server
├── users.json        # Data user (auto-generated)
├── state.json        # State rooms & tasks (auto-generated)
└── README.md
```

---

## Cara Menjalankan

### Requirement
- Python 3.8+
- Tidak ada library eksternal (semua bawaan Python)

### 1. Jalankan Server
```bash
python server.py
```

### 2. Jalankan Client (buka terminal baru untuk setiap user)
```bash
python client.py
```

### 3. Jalankan Load Test
```bash
python load_test.py
```

---

## Desain Protokol

Semua komunikasi menggunakan format JSON dengan struktur berikut:

```json
{
    "type": "TIPE_PACKET",
    "sender": "username",
    "room": "nama_room",
    "timestamp": "2026-06-13 10:00:00",
    "data": {}
}
```

### Daftar Packet Type

| Type | Arah | Deskripsi |
|------|------|-----------|
| `REGISTER` | Client → Server | Daftar akun baru |
| `LOGIN` | Client → Server | Masuk ke sistem |
| `CREATE_ROOM` | Client → Server | Buat room baru |
| `JOIN_ROOM` | Client → Server | Bergabung ke room |
| `ENTER_ROOM` | Client → Server | Masuk ke room yang sudah di-join |
| `LEAVE_ROOM` | Client → Server | Keluar dari room |
| `ROOM_LIST` | Client → Server | Minta daftar room |
| `BROADCAST` | Client → Server | Kirim pesan ke room |
| `BROADCAST` | Server → Client | Push pesan real-time ke semua member |
| `PRIVATE_MESSAGE` | Client → Server | Kirim pesan privat |
| `GET_PRIVATE_MESSAGES` | Client → Server | Ambil pesan privat masuk |
| `ONLINE_USERS` | Client → Server | Minta daftar user online |
| `GET_HISTORY` | Client → Server | Ambil riwayat chat room |
| `CREATE_TASK` | Client → Server | Buat task baru di room |
| `TASK_BOARD` | Client → Server | Ambil daftar task room |
| `ASSIGN_TASK` | Client → Server | Assign task ke user |
| `UPDATE_TASK` | Client → Server | Update status task |
| `DELETE_TASK` | Client → Server | Hapus task |
| `TASK_NOTIFICATION` | Server → Client | Push notifikasi task real-time |
| `SUCCESS` | Server → Client | Response berhasil |
| `ERROR` | Server → Client | Response gagal |
| `PING` | Client → Server | Cek koneksi |
| `PONG` | Server → Client | Balas ping |

---

### Contoh Packet

**Register:**
```json
{
    "type": "REGISTER",
    "sender": "naura",
    "room": "",
    "timestamp": "2026-06-13 10:00:00",
    "data": {
        "password": "mypassword"
    }
}
```

**Broadcast (Client → Server):**
```json
{
    "type": "BROADCAST",
    "sender": "naura",
    "room": "project-room",
    "timestamp": "2026-06-13 10:05:00",
    "data": {
        "message": "Halo semua!"
    }
}
```

**Create Task:**
```json
{
    "type": "CREATE_TASK",
    "sender": "naura",
    "room": "project-room",
    "timestamp": "2026-06-13 10:10:00",
    "data": {
        "title": "Implementasi fitur login"
    }
}
```

**Assign Task:**
```json
{
    "type": "ASSIGN_TASK",
    "sender": "naura",
    "room": "project-room",
    "timestamp": "2026-06-13 10:11:00",
    "data": {
        "task_id": 1,
        "assignee": "ais"
    }
}
```

**Update Task:**
```json
{
    "type": "UPDATE_TASK",
    "sender": "ais",
    "room": "project-room",
    "timestamp": "2026-06-13 10:15:00",
    "data": {
        "task_id": 1,
        "status": "IN_PROGRESS"
    }
}
```

**Success Response:**
```json
{
    "type": "SUCCESS",
    "sender": "",
    "room": "",
    "timestamp": "2026-06-13 10:15:01",
    "data": {
        "message": "Task updated"
    }
}
```

**Task Notification (Server → Client, push):**
```json
{
    "type": "TASK_NOTIFICATION",
    "sender": "",
    "room": "",
    "timestamp": "2026-06-13 10:15:01",
    "data": {
        "message": "You have been assigned task: Implementasi fitur login"
    }
}
```

---

## Mekanisme Real-time

Client menggunakan dua jalur terpisah untuk menghindari tabrakan antara response command dan push dari server:

```
Socket ──► receiver_thread ──► BROADCAST/NOTIFICATION  ──► print langsung
                          └──► response lainnya         ──► response_queue
                                                               │
send_packet() ──────────────────────────────────────────────► queue.get()
```

- **receiver_thread** berjalan terus di background setelah login
- Packet bertipe `BROADCAST` dan `TASK_NOTIFICATION` langsung di-print
- Packet lain (response command) dimasukkan ke `response_queue`
- `send_packet()` mengambil response dari queue, bukan langsung dari socket

---

## Pengujian Beban

Jalankan `load_test.py` untuk simulasi beban server:

```bash
python load_test.py
```

Script ini akan:
- Spawn **10 client** secara bersamaan
- Setiap client **register → login → join room → kirim 5 broadcast**
- Mengukur **latency** tiap pesan
- Menampilkan statistik: min, max, average latency

Contoh output:
```
=== COTASK LOAD TEST ===
Clients : 10
Pesan   : 5 per client
========================

[Client 1] Selesai. Avg latency: 2.45 ms
[Client 2] Selesai. Avg latency: 3.12 ms
...

==================================================
HASIL LOAD TEST
==================================================
Total client  : 10
Berhasil      : 10
Gagal         : 0
Total pesan   : 50

Latency:
  Min  : 1.23 ms
  Max  : 8.45 ms
  Avg  : 3.21 ms
==================================================
```

---

## Konsep Jaringan yang Diterapkan

| Konsep | Implementasi |
|--------|-------------|
| TCP Socket | `socket.AF_INET, socket.SOCK_STREAM` |
| Multithreading | `threading.Thread` per client di server |
| Concurrency | `threading.Thread` receiver + `queue.Queue` di client |
| Serialisasi | `json.dumps` / `json.loads` |
| Application Layer Protocol | Custom packet format berbasis JSON |
| Server Logging | Print log setiap event di server |
| State Persistence | `json.dump` ke `state.json` |
| Password Security | SHA-256 hash via `hashlib` |

