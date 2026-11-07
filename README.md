# Portofolio, Umar Faiz Rahman

Website portofolio pribadi untuk mata kuliah Pemrograman Berbasis Platform (PBP), Fasilkom UI.
Dibangun dengan Django (MVT), dikembangkan bertahap setiap minggu mengikuti tutorial dan tugas.

- Repositori: https://github.com/McKenzy65/myportofolio
- Situs (PWS): https://umar-faiz-myportofolio.pws.cs.ui.ac.id

## Fitur

- **Halaman utama (`/`)**: About Me, Skills, Pendidikan, Proyek (filter kategori tanpa JavaScript), dan Pengalaman yang diambil dari database.
- **Sertifikasi (`/certifications/`)**: daftar, pencarian dengan debounce 300 ms, tambah, edit, star, dan hapus memakai API DRF tanpa reload. Tersedia kondisi loading, kosong, error, modal, dan konfirmasi hapus.
- **Pengalaman (`/#experience`)**: model `Experience` yang sudah ada dilengkapi API DRF, pencarian judul, filter kategori, modal tambah/edit, dan star sesuai akun yang sedang login.
- **Template dasar (`templates/base.html`)**: header, footer, dan kerangka HTML dipakai bersama lewat `{% extends %}`.
- **Data delivery JSON**: data sertifikasi dan pengalaman tersedia sebagai JSON.
- **Flash message** setelah tambah, ubah, atau hapus data, dan **mode gelap/terang** (`static/js/theme.js`).
- **Toast** untuk hasil penambahan AJAX, kesalahan validasi, dan kegagalan memuat daftar.
- **Hak akses**: semua pengunjung dapat membaca; pengguna login dapat memberi/membatalkan star; grup `Editor` dapat mengedit; superuser dapat menambah, mengedit, dan menghapus.
- **Perlindungan input**: permintaan yang mengubah data memakai session dan CSRF, teks dibersihkan dengan `strip_tags` pada form/serializer, dan nilai dari JSON ditampilkan lewat escaping atau `textContent`.
- **Eksplorasi sertifikasi**: filter tahun, unggulan, dan favorit pribadi dapat digabungkan dengan pencarian; urutkan terbaru, terlama, judul, atau star terbanyak. Jumlah hasil, reset filter, dan tombol coba lagi membantu menemukan data.
- **Star tanpa reload**: pengguna login dapat memberi/membatalkan star lewat Fetch API; daftar diperbarui sambil mempertahankan pencarian dan filter.
- **Tampilan akun**: login dan registrasi memakai layout dua panel di desktop dan satu kolom di mobile, field konsisten dengan tema, tombol lihat/sembunyikan kata sandi, serta pesan validasi di dekat field. Kedua halaman menggunakan komponen form bersama.

## Endpoint

| URL | Method | Fungsi |
|---|---|---|
| `/api/v1/certifications/` | GET, POST | Daftar/tambah sertifikasi; filter `title`, `year`, `highlight=1`, `starred=1`, dan `sort=newest/oldest/title/popular` |
| `/api/v1/certifications/<int:id>/` | GET, PUT, PATCH, DELETE | Detail, ubah, dan hapus sertifikasi |
| `/api/v1/certifications/<int:id>/star/` | POST | Toggle star sertifikasi untuk `request.user` |
| `/api/v1/experiences/` | GET, POST | Daftar/tambah pengalaman; filter `title` dan `category` |
| `/api/v1/experiences/<uuid:id>/` | GET, PUT, PATCH, DELETE | Detail, ubah, dan hapus pengalaman |
| `/api/v1/experiences/<uuid:id>/star/` | POST | Toggle star pengalaman untuk `request.user` |
| `/api-auth/login/` | GET, POST | Login session untuk Browsable API |
| `/` | GET | Halaman utama |
| `/certifications/` | GET | Daftar sertifikasi, mendukung `?title=` |
| `/certifications/add/` | GET, POST | Form tambah sertifikasi |
| `/certifications/add-ajax/` | POST | Tambah sertifikasi via AJAX, khusus superuser; JSON 201/400/403 |
| `/certifications/<id>/edit/` | GET, POST | Form ubah sertifikasi |
| `/certifications/<id>/delete/` | POST | Hapus sertifikasi |
| `/api/certifications/` | GET | Sertifikasi dalam JSON; parameter `title`, `year`, `highlight=1`, `starred=1` (wajib login), `sort=newest/oldest/title/popular` |
| `/api/experiences/` | GET | Pengalaman dalam JSON, mendukung `?category=` |
| `/certifications/<id>/star/` | POST | Memberi/membatalkan star, wajib login; JSON jika header Accept berisi application/json |
| `/register/` | GET, POST | Registrasi pengguna |
| `/login/` | GET, POST | Login pengguna |
| `/logout/` | GET | Logout pengguna |

Endpoint `/api/v1/` mengembalikan objek datar dengan `id`, field model yang dipilih, `star_count`, dan `is_starred`. Endpoint JSON lama `/api/certifications/` dan `/api/experiences/` dipertahankan untuk kompatibilitas; halaman memakai API DRF baru.

## Menjalankan proyek

```powershell
git clone https://github.com/McKenzy65/myportofolio.git
cd myportofolio
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Pada macOS/Linux, aktivasi environment memakai `source env/bin/activate`. Jalankan perintah dari folder yang berisi `manage.py`. Jika aktivasi PowerShell dibatasi, gunakan `env\Scripts\python.exe` sebagai pengganti `python` tanpa mengubah execution policy.

Buka http://localhost:8000. Untuk unit test jalankan `python manage.py test main`, agar skrip Selenium `test_e2e.py` di root tidak ikut dimuat. Dependency DRF dicatat di `requirements.txt`. Setelah menarik perubahan model, jalankan `python manage.py migrate` sebelum menyalakan server.

Untuk mencoba empat peran, buat pemilik lewat `python manage.py createsuperuser`; buat akun biasa lewat `/register/`, lalu tambahkan akun Editor ke Django Group bernama tepat `Editor` melalui admin. `is_staff` saja tidak memberi hak mengelola data portofolio.

Pengembangan lokal tidak memerlukan berkas `.env`: secara bawaan `PRODUCTION=False` sehingga memakai SQLite.
Untuk produksi (PostgreSQL) atur `PRODUCTION=True` beserta `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, dan `SCHEMA` lewat environment variable.

## Struktur berkas

```
main/
    models.py       # Experience, Certification
    forms.py        # CertificationForm (ModelForm)
    views.py        # view halaman, form, dan JSON
    urls.py         # routing aplikasi (namespace "main")
    serializers.py  # CertificationSerializer dan ExperienceSerializer
    permissions.py  # aturan akses pengunjung, pengguna, Editor, pemilik
    api_views.py    # function-based view DRF dan SessionAuthentication
    api_urls.py     # endpoint /api/v1/, namespace "api"
    tests.py        # unit test
    tests_api*.py   # pengujian API sertifikasi dan session/CSRF
    tests_experience_api.py  # pengujian API pengalaman
    tests_assignment6.py     # regresi halaman, CSRF, dan jalur lama
    migrations/
portofolio/         # konfigurasi proyek (settings.py, urls.py)
templates/
    base.html
    index.html
    certifications.html
    certification_form.html   # dipakai untuk tambah dan ubah
    components/certification_delete_modal.html
    components/certification_form_modal.html
    components/certification_edit_modal.html
    components/experience_section.html
    components/toast.html
static/
    css/style.css
    css/experiences.css
    js/theme.js
    js/toast.js
    js/experiences.js
    img/
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

### Tugas 4

yang dikerjakan:

1. menambahkan autentikasi bawaan Django: `register` (`UserCreationForm`), `login_user` (`AuthenticationForm`), `logout_user`, beserta halaman `register.html` dan `login.html`serta status login di navbar (`base.html`)
2. menambahkan cookie `last_login` yang di-set saat login, diread di `show_main` dan ditampilkan di `index.html`, serta dihapus saat logout
3. mengunci `create_certification` dan `delete_certification` dengan `@login_required` dan pengecekan `request.user.is_superuser`, sehingga hanya pemilik portofolio yang bisa menambah/menghapus data
4. menambahkan peran **Editor** lewat Django Group: `edit_certification` mengizinkan superuser atau anggota grup "Editor" (dicek dengan `request.user.groups.filter(name="Editor").exists()`), sedangkan create dan delete tetap khusus superuser
5. menambahkan `ManyToManyField starred_by` pada model `Certification`, view `toggle_star` (maksimal satu star per pengguna, POST dan `{% csrf_token %}`), serta komponen `certification_star.html` yang menampilkan jumlah star dan status pengguna
6. menyembunyikan tombol Tambah/Edit/Hapus di `certifications.html` sesuai peran (`{% if user.is_superuser %}`, `{% if user.is_superuser or is_editor %}`)
7. menambahkan `use_natural_foreign_keys=True` pada `get_certifications_json` supaya `starred_by` menampilkan username, bukan id pengguna
8. menambahkan 8 unit test baru untuk 4 peran (pengunjung, user biasa, editor, superuser), total 30 unit test
9. menambahkan skrip pengujian end-to-end dengan Selenium (`test_e2e.py`, bagian opsional Tutorial 04) untuk memverifikasi alur login, cookie, dan otorisasi lewat browser automate

### Tugas 5

Yang dikerjakan:

1. Mengubah halaman Certifications menjadi kerangka HTML; browser mengambil daftar lewat `fetch()` dari `/api/certifications/`. `JsonResponse` dirakit manual dengan jumlah star dan status star pengguna.
2. Menambahkan kondisi loading, kosong, hasil pencarian kosong, dan error. Pencarian judul memakai debounce 300 ms serta `AbortController` untuk membatalkan permintaan sebelumnya.
3. Memindahkan form tambah ke modal. Endpoint `/certifications/add-ajax/` memvalidasi `CertificationForm`, memeriksa superuser di server, dan mengembalikan JSON dengan status 201, 400, atau 403. POST menyertakan CSRF; setelah berhasil daftar dimuat ulang lewat AJAX.
4. Menggunakan toast untuk sukses, kesalahan validasi, dan kegagalan jaringan. Event listener form hanya dipasang jika modal tersedia untuk pengguna tersebut.
5. Melakukan escaping pada teks JSON sebelum dimasukkan ke HTML, dan membersihkan judul/deskripsi dengan `strip_tags` melalui `clean_title`/`clean_description`. Input yang hanya berisi tag dan menjadi kosong ditolak.
6. Mempertahankan hak akses Tugas 4: pengunjung membaca, pengguna biasa memberi star, editor mengedit, dan pemilik mengelola seluruh data. Menambahkan pengujian penolakan create oleh editor, CSRF, dan deskripsi kosong setelah pembersihan.
7. Membatasi lebar navbar ke container pada mobile agar tidak membuat halaman melebar, dan mengembalikan scroll modal ke bagian judul saat dibuka.

Fitur tambahan di luar checklist minimal:

- Filter **tahun**, **unggulan**, dan **favorit saya** dapat digabungkan dengan pencarian judul. Favorit dibatasi pada akun yang sedang login di sisi server.
- Pengurutan **terbaru**, **terlama**, **judul A–Z**, dan **star terbanyak** memakai pilihan field ORM yang tetap, dengan urutan tambahan berdasarkan ID agar hasil stabil.
- **Star/unstar lewat AJAX** dengan CSRF, tombol dinonaktifkan selama request untuk mencegah klik ganda, dan toast hasil aksi. Saat unstar dalam filter Favorit saya, kartu hilang dari hasil tanpa mengganti halaman.
- Badge unggulan, jumlah hasil dengan `aria-live`, reset filter, dan tombol coba lagi untuk memulihkan kegagalan pemuatan. Tahun dari data yang baru ditambahkan langsung masuk ke pilihan filter.

Audit checklist minimal:

| Poin | Implementasi dan bukti |
|---|---|
| Kerangka halaman + fetch JSON | `show_certifications` merender kerangka; `fetchCertifications` mengambil dan membangun kartu di browser. |
| JsonResponse manual + informasi star | `get_certifications_json` menyusun `fields`, `star_count`, `is_starred`, dan nama pemberi star. |
| Loading, kosong, error | Kontainer `loading`, `empty`, `error`, dan `grid` ditampilkan bergantian. |
| Pencarian AJAX + debounce | Filter `title__icontains`; input memakai timer 300 ms, tombol Cari berjalan segera, dan request sebelumnya dibatalkan. |
| Form tambah di modal | `certification_form_modal.html` disertakan di halaman daftar untuk pemilik. |
| POST + ModelForm + JSON 201/400/403 | `create_certification_ajax`: sukses 201, validasi gagal 400, pengguna tanpa hak 403. |
| Hak akses di server | Tambah hanya superuser; editor tidak boleh tambah/hapus; pengguna biasa hanya star. Hak akses halaman edit/hapus dari Tugas 4 tetap berlaku. |
| CSRF pada POST | Form berisi `csrfmiddlewaretoken`; AJAX juga mengirim `X-CSRFToken`. Test CSRF dijalankan dengan `enforce_csrf_checks=True`. |
| Daftar diperbarui tanpa reload | Setelah create berhasil, `fetchCertifications` dijalankan ulang dengan filter aktif. |
| Toast sukses/gagal/validasi | `showToast` dipakai untuk create, star, error pemuatan, dan pesan validasi server. |
| Escaping semua teks di HTML JavaScript | Teks kartu dan URL dinamis memakai `escapeHtml`; toast dan jumlah hasil memakai `textContent`; opsi tahun memakai `new Option`. |
| strip_tags di clean_<field> | `CertificationForm.clean_title` dan `clean_description` membersihkan tag serta menolak hasil kosong. |
| runserver + semua peran | `manage.py runserver` diuji dengan halaman dan JSON yang mengembalikan 200. Tes browser memakai pengunjung, user biasa, editor, dan superuser. |

Pertanyaan reflektif:

1. **Debouncing** menunda suatu aksi sampai tidak ada event baru selama jeda tertentu. Pada pencarian ini, setiap ketikan membatalkan timer sebelumnya; setelah pengguna berhenti mengetik selama 300 ms, permintaan AJAX dikirim. Ini mengurangi permintaan ke server dibanding mengirim satu permintaan untuk setiap karakter. Tombol Cari tetap menjalankan pencarian segera. `AbortController` melengkapi debounce dengan membatalkan permintaan lama yang sudah terlanjur dikirim.
2. **`await`** menunggu sebuah Promise selesai di dalam fungsi async tanpa memblokir seluruh browser. `await fetch()` menghasilkan objek `Response`, kemudian `await response.json()` membaca dan mengurai body JSON secara asinkron. Tanpa `await`, hasilnya masih Promise, sehingga kita tidak bisa langsung memakai `.ok` atau array datanya; alternatifnya adalah `.then()`. `fetch()` tidak otomatis menolak Promise untuk status HTTP 400/403/500, jadi `response.ok` tetap perlu diperiksa.
3. **XSS** terjadi saat data dari pengguna ditafsirkan sebagai kode yang dijalankan browser. Django Template Language secara bawaan melakukan autoescaping, tetapi perlindungan itu tidak otomatis berlaku ketika JavaScript mengambil JSON lalu merangkainya lewat `innerHTML`. Karena itu judul, deskripsi, tahun, jumlah star, dan nama pemberi star di-escape sebelum disisipkan. Toast memakai `textContent`. Server juga membersihkan input lewat `strip_tags`; pembersihan server tetap harus dilengkapi escaping saat menampilkan data, termasuk data lama yang mungkin sudah tersimpan.

Pemeriksaan browser yang dapat diulang:

- Buka `/certifications/` tanpa login: daftar tetap tampil dan modal tambah tidak tersedia.
- Ketik pencarian dan lihat Network: permintaan baru muncul setelah jeda 300 ms; pencarian tidak mengganti halaman.
- Login sebagai pemilik, tambah melalui modal: POST menghasilkan 201, toast tampil, modal tertutup, dan daftar diperbarui tanpa reload.
- Uji nilai tahun tidak valid atau judul/deskripsi hanya tag melalui POST: respons 400 berisi pesan validasi. Request tanpa CSRF ditolak 403; editor dan pengguna biasa ditolak 403 untuk endpoint tambah AJAX.
- Uji teks `<img src="x" onerror="alert('XSS!')">`: tidak boleh muncul alert. Input yang menjadi kosong setelah tag dibuang ditolak.

Hasil verifikasi lokal oleh Codex pada 5 Oktober 2026: seluruh 48 unit test lulus; `manage.py check` tidak melaporkan masalah dan `makemigrations --check --dry-run` tidak menemukan perubahan model. Unit test terakhir menggunakan MD5 hanya sebagai hasher pada proses test untuk mempercepat pengujian; konfigurasi password aplikasi tidak diubah. Pengujian Chrome headless dengan database test terpisah juga lulus untuk empat peran, escaping data lama, debounce, tambah lewat modal tanpa reload dengan CSRF, toast validasi, filter tahun/unggulan/favorit, pengurutan, reset, star/unstar tanpa reload, kegagalan fetch dan pemulihan melalui tombol Coba lagi, serta halaman/modal pada lebar 390 px. `manage.py runserver` juga dijalankan pada port sementara; halaman dan endpoint JSON dapat diakses tanpa login. Database portofolio lokal tidak dipakai untuk menambah data uji.

---

### Tugas 6

Bagian tugas pribadi tetap memakai model `Certification` yang dibangun sejak Tugas 2 dan dikembangkan pada Tugas 3–5. Implementasi Tutorial 07 sebelumnya juga sudah diterapkan pada model ini. Pada iterasi Tugas 6, edit Certifications dilengkapi lewat API, dan model `Experience` yang sudah ada memperoleh rangkaian API serta antarmuka tersendiri. Perubahan ini tidak mengganti riwayat pengerjaan sebelumnya atau membuktikan pemenuhan tenggat prasyarat Tutorial 07.

Yang dikerjakan:

1. Mempertahankan `CertificationSerializer` dan menambahkan `ExperienceSerializer`, dengan `fields` eksplisit, pembersihan judul/deskripsi melalui `validate_<field>`, serta informasi star yang hanya dapat dibaca.
2. Melengkapi daftar, detail, create, PUT/PATCH, delete, dan toggle star untuk dua model di `/api/v1/`. Experience mempertahankan UUID dan data lamanya; relasi star ditambahkan melalui migrasi. Sesuai model sebelumnya, `started_at` adalah waktu pencatatan otomatis yang read-only, sedangkan `ended_at` opsional dan boleh kosong untuk pengalaman yang masih berlangsung.
3. Memakai `SessionAuthentication`, `IsPortfolioOwnerOrEditorOrReadOnly`, dan `IsAuthenticated` pada endpoint yang sesuai. Akun pemberi star selalu berasal dari `request.user`.
4. Mengintegrasikan perubahan data lewat AJAX, termasuk edit untuk Editor/pemilik, CSRF pada setiap request mutasi, toast kesalahan API, dan escaping saat membangun tampilan.
5. Menambah pengujian API, validasi, peran, perubahan database, serta login session dengan pemeriksaan CSRF aktif. Test Certifications dari Tutorial 07 tetap menjadi bagian dari suite `main`.

| Peran | Daftar/detail | Star/unstar | PUT/PATCH | Tambah/hapus |
|---|---|---|---|---|
| Pengunjung | Ya | Tidak | Tidak | Tidak |
| Pengguna biasa | Ya | Ya, akun sendiri | Tidak | Tidak |
| Grup `Editor` | Ya | Ya, akun sendiri | Ya | Tidak |
| Superuser | Ya | Ya, akun sendiri | Ya | Ya |

Peta checklist implementasi:

| Checklist | Lokasi dan cara memeriksa |
|---|---|
| Serializer eksplisit, validasi teks, star read-only, tanpa email/password | `main/serializers.py`; kirim teks hanya tag HTML dan field star palsu, lalu periksa respons dan database. |
| Otorisasi empat peran di server | `main/permissions.py`, `main/api_views.py`; penolakan diuji bersama nilai database sesudah request. View form sertifikasi lama tetap membatasi create/delete ke pemilik. |
| Function-based API, session, pencarian, URL unik | `main/api_views.py`, `main/api_urls.py`; gunakan namespace `api`, ID integer untuk Certification dan UUID untuk Experience. |
| Status HTTP | Create 201; validasi 400; izin/CSRF 403; objek tidak ada 404; delete 204 dengan body kosong. |
| Daftar/cari/tambah/edit/star/hapus tanpa reload | Halaman Certifications dan bagian Experience memakai endpoint DRF, dengan pesan API 400/403 melalui toast. |
| CSRF dan escaping | Token tersedia di halaman untuk semua peran; mutasi mengirim `X-CSRFToken`; nilai teks di-escape atau dimasukkan lewat `textContent`. |
| Test API, validasi, star, dan database pada penolakan | `main/tests_api.py`, `main/tests_api_integration.py`, `main/tests_permissions.py`, `main/tests_experience_api.py`, dan regresi halaman/jalur lama di `main/tests_assignment6.py`. |
| Login dan CSRF nyata | Test memakai `APIClient(enforce_csrf_checks=True)` serta `.login()`, menolak request tanpa token dan menerima aksi yang diizinkan ketika token benar. |
| Eksekusi dan regresi | Jalankan `python manage.py test main`, `python manage.py check`, `python manage.py makemigrations --check --dry-run`, lalu periksa kedua halaman dan Browsable API dengan `runserver`. |

Untuk pemeriksaan manual, buka `/api/v1/certifications/` dan `/api/v1/experiences/` di browser. Login lewat `/api-auth/login/` untuk mencoba request berdasarkan peran. Pada halaman portofolio, coba pencarian kosong, tambah, edit, star/unstar, dan hapus sambil memeriksa Network: aksi menggunakan endpoint `/api/v1/`, status sesuai, dan tidak memuat ulang dokumen. Coba juga session Editor dan pengguna biasa, bukan hanya pemilik.

Hasil verifikasi lokal oleh Codex pada 7 November 2026: **136 test lulus** pada salinan proyek bersih dalam 54,466 detik, mencakup 106 test lama dan 30 test baru. Pengujian ulang pada proyek lokal asli juga lulus 136 test dalam 53,371 detik, termasuk ketika perubahan latihan yang belum di-commit tetap tersedia. `manage.py check` tidak menemukan masalah, `makemigrations --check --dry-run` tidak menemukan migrasi tertinggal, dan `python -m pip check` tidak menemukan dependency yang rusak. Migrasi dan `runserver` berhasil dijalankan pada database uji terpisah di port 8766; kedua Browsable API mengembalikan 200. Pengujian Edge headless mencakup empat peran pada kedua bagian, debounce, hasil kosong, pemulihan error, create 201/PATCH/delete 204 tanpa reload, toast 400/403, escaping XSS, CSRF pada setiap mutasi, dan pencegahan submit ganda. Tampilan serta modal diperiksa pada lebar 390 px dalam tema gelap/terang, tanpa error JavaScript. Migrasi juga sudah diterapkan pada proyek lokal asli; perbandingan fingerprint sebelum/sesudah memastikan data Experience, Certification, relasi star lama, dan akun pengguna tetap utuh.

Pertanyaan reflektif:

1. **REST dan perbedaan PUT/PATCH.** REST adalah gaya arsitektur yang mengatur interaksi klien dan server melalui representasi resource. Batasannya mencakup pemisahan client-server, stateless, cache, antarmuka seragam, sistem berlapis, dan code-on-demand yang opsional. JSON hanya format representasi; mengembalikan JSON belum membuktikan batasan tersebut terpenuhi. Pemakaian URI resource, method dan status HTTP yang tepat membantu, sedangkan antarmuka seragam juga mencakup pesan yang menjelaskan dirinya serta navigasi melalui hypermedia. Proyek ini mengikuti pola API berbasis resource dari tutorial dan memakai session login, sehingga saya tidak mengklaim seluruh batasan REST murni sudah dipenuhi. [Fielding, REST](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm).

   PUT menyatakan representasi pengganti resource; cocok ketika seluruh data yang bisa diedit dikirim, misalnya judul, deskripsi, tahun, dan status unggulan sertifikasi. PATCH menyatakan perubahan sebagian; cocok untuk mengganti `{"title": "Judul baru"}` tanpa mengirim field lain. Pada DRF, PATCH memakai `partial=True`; PUT tetap memvalidasi field wajib. Field read-only tidak menjadi input pada keduanya. PUT bersifat idempotent; sifat idempotent PATCH bergantung pada operasinya. [RFC 9110: PUT](https://www.rfc-editor.org/rfc/rfc9110.html#name-put), [RFC 5789: PATCH](https://www.rfc-editor.org/rfc/rfc5789.html#section-2).

2. **Peran serializer.** Serializer mengubah objek model menjadi tipe data Python yang dapat dirender sebagai JSON, sekaligus memeriksa data masukan sebelum disimpan. `ModelSerializer` mengambil aturan field dari model; daftar `fields` eksplisit mengendalikan data yang tampil. Di proyek ini, `validate_title` dan `validate_description` membersihkan tag HTML dan menolak hasil kosong. `star_count` dan `is_starred` dihitung server, sehingga klien tidak bisa menentukan jumlah star atau akun pemberinya. Dibanding menyusun dictionary dengan `JsonResponse`, aturan representasi, validasi, create, dan update terpusat serta dapat diuji ulang. `JsonResponse` sendiri hanya mengirim JSON; validasi dan penyimpanan tetap perlu dibuat terpisah. [Dokumentasi serializer DRF](https://www.django-rest-framework.org/api-guide/serializers/).

3. **Autentikasi dan otorisasi.** Autentikasi menentukan identitas pengirim request; `SessionAuthentication` membaca session login Django dan mengisi `request.user`. Otorisasi menentukan tindakan yang boleh dilakukan identitas tersebut. Contohnya, Editor berhasil login tetapi tetap ditolak ketika POST untuk membuat data atau DELETE; ia boleh PUT/PATCH. Tombol tersembunyi hanya mengatur tampilan, karena pengguna masih dapat mengirim request langsung lewat browser, curl, atau aplikasi lain. Karena itu permission diperiksa server sebelum data ditulis. Endpoint star memakai `IsAuthenticated`, sedangkan identitasnya diambil dari session, bukan ID dalam body. [Dokumentasi autentikasi DRF](https://www.django-rest-framework.org/api-guide/authentication/).

4. **Session dan CSRF.** Browser menyertakan cookie session secara otomatis pada request yang memenuhi aturan cookie. Situs lain dapat mencoba memicu aksi memakai session korban, sehingga request yang mengubah data tetap memerlukan pemeriksaan CSRF. AJAX mengirim token lewat `X-CSRFToken`; server menolak token hilang atau salah. JSON tidak menggantikan perlindungan ini. [SessionAuthentication DRF](https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication).

   `force_authenticate` melewati proses autentikasi sebenarnya, sehingga cocok untuk menguji izin tetapi tidak membuktikan login session dan CSRF. Pengujian CSRF memakai `APIClient(enforce_csrf_checks=True)` dan `.login()`: akses halaman untuk memperoleh cookie/token, lakukan request tanpa token dan pastikan 403 serta database tidak berubah, lalu ulangi dengan token untuk aksi yang memang diizinkan. [Pengujian CSRF DRF](https://www.django-rest-framework.org/api-guide/testing/#csrf-validation).

Pengumpulan memakai tautan commit akhir GitHub yang telah di-push, bukan hanya tautan repositori. Status deployment PWS dan pengumpulan di SCELE perlu diperiksa terpisah dari hasil test lokal.

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
4. Fitur tambahan atas permintaan saya, yang diedit langsung oleh AI: tampilan flash message di `base.html`, endpoint JSON pengalaman (`/api/experiences/`) beserta helper `json_response`, 14 unit test baru untuk create/edit/delete/JSON, dan penulisan ulang bagian atas README (fitur, endpoint, cara menjalankan, struktur berkas)
5. Perubahan tampilan yang saya minta ke AI: font Poppins, foto pada kartu proyek, penambahan skill Java, dan border foto profil

Strategi prompting: saya memberikan PDF Tutorial 03 dan Tugas 3, meminta AI menjelaskan materi terlebih dahulu, lalu meminta panduan per commit (saya yang mengetik, menjalankan, dan melakukan commit sendiri). Setiap langkah saya minta dicek ulang terhadap PDF, dan saya meminta AI membaca file proyek untuk memverifikasi hasil edit saya.

Perbaikan serta verifikasi manual yang saya lakukan

1. mengetik dan menyesuaikan kode ke struktur proyek saya sendiri, termasuk view `edit_certification` dan routing-nya
2. menjalankan `python manage.py runserver` dan mencoba fitur tambah, ubah, hapus, pencarian, dan endpoint `/api/certifications/` langsung di browser
3. memperbaiki error yang muncul sendiri: `ModuleNotFoundError: dotenv` karena venv belum aktif, `TemplateSyntaxError` karena sisa `<!DOCTYPE>` sebelum `{% extends %}`, folder `components/` yang salah letak, import yang belum ditambahkan di `main/urls.py`, variabel `Certification` yang menimpa nama model di `delete_certification`, dan CSS yang tertahan cache browser
4. me-refactor `index.html` agar memakai `base.html`, menghapus fungsi `show_certifications` yang terduplikasi, dan meninjau ulang agar struktur kode mengikuti PDF
5. melakukan commit secara bertahap dengan pesan yang deskriptif

Keterbatasan AI yang saya temui: instruksi AI sempat tidak sinkron dengan PDF (misalnya struktur modal hapus yang keliru pada percobaan pertama) dan beberapa langkah tidak menyebutkan detail yang membuat error, seperti `{% load static %}` yang harus ditulis ulang di template turunan. AI juga tidak bisa menjalankan klik/submit form di browser saya, sehingga pengujian alur tambah, ubah, hapus tetap saya lakukan sendiri. Unit test buatan AI hanya memeriksa HTML dan data di sisi server, bukan tampilan visual (misalnya flash message, foto kartu proyek, dan border foto profil), jadi hal tersebut tetap saya periksa langsung di browser. Isi teks kartu proyek yang ditulis AI juga saya verifikasi terhadap data saya sendiri, karena AI tidak mengetahui detail proyek saya di luar yang ada di repositori.

### Tugas 4

Tools yang dipakai: Claude Code (Claude Sonnet 5, Anthropic).

Bagian yang dibantu AI

1. Penjelasan materi Tutorial 04 (autentikasi bawaan Django, session, cookie, CSRF, otorisasi berbasis peran) sebelum saya mengimplementasikan sendiri
2. Panduan tiap langkah Tutorial 04, disesuaikan ke model `Certification` milik saya (bukan `Project` seperti contoh PDF): `register`/`login_user`/`logout_user`, cookie `last_login`, `@login_required` dan cek `is_superuser` pada `create_certification`/`edit_certification`/`delete_certification`, `ManyToManyField starred_by`, view `toggle_star`

Strategi prompting: saya memberikan PDF Tutorial 04 dan Tugas 4, meminta AI menjelaskan materi dulu, lalu meminta AI membaca ulang kode saya untuk mengecek bug sebelum saya commit.

Perbaikan serta verifikasi manual yang saya lakukan

1. menjalankan `python manage.py migrate` dan `python manage.py runserver`, lalu mencoba sendiri alur register, login, logout, dan status navbar di browser
2. membuat grup "Editor" secara manual lewat Django Admin dan memasukkan akun uji ke dalamnya, karena ini langkah yang tidak bisa dilakukan lewat kode
3. menjalankan `python manage.py test` untuk memastikan seluruh 30 unit test lulus, termasuk 8 test otorisasi peran yang baru
4. menyelesaikan konflik `git rebase` secara manual saat menyatukan commit lokal dengan perubahan yang saya buat langsung lewat GitHub web editor
5. mengecek langsung endpoint `/api/certifications/` di browser untuk memastikan `starred_by` tidak membocorkan id pengguna

Keterbatasan AI yang saya temui: AI sempat menandai `edit_certification` tanpa proteksi sama sekali dan `get_certifications_json` yang menghitung `use_natural_foreign_keys` tapi tidak memakainya, keduanya bug yang lolos dari saya sendiri karena saya mengetik terburu-buru mengejar tenggat waktu. AI juga tidak bisa menjalankan Burp Suite (bagian opsional Tutorial 04) karena itu aplikasi desktop terpisah yang perlu diinstal dan dioperasikan manual, jadi bagian itu saya lewati dan cukup memahami konsepnya dari penjelasan AI.

### Tugas 5

Tools pada sesi ini: OpenAI Codex.

Bagian yang dibantu AI: membaca PDF Tutorial 0–5 dan Tugas 1–5 untuk memahami konteks, memeriksa implementasi Certifications yang sudah ada, melengkapi dokumentasi Tugas 5, memperbaiki validasi deskripsi setelah `strip_tags`, memperjelas kondisi hasil pencarian kosong, menambahkan toast kegagalan pemuatan, memperbaiki lebar navbar dan posisi scroll modal pada mobile, serta menambahkan pengujian CSRF dan otorisasi editor. Implementasi utama AJAX, modal, toast, dan escaping sudah ada pada commit `2253054` sebelum sesi Codex ini.

Strategi prompting: memberikan PDF tutorial/tugas, meminta pemahaman konteks dan cara menghubungkan folder VS Code, lalu memberikan lokasi `manage.py` untuk pemeriksaan proyek lokal.

Ringkasan log prompting:

1. Meminta memahami konteks dan cara melanjutkan Tugas 5 melalui VS Code.
2. Memberikan `tugas-5.pdf` agar persyaratannya bisa dibaca.
3. Memberikan alamat folder proyek melalui path `manage.py`.
4. Meminta audit seluruh checklist minimal serta fitur inovasi untuk mendukung target nilai 4. Codex menambahkan filter gabungan, pengurutan, favorit pribadi, star/unstar AJAX, jumlah hasil, badge unggulan, reset filter, dan tombol coba lagi, serta pengujian server/browser untuk fitur tersebut.
5. Meminta tampilan Certifications, login, dan buat akun diperbaiki agar lebih profesional. Codex merapikan pencarian/filter menjadi panel dengan pilihan pill, kartu sertifikasi, header, serta layout login/registrasi; menambahkan komponen `auth_fields.html`, `auth_story.html`, dan `auth.js`. Form autentikasi tetap memakai subclass form bawaan Django. Verifikasi browser mencakup gelap/terang di desktop, lebar mobile 390 px, tampil/sembunyikan password, penolakan konfirmasi password yang berbeda, registrasi berhasil, login salah/benar, serta pengujian ulang fitur AJAX. Seluruh pengujian memakai database test terpisah.

Keterbatasan: jawaban reflektif di atas merupakan draf yang dibantu Codex dan perlu ditinjau agar sesuai pemahaman pribadi. Pengujian lokal tidak membuktikan keberhasilan deployment PWS, status pengumpulan SCELE, atau pemenuhan tenggat prasyarat Tutorial 05.

### Tugas 6

Tools pada sesi ini: OpenAI Codex, dengan pemeriksaan dokumentasi resmi DRF, disertasi REST Fielding, dan RFC HTTP untuk jawaban reflektif.

Bagian yang dibantu AI: membaca `tugas-6.pdf` dan kode yang ada, memetakan checklist, menambahkan API serta star untuk Experience, melengkapi edit Certifications lewat API, membantu antarmuka AJAX, menulis pengujian peran/validasi/CSRF, dan menyusun dokumentasi serta draf jawaban reflektif. Codex juga membantu memisahkan perubahan menjadi commit berdasarkan bagian pekerjaan yang selesai dan memeriksa hasil sebelum push.

Ringkasan log prompting:

1. Pengguna memberikan `tugas-6.pdf` dan meminta commit/push bertahap serta seluruh checklist diperiksa.
2. Codex membaca ketentuan, riwayat proyek, dan file lokal. Ditemukan bahwa model Certification sudah dipakai untuk tugas pribadi sekaligus implementasi Tutorial 07 sebelumnya.
3. Pengerjaan diarahkan untuk mempertahankan Certification, melengkapi edit API-nya, dan menambahkan implementasi DRF terpisah pada Experience yang sudah ada. Backend, antarmuka, dokumentasi, dan pemeriksaan dibagi sebagai pekerjaan terpisah.

Keterbatasan dan evaluasi: AI sebelumnya menerapkan tutorial pada model tugas pribadi; koreksi sekarang didokumentasikan tanpa mengubah riwayat. Draf refleksi masih perlu ditinjau pemilik proyek agar sesuai pemahamannya. Verifikasi lokal tidak membuktikan deployment PWS atau pengumpulan SCELE. Waktu commit mengikuti pekerjaan yang benar-benar dilakukan; tanggal dan jeda tidak direkayasa.


