## Anggota Kelompok 10
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Salwa Nadia Maharani | 5025241041 | Program Jaringan D |
| Naura Rossa Azalia | 5025241042 | Program Jaringan D |
---
## Link Youtube (Unlisted)

```
https://youtu.be/8HEx7fiEhNs
```
---
# **CoTask - Multi-Chat Room dengan Task Board**

Aplikasi chat berbasis jaringan dengan fitur manajemen task, dibangun menggunakan Python socket programming untuk Final Project Pemrograman Jaringan ITS 2025/2026.

---

## **Fitur**

- **Authentication** - Register dan login dengan password ter-hash (SHA-256)
- **Multi-Room Chat** - Buat, join, dan masuk ke banyak room sekaligus
- **Real-time Broadcast** - Pesan langsung muncul di semua client dalam room tanpa perlu refresh
- **Private Message** - Kirim pesan langsung ke user lain beserta notifikasi real-time
- **Chat History** - Riwayat pesan per room tersimpan
- **Task Board** - Buat, assign, update status, dan hapus task per room
- **Notifikasi Task** - Notifikasi otomatis saat di-assign task, task selesai, atau task dihapus
- **Online Users** - Lihat siapa saja yang sedang online
- **State Persistence** - Rooms, tasks, dan chat history tersimpan ke file JSON, tidak hilang saat server restart

---

## **Arsitektur Sistem**
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

## **Struktur File**

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

## **Cara Menjalankan**

### **Requirement**
- Python 3.8+
- Tidak ada library eksternal (semua bawaan Python)

### **1. Jalankan Server**
```bash
python server.py
```

### **2. Jalankan Client (buka terminal baru untuk setiap user)**
```bash
python client.py
```

### **3. Jalankan Load Test**
```bash
python load_test.py
```

---

## **Application Flow**
1. Authentication, wajib registrasi akun sebelum dapat menggunakan sistem
   `Register → Login → Masuk ke Menu Utama`
2. Room Management, 
   ```
   Menu Utama  ├── Create Room
               ├── Join Room
               └── Room List
   ```
3. Enter Room, setelah join ke suatu room, pengguna dapat enter room untuk menuju ke workspace room tersebut. Di dalam room, seluruh aktivitas chat dan task management dilakukan. 
4. Real-time Communication, Setiap room menyediakan fitur komunikasi antar anggota secara real-time.
```
Broadcast Message
        ↓
      Server
        ↓
Semua Member Room
```
Selain chat room, pengguna juga dapat mengirim pesan pribadi kepada pengguna lain.
```
  Private Message
        ↓
      Server
        ↓
    Target User
```
5. Task Management, setiap room memiliki task board yang digunakan untuk mengelola pekerjaan kelompok. Alur task management:
```
  Create Task
      ↓
  Assign Task
      ↓
    TODO
      ↓
  IN_PROGRESS
      ↓
    DONE
```
Hanya pengguna yang ditugaskan (assignee) yang dapat memperbarui status task.
6. Notification System, server secara otomatis mengirim notifikasi kepada pengguna ketika terjadi event tertentu.
```
    Assign Task
        ↓
Notification ke Assignee
```
```
      Task Selesai
          ↓
Notification ke Creator Task
```
```
    Private Message
        ↓
Notification ke Penerima
```

## **Desain Protokol**

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

### **Daftar Packet Type**

| **Type** | **Arah** | **Deskripsi** |
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

### **Contoh Packet**

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

## **Pengujian Beban**

Jalankan `load_test.py` untuk simulasi beban server:

```bash
python load_test.py
```

Setiap client yang disimulasikan akan melakukan langkah-langkah berikut:
- Terhubung ke server menggunakan TCP Socket.
- Melakukan proses register dan login.
- Bergabung ke room yang telah ditentukan.
- Mengirim sejumlah pesan broadcast ke room.
- Mengukur waktu yang dibutuhkan hingga server memberikan respons.

Pengujian menghasilkan beberapa metrik performa berikut:
- Success Rate: Persentase client yang berhasil menyelesaikan seluruh skenario tanpa error.
- Latency Minimum: Waktu respons tercepat yang tercatat.
- Latency Maximum: Waktu respons terlama yang tercatat.
- Average Latency: Rata-rata waktu respons seluruh request.
- Total Messages Processed: Jumlah pesan yang berhasil diproses server.

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
Total client  : 50
Berhasil      : 50
Gagal         : 0
Pesan/client  : 250
Total pesan   : 250
Throughput  : 370.70 msg/s

Latency:
  Min  : 0.06 ms
  Max  : 84.71 ms
  Avg  : 4.90 ms
==================================================
```

---

## **Konsep Jaringan yang Diterapkan**

| **Konsep** | **Implementasi** |
|--------|-------------|
| TCP Socket | `socket.AF_INET, socket.SOCK_STREAM` |
| Multithreading | `threading.Thread` per client di server |
| Concurrency | `threading.Thread` receiver + `queue.Queue` di client |
| Serialisasi | `json.dumps` / `json.loads` |
| Application Layer Protocol | Custom packet format berbasis JSON |
| Server Logging | Print log setiap event di server |
| State Persistence | `json.dump` ke `state.json` |
| Password Security | SHA-256 hash via `hashlib` |

