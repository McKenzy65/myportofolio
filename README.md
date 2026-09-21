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


### Tugas 2

- yang dikerjakan:

1. menambahkan model `Certification` pada aplikasi `main` dgn field `title`, `description`, `year` dan `is_highlight`
2. membuat dan menerapkan migrasi model (`0002_certification.py`), include migrasi data (`0003_populate_certifications.py`) yg memindahkan 6 entri sertifikasi yg sebelumnya hard coded di `index.html` menjadi data pada database
3. membuat view `show_certifications` yg mengambil seluruh `Certification` dari database lalu meneruskannya sebagai context ke template baru
4. membuat page baru `templates/certifications.html` yg bisa diakses dari URL `/certifications/` (named route `main:show_certifications`), (terpisah dari halaman utama yang memuat bagian Pengalaman)
5. memindahkan section "Penghargaan & sertifikasi" dari `index.html` ke halaman barunya, lalu mengubah navbar pada kedua halaman agar memakai tag `{% url %}` supaya konsisten dan tidak ada tautan hardcoded
6. menambahkan tampilan kondisi kosong ("Belum ada data sertifikasi di database") ketika belom ada data `Certification`
7. menambahkan 5 unit test baru untuk `Certification`: URL dan template yang dipakai, pembuatan objek model, data muncul di halaman HTML, dan pesan kondisi kosong ketika data belum ada

- Pertanyaan reflektif

1. ketika pengguna membuka halaman `/certifications/`, browser mengirim HTTP request ke server Django. lalu `urls.py` milik proyek (`portofolio/urls.py`) menerima request tersebut lebih dulu dan lewat `include('main.urls')`, mendelegasikann pencocokan path ke `urls.py` milik aplikasi `main`. di `main/urls.py` path `certifications/` dicocokkan dengan named route `main:show_certifications` yg terhubung ke fungsi `show_certifications` di `main/views.py` view tersebut memanggil `Certification.objects.all()` buat ngambil semua baris tabel `Certification` lewat django ORM, sesuai skema yang didefinisikan di `main/models.py`, lalu memasukkan hasilnya ke dalam dict context dan memanggil `render(request, 'certifications.html', context)`. django mencari `certifications.html` di folder `templates/` (sesuai `TEMPLATES['DIRS']` pada `settings.py`), merender template tersebut dengan context yang diberikan, bagian `{% for cert in certification_list %}` melakukan looping pada queryset dan menyisipkan nilai tiap field ke HTML dan hasil akhirnya dikembalikan sebagai response HTML yg ditampilkan browser ke user

2. data sebaiknya disimpan di model, bukan dicode langsung di template, karna keduanya memisahkan tanggung jawab sesuai pola MVT(model mengurus struktur dan penyimpanan data) sedangkan template hanya mengurus cara data itu ditampilin. jika data hardcoded di HTML, menambah atau mengubah satu sertifikasi berarti mengedit kode dan mendeploy ulang aplikasi, sering typo dan gampang tidak konsisten antar entri karena disalin manual, jika data disimpen di model,, penambahan atau perubahan data cukup pakai django admin atau ORM tanpa menyentuh template maupun deployment ulang. strukturnya konsisten karna dihasilkan otomatis oleh satu blok loop template dan tipe datanya bisa divalidasi oleh django (misalnya `year` wajib berupa angka) aplikasi menajdi lebih mudah dimaintanance dan dikembangkan seiring bertambahnya data

3. `makemigrations` mengread perubahan yg dibuat pada `models.py` (menambah model baru, menambah/mengubah/menghapus field dan sebagainyaa) lalu menghasilkan berkas migrasi yg mendeskripsikan perubahan tersebut secara deklaratif, tanpa menyentuh database sama sekali

`migrate` memigrasi berkas2 tersebut secara berurutan utk make sure menerapkan perubahan tersebut (skema tabel, maupun perubahan data dari `RunPython`) ke database yg sedang dipakai, contoh pada tugas ini: menambahkan model `Certification` mengharuskan `makemigrations` dijalankan lebih dulu utk menghasilkan `0002_certification.py`, lalu `migrate` dijalankan supaya tabel `main_certification` benar2 dibuat di `db.sqlite3`. contoh lain, migrasi data `0003_populate_certifications.py` yang memindahkan 6 sertifikasi hard coded ke database juga baru benar2 mengisi datanya setelah `migrate` dijalankan

______________________________________________________________________________________________________________
### Tugas 3

yang dikerjakan:

1. membuat template dasar `templates/base.html` (head, navbar, footer, `{% block meta %}` dan `{% block content %}`), terus me refactor `index.html`, `certifications.html`, `certification_form.html` agar memakai `{% extends 'base.html' %}` sehingga tdk ada kode header/footer yg berulang
2. membuat `CertificationForm` (`ModelForm`) di `main/forms.py` dgn empat field: `title` (CharField), `description` (TextField), `year` (PositiveIntegerField), dan `is_highlight` (BooleanField)
3. membuat view `create_certification` (form tambah data), `edit_certification` (form ubah data memakai `instance=`), `delete_certification` (hapus data dari POST), disertai dgn named route masing2
4. membuat view `get_certifications_json` yg meng return data sertifikasi dalam format JSON (`/api/certifications/`) dan mendukung filter `?title=`
5. mengubah `show_certifications` agar mengambil data melalui `get_certifications_json`, meng deserialisasi, lalu menampilkannya di template, ditambah kotak pencarian based on judul
6. membuat UI: halaman form tambah/ubah (`certification_form.html` dipake bersama), tombol "Tambah Sertifikasi", tombol "Edit", tombol "Hapus" dengan modal konfirmasi (`components/certification_delete_modal.html`) berbasis atribut `popover`
7. menambahkan `CSRF_TRUSTED_ORIGINS` untuk domain PWS di `settings.py`

Pertanyaan reflektif

1. `ModelForm` dipake karna django membuat field form, label, tipe input, dan validasi langsung dari definisi model. Kalau membuat form HTML manual, setiap field harus ditulis ulang dan validasinya (misalnya `year` harus angka, `title` maksimal 255 karakter) harus dibuat sendiri, sehingga mudah tidak sinkron ketika model berubah. Dengan `ModelForm`, `form.is_valid()` memvalidasi input, `form.save()` menyimpan ke database, dan `instance=` membuat form yang sama bisa dipakai untuk mengubah data yang sudah ada. `{% csrf_token %}` diwajibkan karena form POST rentan terhadap serangan CSRF (Cross-Site Request Forgery), yaitu situs lain yang diam-diam membuat browser pengguna yang sedang login mengirim request ke server kita. Django membuat token rahasia yang unik per sesi dan menyisipkannya ke form, lalu server mencocokkannya saat request masuk. Request tanpa token yang cocok ditolak (403), sehingga hanya form yang benar-benar berasal dari halaman kita yang diterima.

2. JSON lebih disukai karena lebih ringkas: XML mengulang nama tag pembuka dan penutup untuk setiap elemen sehingga ukurannya lebih besar, sedangkan JSON hanya memakai pasangan key-value dan array. JSON juga lebih cepat di-parse dan cocok langsung dengan struktur data di kebanyakan bahasa (objek/dictionary dan list), termasuk JavaScript di sisi frontend yang bisa memakainya lewat `JSON.parse` atau `fetch()` tanpa parser tambahan. JSON punya tipe data dasar (string, number, boolean, null), dan tetap mudah dibaca manusia. XML masih dipakai pada sistem lama dan enterprise, tetapi untuk REST API modern JSON menjadi pilihan utama.

3. Saat browser membuka `/api/certifications/`, request diterima `portofolio/urls.py`, diteruskan lewat `include('main.urls')` ke `main/urls.py`, lalu dicocokkan ke `get_certifications_json`. View membaca parameter `title` dari `request.GET`, mengambil data lewat `Certification.objects.all()` (difilter dengan `title__icontains` jika ada query), lalu memanggil `serializers.serialize("json", certifications)` dan mengembalikannya dengan `HttpResponse(..., content_type="application/json")`. Serialization diperlukan karena `QuerySet` dan objek model adalah objek Python di memori, sedangkan HTTP hanya mengirim teks/byte. Objek itu harus diubah dulu ke format teks standar (JSON) yang berisi `model`, `pk`, dan `fields` agar bisa dikirim dan dibaca oleh client atau sistem lain. Di `show_certifications`, hasil JSON tersebut dideserialisasi kembali (`serializers.deserialize`) menjadi objek Python untuk dirender oleh template.

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

Log percakapan:

### Tugas 2

Tools yang dipakai: Claude Code (Claude Sonnet 5, Anthropic).

Bagian yang dibantu AI

1. Penulisan unit test untuk `Certification`

Strategi prompting: saya mmeminta AI membaca struktur proyek portofolio yang sudah ada (hasil Tutorial 02) untuk membuatkan unit test yang benar dan best practice

Perbaikan serta verifikasi manual yang saya lakukan

1. implementasi model `Certification`, migrasi (includee migrasi data), view `show_certifications`, URL dan template `certifications.html`, mengikuti pola MVT yang sudah ada pada `Experience` di Tutorial 02
2. pemindahan section "Penghargaan & sertifikasi" dari `index.html` ke page baru, dan penyesuaian navbar di kedua page agar memakai tag `{% url %}`
3. penulisan draf awal jawaban pertanyaan reflektif di atas
4. menjalankan `python manage.py test` dan `python manage.py runserver` utk memastikan seluruh test passed dan berhasil dan kedua halaman (utama, sertifikasi) bener2 muncul dengan data yg sesuai di browser
5. meninjau ulang (me-make sure) isi migrasi data agar 6 sertifikasi yg dipindah sama persis dengan yg sebelumnya ada di `index.html`

Keterbatasan AI yang saya temui: AI perlu diarahkan untuk memperbaiki satu unit test yang gagal karena migrasi data mengisi database test dengan data awal, sehingga kondisi "kosong" harus dites dengan menghapus data lebih dulu

### Tugas 3

Tools yang dipakai: Claude Code (Claude Sonnet 5, Anthropic).

Bagian yang dibantu AI

1. Penjelasan materi Tutorial 03 (skeleton template, `ModelForm`, CSRF, serialize/deserialize JSON) dalam bahasa yang lebih mudah dipahami
2. Pemecahan Tutorial 03 dan Tugas 3 menjadi beberapa langkah/commit, beserta contoh kode yang disesuaikan ke model `Certification` (`base.html`, `forms.py`, view create/edit/delete/JSON, template form, modal hapus, dan CSS pendukung)
3. Pengecekan kode saya terhadap PDF tutorial dan checklist tugas, serta penambahan fitur update, tombol tambah/edit, dan CSS terkait pada tahap akhir

Strategi prompting: saya memberikan PDF Tutorial 03 dan Tugas 3, meminta AI menjelaskan materi terlebih dahulu, lalu meminta panduan per commit (saya yang mengetik, menjalankan, dan melakukan commit sendiri). Setiap langkah saya minta dicek ulang terhadap PDF, dan saya meminta AI membaca file proyek untuk memverifikasi hasil edit saya.

Perbaikan serta verifikasi manual yang saya lakukan

1. mengetik dan menyesuaikan kode ke struktur proyek saya sendiri, termasuk view `edit_certification` dan routing-nya
2. menjalankan `python manage.py runserver` dan mencoba fitur tambah, ubah, hapus, pencarian, dan endpoint `/api/certifications/` langsung di browser
3. memperbaiki error yang muncul sendiri: `ModuleNotFoundError: dotenv` karena venv belum aktif, `TemplateSyntaxError` karena sisa `<!DOCTYPE>` sebelum `{% extends %}`, folder `components/` yang salah letak, import yang belum ditambahkan di `main/urls.py`, variabel `Certification` yang menimpa nama model di `delete_certification`, dan CSS yang tertahan cache browser
4. me-refactor `index.html` agar memakai `base.html`, menghapus fungsi `show_certifications` yang terduplikasi, dan meninjau ulang agar struktur kode mengikuti PDF
5. melakukan commit secara bertahap dengan pesan yang deskriptif

Keterbatasan AI yang saya temui: instruksi AI sempat tidak sinkron dengan PDF (misalnya struktur modal hapus yang keliru pada percobaan pertama) dan beberapa langkah tidak menyebutkan detail yang membuat error, seperti `{% load static %}` yang harus ditulis ulang di template turunan. AI juga tidak bisa menjalankan klik/submit form di browser saya, sehingga pengujian alur tambah, ubah, hapus tetap saya lakukan sendiri.


