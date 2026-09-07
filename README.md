# Portofolio ,  Umar Faiz Rahman

Website portofolio pribadi untuk mata kuliah Pemrograman Berbasis Platform (PBP), Fasilkom UI.
Saat ini halaman masih murni HTML5 + CSS3 yang disajikan lewat proyek Django.

**Bagian halaman**

- About Me ,  nama, NPM, foto, bio, dan tautan sosial.
- Skills ,  dibagi tiga kelompok (bahasa & framework, tools, sedang dipelajari) dengan indikator tingkat penguasaan.
- Pendidikan ,  timeline vertikal.
- Proyek ,  grid kartu proyek dengan filter kategori **tanpa JavaScript** (radio input + selector `:checked`).
- Pengalaman ,  daftar pengalaman organisasi/kepanitiaan.
- Penghargaan & sertifikasi
## Menjalankan proyek

```bash
git clone <url-repo-ini>
cd <nama-folder>
python -m venv env
source env/bin/activate        
pip install -r requirements.txt
python manage.py runserver
```

http://localhost:8000`

Struktur berkas:

```
templates/index.html
static/css/style.css
static/img/avatar.jpg
static/img/bg_web.gif
```

---

## Progres mingguan

Progres mingguan
Tugas 1

Yang dikerjakan

Mengganti data contoh di section About Me dengan data sendiri.
Mengubah tema halaman dari terang menjadi gelap, dengan palet yang diambil dari bg_web.gif yang dipakai sebagai latar hero.
Menambahkan empat section baru (Skills, Pendidikan, Proyek, Pengalaman), masing-masing dengan aturan CSS sendiri.
Menambahkan filter proyek berbasis CSS murni, animasi masuk di hero, dan dukungan prefers-reduced-motion.
Merapikan struktur style.css menjadi 11 blok bernomor dengan komentar.

Pertanyaan reflektif

Ya. Setiap bagian halaman dibungkus <section> dengan id dan aria-labelledby, setiap proyek adalah <article> karena bisa berdiri sendiri, riwayat pendidikan memakai <ol> karena urutannya bermakna, dan navigasi memakai <nav>. Manfaat yang paling terasa ada tiga. Pertama, CSS jadi lebih mudah ditulis dan dibaca karena selektor mengikuti struktur dokumen, misalnya .section-head cukup ditulis sekali dan berlaku untuk semua section. Kedua, anchor link di header (#skills, #projects, dst.) langsung bekerja tanpa perlu wrapper tambahan. Ketiga, halaman lebih terbaca oleh screen reader dan mesin pencari karena heading dan landmark-nya jelas. Kalau saya hanya memakai <div>, secara visual hasilnya sama, tetapi saya harus mengandalkan nama class untuk memahami struktur, dan itu lebih cepat berantakan saat section bertambah.
Tantangan terbesar ada di tiga tempat. (a) Hero: di desktop foto ada di kanan dan latar GIF di-mask dari kiri ke kanan supaya teks tetap terbaca; di mobile foto pindah ke antara judul dan detail, dan mask diubah menjadi atas ke bawah. Ini diselesaikan dengan grid-template-areas yang berbeda per breakpoint. (b) Timeline: kolom tanggal 160px di kiri tidak muat di layar sempit, jadi garis dan titik timeline dipindah ke sisi kiri dan tanggal ditaruh di atas judul. (c) Header: lima link navigasi tidak muat sebaris di 390px, jadi nav dibuat bisa di-scroll horizontal. Cara saya mengevaluasi: saya urutkan elemen berdasarkan informasi yang paling penting bagi pengunjung — nama, bio, dan tautan kontak harus terlihat dulu, foto boleh mengecil, sedangkan hiasan (latar GIF, blok warna di belakang foto) boleh dikurangi opasitasnya atau dihilangkan. Untuk ukuran, saya pakai clamp() pada judul dan padding section supaya skalanya mengikuti lebar layar tanpa terlalu banyak breakpoint, dan minmax(0, 1fr) di grid supaya kolom tidak meluap.
Batasan yang paling terasa: semua konten ditulis langsung di HTML, jadi menambah satu proyek berarti menyalin satu blok <article> dan mengedit manual, yang rawan salah dan tidak konsisten. Filter proyek berbasis CSS juga terbatas — hanya bisa satu kategori per proyek dan setiap kategori baru harus ditambahkan selektornya di CSS. Tidak ada cara untuk menampilkan data yang berubah (misalnya proyek terbaru dari GitHub) atau menerima input pengunjung. Untuk iterasi berikutnya, yang paling ingin saya siapkan adalah memindahkan proyek, skill, dan pengalaman ke model Django lalu merender kartunya lewat template loop, sehingga penambahan data cukup lewat admin. Setelah itu, form kontak sederhana yang menyimpan pesan ke database.

Refleksi proses

Masalah yang paling lama diselesaikan adalah membuat GIF latar menyatu dengan warna dasar tanpa menutupi teks. Percobaan pertama memakai opacity saja, hasilnya teks di sisi kiri tetap sulit dibaca. Solusi akhirnya adalah dua lapisan: mask-image gradient untuk memudarkan tepi GIF, ditambah pseudo-element ::after dengan gradient gelap di atasnya. Untuk memastikan responsif, halaman dicek di lebar 1280px dan 390px setiap kali ada perubahan layout.

---

## AI Disclosure

**Tools yang dipakai:** Claude (Anthropic), claude.ai.

**Bagian yang dibantu AI**

- Draft awal struktur HTML section Skills, Pendidikan, Proyek, dan Pengalaman.
- Draft awal CSS untuk tema gelap

**Strategi prompting:** saya memberikan `index.html` dan `style.css` hasil Tutorial 01, file GIF yang ingin dipakai sebagai latar, dan meminta agar memperbagus jika ada bagian yg masih kurang bagus.

**Perbaikan manual yang saya lakukan**

- Mengganti seluruh isi Skills, Pendidikan, Proyek, dan Pengalaman dengan data saya yang sebenarnya (draft AI berisi contoh yang perlu diverifikasi).
- Mengganti tautan GitHub/GitLab/proyek dengan tautan asli.
- Mengompres `bg_web.gif` (versi asli 16 MB) supaya halaman tidak berat.

**Keterbatasan AI yang saya temui:** AI tidak tahu data pribadi saya, jadi semua isi konten tetap harus saya tulis ulang. AI juga tidak bisa melihat hasil render di browser saya, sehingga pengecekan tampilan di berbagai ukuran layar tetap saya lakukan sendiri.

**Log percakapan:** 