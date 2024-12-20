# -*- coding: utf-8 -*-
# from odoo import http
import json
from odoo import http
from odoo.http import request
import random
from datetime import date
import datetime
from odoo.exceptions import UserError
import hashlib
import locale
import base64

# class PsbController(http.Controller):
#     @http.route('/psb/statistics', type='http', auth='public', methods=['POST'], csrf=False)
#     def get_statistics(self):
#         Pendaftaran = request.env['ubig.pendaftaran'].sudo()
#         data = Pendaftaran.get_psb_statistics()

#         if request.httprequest.headers.get('Content-Type') == 'application/json':
#             # Permintaan JSON
#             return json.dumps(data)
#         else:
#             # Permintaan HTTP biasa
#             return request.make_response(
#                 json.dumps(data),
#                 headers={'Content-Type': 'application/json'}
#             )
        
#     @http.route('/pendaftaran/check', type='http', auth='public', methods=['POST'], csrf=False)
#     def check_kuota(self):
#         Pendaftaran = request.env['ubig.pendaftaran'].sudo()
#         total_pendaftar = Pendaftaran.search_count([])

#         # Mengambil nilai kuota pendaftaran dari ir.config_parameter
#         config_param = request.env['ir.config_parameter'].sudo()
#         kuota_pendaftaran = int(config_param.get_param('pesantren_pendaftaran.kuota_pendaftaran', default=0))

#         data = {
#             'is_full': total_pendaftar >= kuota_pendaftaran # True jika kuota penuh
#         }

#         if request.httprequest.headers.get('Content-Type') == 'application/json':
#             # Permintaan JSON
#             return json.dumps(data)
#         else:
#             # Permintaan HTTP biasa
#             return request.make_response(
#                 json.dumps(data),
#                 headers={'Content-Type': 'application/json'}
#             )


class PesantrenBeranda(http.Controller):
    @http.route('/beranda', type='http', auth='public')
    def index(self, **kwargs):

        # Ambil perusahaan yang aktif (current company)
        company = http.request.env.user.company_id

        # Ambil alamat perusahaan
        alamat_perusahaan = {
            'street': company.street or '',
            'street2': company.street2 or '',
            'city': company.city or '',
            'state': company.state_id.name if company.state_id else '',
            'zip': company.zip or '',
            'country': company.country_id.name if company.country_id else '',
        }

        # Gabungkan alamat menjadi satu string (opsional)
        alamat_lengkap = ', '.join(filter(None, [
            alamat_perusahaan['street'],
            alamat_perusahaan['street2'],
            alamat_perusahaan['city'],
            alamat_perusahaan['state'],
            alamat_perusahaan['zip'],
            alamat_perusahaan['country']
        ]))

         # Ambil nilai dari field konfigurasi
        config_obj = http.request.env['ir.config_parameter'].sudo()

        tgl_mulai_pendaftaran = config_obj.get_param('pesantren_pendaftaran.tgl_mulai_pendaftaran')
        tgl_akhir_pendaftaran = config_obj.get_param('pesantren_pendaftaran.tgl_akhir_pendaftaran')
        tgl_mulai_verifikasi_berkas = config_obj.get_param('pesantren_pendaftaran.tgl_mulai_verifikasi_berkas')
        tgl_akhir_verifikasi_berkas = config_obj.get_param('pesantren_pendaftaran.tgl_akhir_verifikasi_berkas')
        tgl_mulai_seleksi = config_obj.get_param('pesantren_pendaftaran.tgl_mulai_seleksi')
        tgl_akhir_seleksi = config_obj.get_param('pesantren_pendaftaran.tgl_akhir_seleksi')
        tgl_pengumuman_hasil_seleksi = config_obj.get_param('pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi')

        # Set nilai default dinamis jika parameter kosong
        if not tgl_mulai_pendaftaran:
            tgl_mulai_pendaftaran_dt = datetime.datetime.now() + datetime.timedelta(days=1)
            tgl_mulai_pendaftaran = tgl_mulai_pendaftaran_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_mulai_pendaftaran_dt = datetime.datetime.strptime(tgl_mulai_pendaftaran, '%Y-%m-%d %H:%M:%S')

        if not tgl_akhir_pendaftaran:
            tgl_akhir_pendaftaran_dt = tgl_mulai_pendaftaran_dt + datetime.timedelta(days=3)
            tgl_akhir_pendaftaran = tgl_akhir_pendaftaran_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_akhir_pendaftaran_dt = datetime.datetime.strptime(tgl_akhir_pendaftaran, '%Y-%m-%d %H:%M:%S')

        if not tgl_mulai_verifikasi_berkas:
            tgl_mulai_verifikasi_berkas_dt = datetime.datetime.now() + datetime.timedelta(days=1)
            tgl_mulai_verifikasi_berkas = tgl_mulai_verifikasi_berkas_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_mulai_verifikasi_berkas_dt = datetime.datetime.strptime(tgl_mulai_verifikasi_berkas, '%Y-%m-%d %H:%M:%S')

        if not tgl_akhir_verifikasi_berkas:
            tgl_akhir_verifikasi_berkas_dt = tgl_mulai_verifikasi_berkas_dt + datetime.timedelta(days=3)
            tgl_akhir_verifikasi_berkas = tgl_akhir_verifikasi_berkas_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_akhir_verifikasi_berkas_dt = datetime.datetime.strptime(tgl_akhir_verifikasi_berkas, '%Y-%m-%d %H:%M:%S')

        if not tgl_mulai_seleksi:
            tgl_mulai_seleksi_dt = tgl_akhir_pendaftaran_dt
            tgl_mulai_seleksi = tgl_mulai_seleksi_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_mulai_seleksi_dt = datetime.datetime.strptime(tgl_mulai_seleksi, '%Y-%m-%d %H:%M:%S')

        if not tgl_akhir_seleksi:
            tgl_akhir_seleksi_dt = tgl_mulai_seleksi_dt + datetime.timedelta(days=3)
            tgl_akhir_seleksi = tgl_akhir_seleksi_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_akhir_seleksi_dt = datetime.datetime.strptime(tgl_akhir_seleksi, '%Y-%m-%d %H:%M:%S')

        if not tgl_pengumuman_hasil_seleksi:
            tgl_pengumuman_hasil_seleksi_dt = tgl_akhir_seleksi_dt + datetime.timedelta(days=2)
            tgl_pengumuman_hasil_seleksi = tgl_pengumuman_hasil_seleksi_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_pengumuman_hasil_seleksi_dt = datetime.datetime.strptime(tgl_pengumuman_hasil_seleksi, '%Y-%m-%d %H:%M:%S')

        # Format tanggal manual dalam bahasa Indonesia
        def format_tanggal_manual(dt):
            bulan_indonesia = [
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            return f"{dt.day} {bulan_indonesia[dt.month - 1]} {dt.year}"

        # Format tanggal untuk ditampilkan di halaman
        tgl_mulai_pendaftaran_formatted = format_tanggal_manual(tgl_mulai_pendaftaran_dt)
        tgl_akhir_pendaftaran_formatted = format_tanggal_manual(tgl_akhir_pendaftaran_dt)
        tgl_mulai_verifikasi_berkas_formatted = format_tanggal_manual(tgl_mulai_verifikasi_berkas_dt)
        tgl_akhir_verifikasi_berkas_formatted = format_tanggal_manual(tgl_akhir_verifikasi_berkas_dt)
        tgl_mulai_seleksi_formatted = format_tanggal_manual(tgl_mulai_seleksi_dt)
        tgl_akhir_seleksi_formatted = format_tanggal_manual(tgl_akhir_seleksi_dt)
        tgl_pengumuman_hasil_seleksi_formatted = format_tanggal_manual(tgl_pengumuman_hasil_seleksi_dt)

        current_year = datetime.datetime.now().year

        next_year = current_year + 1
        year_range = f"{current_year} - {next_year}"


        html_content = f"""
                    <!doctype html>
                    <html lang="en">

            <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Daarul Qur'an Istiqomah</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"
                integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            </head>
            <style>
            .bg-body-grenyellow {{ background: linear-gradient(to right, #009688 40%, #ccff33 130%); }}

            .rounded-90 {{ border-radius: 0 0 25% 0; }}

            .p-auto {{ padding: 6% 0; }}

            .stepper {{ justify-content: space-around; align-items: center; margin-top: 50px; }}

            .step {{ text-align: center; position: relative; padding-top: 30px; }}

            .step-circle {{ 
                width: 50px;
                height: 50px;
                background-color: #009688;
                color: white;
                font-size: 1.5rem;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
                position: relative;z-index: 1; }}

            .step-line {{ 
                width: 100%;
                height: 2px;
                background-color: #009688;
                position: absolute;
                top: 55px;
                left: 0;
                z-index: -10; }}

            .step:last-child .step-line {{ 
                width: 50%; }}

            .step:first-child .step-line {{ 
                width: 50%;
                left: 50%; }}

            .text-green {{ 
                color: #009688; }}
            .footer {{ 
                background-color: #4a4a4a;
             }}
            .footer h5 {{
                font-weight: bold;
            }}
            .footer p, .footer a {{
            color: #ffffff;
            font-size: 0.9rem;
            }}
            .footer a:hover {{
            text-decoration: underline;
            }}
            .footer hr {{
            border-color: #ffffff;
            opacity: 0.3;
            }}
            .card p{{
            margin: 0;
            }}
            @media(max-width:768px) {{
            h1{{
                font-size:1.5rem;
            }}
            h3{{
                font-size: 1rem;
            }}
            h5{{
                font-size: 0.9rem;
            }}
            .step{{
                padding: 5px;
                padding-top: 20px;
                margin: 30px 0;
                box-shadow: var(--bs-box-shadow) !important;
                border-radius: 10px;
            }}
            .bg-body-grenyellow.rounded-90{{
                border-radius: 0;
            }}
            .w-set-auto{{
                width: 100%;
            }}
            }}

            /* Styling umum */
            .card-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%; /* Pastikan tinggi fleksibel */
                text-align: center; /* Pusatkan semua teks */
            }}

            .card-value {{
                font-weight: bold;
                font-size: 2rem; /* Ukuran dasar untuk angka */
                line-height: 1; /* Pastikan tidak ada spasi tambahan */
                margin: 0; /* Hapus margin */
                height: 50px;
            }}

            .card-label {{
                font-weight: 600;
                color: #6c757d; /* Warna teks sekunder */
                font-size: 1.25rem; /* Ukuran dasar untuk label */
                margin: 0; /* Hapus margin */
                line-height: 1.2; /* Sedikit lebih tinggi untuk label */
                height: 30px;
            }}

            /* Responsif untuk layar medium */
            @media (max-width: 768px) {{
                .card-value {{
                    font-size: 1.75rem; /* Lebih kecil untuk tablet */
                }}
                .card-label {{
                    font-size: 1rem; /* Lebih kecil untuk label tablet */
                }}
            }}

            /* Responsif untuk layar kecil */
            @media (max-width: 576px) {{
                .card-value {{
                    font-size: 1.5rem; /* Lebih kecil untuk layar kecil */
                    height: 30px;
                }}
                .card-label {{
                    font-size: 0.875rem; /* Ukuran kecil untuk label */
                }}
            }}

            /* Responsif untuk layar sangat kecil */
            @media (max-width: 400px) {{
                .card-value {{
                    font-size: 1.25rem; /* Ukuran paling kecil */
                }}
                .card-label {{
                    font-size: 0.75rem; /* Ukuran kecil untuk label */
                }}
            }}

            </style>

            <body>
            <!-- Navbar -->
            <nav class="navbar navbar-expand-lg bg-body-grenyellow shadow sticky-top">
            <div class="container d-flex">
                <a class="navbar-brand d-flex text-white fw-bold" href="#">
                <img src="https://i.ibb.co.com/1MFsvMq/1731466812700.png" alt="Icon Daarul Qur’an Istiqomah" class="me-2 d-md-block d-none" width="40" height="40">
                <span class="d-md-block d-none h3">
                    PSB Daarul Qur’an Istiqomah
                </span> 
                <span class="d-md-none d-block h3">
                    PSBDQI
                </span> 
                </a>
                <div class="d-flex justify-content-end" id="navbarSupportedContent">
                <div>
                    <!-- Buttons for Pendaftaran and Login -->
                    <a href="/psb" class="btn btn-light ms-2" type="submit">Pendaftaran</a>
                    <a href="/login" class="btn btn-warning ms-2" type="submit">Login</a>
                </div>
                </div>
            </div>
            </nav>
            <!-- Navbar end -->


            <!-- banner -->
            <div class="bg-body-grenyellow rounded-90">
                <div class="container py-3 d-md-flex d-block text-light justify-content-center align-items-center">
                <div class="me-5 w-set-auto d-flex justify-content-center">
                    <img src="https://i.ibb.co.com/1MFsvMq/1731466812700.png" alt="" width="65%">
                </div>
                <div class="ms-md-3 m-0 text-center text-md-start">
                    <h1 class="fw-bold">Pendaftaran Santri Baru</h1>
                    <h3 class="fw-bold pb-3">Pondok Pesantren Daarul Qur’an Istiqomah</h3>
                    <h5 class="fw-bold">Daarul Qur’an Istiqomah Boarding School for Education and Science</h5>
                    <h5 class="fw-bold">Tahun Ajaran { year_range }</h5>
                    <a href="/psb" class="btn btn-light rounded-5 text-primary mt-2">Daftar Sekarang</a>
                </div>
                </div>
            </div>
            <!-- banner end -->

            <!-- Step Pendaftaran -->
            <!-- <div class="container">
                <div class="row shadow rounded mt-5 mb-5 p-5" style="background-color: #EAF1FB;">
                    <div class="col-3 col-sm-3 col-md-3 col-lg-3">
                        <div class="card-item">
                            <span class="card-value" id="count-kuota">0</span>
                            <span class="card-label">Jumlah Kuota</span>
                        </div>
                    </div>
                    <div class="col-3 col-sm-3 col-md-3 col-lg-3">
                        <div class="card-item">
                            <span class="card-value" id="count-pendaftar">0</span>
                            <span class="card-label">Jumlah Pendaftar</span>
                        </div>
                    </div>
                    <div class="col-3 col-sm-3 col-md-3 col-lg-3">
                        <div class="card-item">
                            <span class="card-value" id="count-diterima">0</span>
                            <span class="card-label">Jumlah Diterima</span>
                        </div>
                    </div>
                    <div class="col-3 col-sm-3 col-md-3 col-lg-3">
                        <div class="card-item">
                            <span class="card-value" id="count-sisa">0</span>
                            <span class="card-label">Sisa Kuota</span>
                        </div>
                    </div>
                </div>
            </div> -->
            
            <div class="container text-center my-3">
                <h1 class="fw-bold"><span class="text-green">Alur</span> Pendaftaran Online</h1>
                <div class="container">
                <div class="stepper d-md-flex d-block">
                    <div class="step">
                    <div class="step-circle">1</div>
                    <div class="step-line d-md-block d-none"></div>
                    <p class="mt-3 fw-bold">Pembuatan Akun</p>
                    <p class="text-muted">Mengisi identitas calon peserta didik sekaligus pembuatan akun untuk mendapatkan Nomor
                        Registrasi.</p>
                    </div>
                    <div class="step">
                    <div class="step-circle">2</div>
                    <div class="step-line d-md-block d-none"></div>
                    <p class="mt-3 fw-bold">Melengkapi Data</p>
                    <p class="text-muted">Melengkapi data peserta didik, data orang tua / wali atau mahram khususnya santri putri.
                    </p>
                    </div>
                    <div class="step">
                    <div class="step-circle">3</div>
                    <div class="step-line d-md-block d-none"></div>
                    <p class="mt-3 fw-bold">Mengunggah Berkas</p>
                    <p class="text-muted">Mengunggah berkas persyaratan dan berkas pendukung lainnya yang berupa gambar / foto.
                    </p>
                    </div>
                    <div class="step">
                    <div class="step-circle">4</div>
                    <div class="step-line d-md-block d-none"></div>
                    <p class="mt-3 fw-bold">Pembayaran</p>
                    <p class="text-muted">Melakukan pembayaran biaya pendaftaran sesuai pendidikan yang telah dipilih.</p>
                    </div>
                    <div class="step">
                    <div class="step-circle">5</div>
                    <div class="step-line d-md-block d-none"></div>
                    <p class="mt-3 fw-bold">Cetak Pendaftaran</p>
                    <p class="text-muted">Cetak atau simpan Nomor Registrasi sebagai bukti pendaftaran untuk ditunjukkan ke
                        petugas PSB.</p>
                    </div>
                </div>
                </div>
            </div>
            <!-- End step pendaftaran -->


            <!-- Syarat Pendaftaran -->
            <div class="container my-5">
                <div class="row align-items-center">
                <!-- Text Section -->
                <div class="col-md-6">
                    <h2 class="fw-bold"><span class="text-green ">Syarat</span> Pendaftaran</h2>
                    <p>Untuk memenuhi persyaratan pendaftaran santri baru, perlu beberapa berkas yang harus disiapkan:</p>
                    <ul class="list-unstyled d-grid gap-2">
                    <li class="d-flex"><i class="bi bi-check-circle-fill me-2 text-warning"></i>
                        <div class="d-flex flex-column"><strong>Fotocopy Akta Kelahiran 2lembar</strong> </div>
                    </li>
                    <li class="d-flex"><i class="bi bi-check-circle-fill me-2 text-warning"></i>
                        <div class="d-flex flex-column"><strong>Fotocopy KK 1lembar</strong></div>
                    </li>
                    <li class="d-flex"><i class="bi bi-check-circle-fill me-2 text-warning"></i>
                        <div class="d-flex flex-column"><strong>Fotocopy KTP Orangtua (Masing-masing 1lembar)</strong></div>
                    </li>
                    <li class="d-flex"><i class="bi bi-check-circle-fill me-2 text-warning"></i>
                        <div class="d-flex flex-column"><strong>Fotocopy Raport Semester akhir (menyusul)</strong>
                        </div>
                    </li>
                    <li class="d-flex"><i class="bi bi-check-circle-fill me-2 text-warning"></i>
                        <div class="d-flex flex-column"><strong>Pas Foto berwarna ukuran 3x4 4lembar</strong> </div>
                    </li>
                    <li class="d-flex"><i class="bi bi-check-circle-fill me-2 text-warning"></i>
                        <div class="d-flex flex-column"><strong>Pas Foto Orangtua masing-masing 1lembar (Khusus Pendaftar KB dan TK)</strong> </div>
                    </li>
                    <li class="d-flex"><i class="bi bi-check-circle-fill me-2 text-warning"></i>
                        <div class="d-flex flex-column"><strong>Berkas dimasukkan dalam Map warna hijau dan diberi nama serta lembaga pendidikan</strong> </div>
                    </li>
                    </ul>
                </div>
                <!-- Image Section -->
                <div class="col-md-6">
                    <img src="pesantren_pendaftaran/static/src/img/PAGE2.44b0e259.png" class="img-fluid rounded-4"
                    alt="Syarat Pendaftaran">
                </div>
                </div>
            </div>
            <!-- Syarat Pendaftaran End -->

            <!-- Alur Penyerahan Santri -->
            <div class="container mt-5">
                <h1 class="fw-bold">Alur <span class="text-green">Penyerahan Santri</span></h1>
                <div class="row justify-content-center">
                <!-- Card 1 -->
                <div class="col-md-4 text-center my-2">
                    <div class="card p-4 shadow border-0 h-100">
                    <div class="circle-icon mb-3">
                        <i class="bi bi-plus-circle-fill h1 text-green"></i>
                    </div>
                    <h2 class="step-number">1</h2>
                    <h5 class="font-weight-bold mt-3">Checkup / Periksa Kesehatan</h5>
                    <p>Pemeriksaan kesehatan dari calon peserta didik oleh petugas klinik Az-Zainiyah.</p>
                    <div class="bottom-icon mt-4">
                        <i class="bi bi-shirt text-info"></i>
                    </div>
                    </div>
                </div>
                <!-- Card 2 -->
                <div class="col-md-4 text-center my-2">
                    <div class="card p-4 shadow border-0 h-100">
                    <div class="circle-icon mb-3">
                        <i class="bi bi-file-earmark-text-fill h1 text-green"></i>
                    </div>
                    <h2 class="step-number">2</h2>
                    <h5 class="font-weight-bold mt-3">Konfirmasi Nomor Registrasi</h5>
                    <p>Menyerahkan Nomor Registrasi dan bukti pendaftaran online kepada petugas PSB.</p>
                    <div class="bottom-icon mt-4">
                        <i class="bi bi-handshake text-success"></i>
                    </div>
                    </div>
                </div>
                <!-- Card 3 -->
                <div class="col-md-4 text-center my-2">
                    <div class="card p-4 shadow border-0 h-100">
                    <div class="circle-icon mb-3">
                        <i class="bi bi-person-check-fill h1 text-green"></i>
                    </div>
                    <h2 class="step-number">3</h2>
                    <h5 class="font-weight-bold mt-3">Ikrar Santri</h5>
                    <p>Melakukan Ikrar Santri dan kesediaan mengikuti aturan yang ditetapkan Pondok.
                    </p>
                    </div>
                </div>
                <!-- Card 4 -->
                <div class="col-md-4 text-center my-2">
                    <div class="card p-4 shadow border-0 h-100">
                    <div class="circle-icon mb-3">
                        <i class="bi bi-box-seam-fill h1 text-green"></i>
                    </div>
                    <h2 class="step-number">4</h2>
                    <h5 class="font-weight-bold mt-3">Pengambilan Seragam</h5>
                    <p>Pengambilan seragam sesuai dengan ukuran yang telah dipilih oleh pendaftar. </p>
                    <div class="bottom-icon mt-4">
                        <i class="bi bi-shirt text-info"></i>
                    </div>
                    </div>
                </div>
                <!-- Card 5 -->
                <div class="col-md-4 text-center my-2">
                    <div class="card p-4 shadow border-0 h-100">
                    <div class="circle-icon mb-3">
                        <i class="bi bi-people h1 text-green"></i>
                    </div>
                    <h2 class="step-number">5</h2>
                    <h5 class="font-weight-bold mt-3">Sowan Pengasuh</h5>
                    <p>Penyerahan calon peserta didik oleh orangtua / wali kepada pengasuh </p>
                    <div class="bottom-icon mt-4">
                        <i class="bi bi-handshake text-success"></i>
                    </div>
                    </div>
                </div>
                <!-- Card 6 -->
                <div class="col-md-4 text-center my-2">
                    <div class="card p-4 shadow border-0 h-100">
                    <div class="circle-icon mb-3">
                        <i class="bi bi-buildings h1 text-green"></i>
                    </div>
                    <h2 class="step-number">6</h2>
                    <h5 class="font-weight-bold mt-3">Asrama Santri</h5>
                    <p>Santri baru menempati asrama yang telah ditetepkan oleh pengurus. </p>
                    </div>
                </div>
                </div>
            </div>
            <!-- Alur Penyerahan Santri end-->

            <!-- Informasi Pelayanan Pendaftaran -->
            <div class="container my-5">
                <div class="row align-items-center">
                <div class="col-md-6">
                    <img src="pesantren_pendaftaran/static/src/img/PAGE3.e3b6d704.png" alt="Image" class="rounded-custom img-fluid" />
                </div>
                <div class="col-md-6 col-sm-12">
                    <h3 class="fw-bold"><span class="text-primary ">Informasi</span> Pelayanan Pendaftaran</h3>
                    <div class="accordion" id="accordionExample">
                    <div class="accordion-item mb-3">
                        <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne"
                            aria-expanded="true" aria-controls="collapseOne">
                            Pembukaan Pendaftaran:
                        </button>
                        </h2>
                        <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne"
                        data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <p class="m-0">Tanggal:</p>
                            <p class="fw-bold">{tgl_mulai_pendaftaran_formatted} s.d {tgl_akhir_pendaftaran_formatted}</p>
                        </div>
                        </div>
                    </div>
                    <div class="accordion-item mb-3">
                        <h2 class="accordion-header" id="headingTwo">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                            Verifikasi Berkas:
                        </button>
                        </h2>
                        <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo"
                        data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <!-- Konten untuk Verifikasi Berkas -->
                            <p class="m-0">Tanggal:</p>
                            <p class="fw-bold">{tgl_mulai_verifikasi_berkas_formatted} s.d {tgl_akhir_verifikasi_berkas_formatted}</p>
                            <p class="m-0">Tempat Penerimaan:</p>
                            <p class="fw-bold">Pondok Pesantren Daarul Qur'an Istiqomah, {alamat_lengkap} </p>
                        </div>
                        </div>
                    </div>
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="headingThree">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                            Waktu Pelayanan:
                        </button>
                        </h2>
                        <div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree"
                        data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <!-- Konten untuk Waktu Pelayanan -->
                            <p class="m-0">Pagi:</p>
                            <p class="fw-bold">08.00 ~ 12.00 WIB</p>
                            <p class="m-0">Siang:</p>
                            <p class="fw-bold">13.00 ~ 16.00 WIB</p>
                        </div>
                        </div>
                    </div>
                    </div>
                </div>
                </div>
            </div>
            <!-- Informasi Pelayanan Pendaftaran end-->

            <!-- Footer -->
            <footer class="footer py-4">
                <div class="container">
                <div class="row text-white">
                    <div class="col-md-4">
                    <h5>Pondok Pesantren Daarul Qur’an Istiqomah</h5>
                    <p>
                        {alamat_lengkap} <br>
                    </p>
                    </div>
                    <div class="col-md-4">
                    <h5>Social Pages</h5>
                    <ul class="list-unstyled">
                        <li><a href="https://www.facebook.com/daquistiqomah?mibextid=ZbWKwL" class="text-white"><i class="bi bi-facebook"></i> Facebook</a></li>
                        <li><a href="https://www.instagram.com/dqimedia?igsh=NTVwdWlwd3o5MTF1" class="text-white"><i class="bi bi-instagram"></i> Instagram</a></li>
                        <li><a href="https://youtube.com/@dqimedia?si=6_A8Vr3nysaegI7B" class="text-white"><i class="bi bi-youtube"></i> Youtube</a></li>
                    </ul>
                    </div>
                    <div class="col-md-4">
                    <h5><i class="bi bi-telephone"></i> Pusat Layanan Informasi</h5>
                    <p>
                        0853-9051-1124 (Layanan Umum)
                    </p>
                    </div>
                </div>
                <div class="text-center text-white mt-4">
                    <hr class="border-white">
                    <p>©Copyright 2024 - Daarul Qur’an Istiqomah</p>
                </div>
                </div>
            </footer>
            
            <!-- Footer end -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
                integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
                crossorigin="anonymous"></script>

                <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
                <script>

                // Fungsi easing: Memulai lambat, kemudian cepat (Ease In Out Cubic)
                // function easeInOutCubic(t) {{
                //    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
                // }}

                // Fungsi untuk animasi menghitung dengan ancang-ancang yang lebih lama
                // function animateCount(elementId) {{
                //    const element = document.getElementById(elementId);
                //    const targetValue = parseInt(element.getAttribute('data-value'), 10);
                //    let currentValue = 0;

                    // Durasi animasi (ms)
                    // const duration = 2500; // Menambah durasi sedikit untuk memberi efek ancang-ancang yang lebih lama
                    // let startTime = null;

                    // Fungsi untuk update angka setiap frame
                    // function updateNumber(currentTime) {{
                    // if (!startTime) startTime = currentTime; // Inisialisasi waktu mulai animasi
                    // let elapsedTime = currentTime - startTime; // Waktu yang telah berlalu
                    // let progress = elapsedTime / duration; // Normalisasi progress waktu antara 0 dan 1

                    // if (progress > 1) progress = 1; // Membatasi progress agar tidak melebihi 1

                    // Membuat animasi "ancang-ancang" yang lebih lama
                    // let easingProgress = easeInOutCubic(progress);
                    // Memberikan sedikit "slow start" di awal untuk memperpanjang transisi awal
                    // let dynamicProgress = progress < 0.4 ? easingProgress * 0.6 : easingProgress; // 40% pertama lebih lambat

                    // Hitung nilai yang akan ditampilkan berdasarkan progress
                    // let increment = Math.floor(targetValue * dynamicProgress);

                    // Update nilai elemen
                    // element.textContent = increment;

                    // Jika progress sudah mencapai 100%, hentikan animasi
                    // if (progress < 1) {{
                    //    requestAnimationFrame(updateNumber);
                    //}}
                    //}}

                    // Mulai animasi dengan requestAnimationFrame
                    //requestAnimationFrame(updateNumber);
                //}}

                // Panggil fungsi untuk setiap elemen setelah halaman dimuat
                // document.addEventListener("DOMContentLoaded", () => {{
                    // animateCount("count-kuota");
                    // animateCount("count-pendaftar");
                    // animateCount("count-diterima");
                    // animateCount("count-sisa");
                //}});

                function easeInOutCubic(t) {{
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
}}

function animateCount(elementId, targetValue) {{
    const element = document.getElementById(elementId);
    let currentValue = parseInt(element.textContent, 10) || 0;

    const duration = 2500; // Durasi animasi (ms)
    let startTime = null;

    function updateNumber(currentTime) {{
        if (!startTime) startTime = currentTime;
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        const dynamicValue = currentValue + (targetValue - currentValue) * easeInOutCubic(progress);

        element.textContent = Math.round(dynamicValue);

        if (progress < 1) {{
            requestAnimationFrame(updateNumber);
        }}
    }}

    requestAnimationFrame(updateNumber);
}}




                </script>
            </body>

            </html>
        """
        return request.make_response(html_content)

class PesantrenPendaftaran(http.Controller):
    @http.route('/psb', auth='public')
    def index(self, **kw):

        # Ambil nilai dari field konfigurasi
        config_obj = http.request.env['ir.config_parameter'].sudo()

        tgl_mulai_pendaftaran = config_obj.get_param('pesantren_pendaftaran.tgl_mulai_pendaftaran')
        tgl_akhir_pendaftaran = config_obj.get_param('pesantren_pendaftaran.tgl_akhir_pendaftaran')
        tgl_mulai_seleksi = config_obj.get_param('pesantren_pendaftaran.tgl_mulai_seleksi')
        tgl_akhir_seleksi = config_obj.get_param('pesantren_pendaftaran.tgl_akhir_seleksi')
        tgl_pengumuman_hasil_seleksi = config_obj.get_param('pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi')
        is_halaman_pendaftaran = config_obj.get_param('pesantren_pendaftaran.is_halaman_pendaftaran')
        is_halaman_pengumuman = config_obj.get_param('pesantren_pendaftaran.is_halaman_pengumuman')

        # Set nilai default dinamis jika parameter kosong
        if not tgl_mulai_pendaftaran:
            tgl_mulai_pendaftaran_dt = datetime.datetime.now() + datetime.timedelta(days=1)
            tgl_mulai_pendaftaran = tgl_mulai_pendaftaran_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_mulai_pendaftaran_dt = datetime.datetime.strptime(tgl_mulai_pendaftaran, '%Y-%m-%d %H:%M:%S')

        if not tgl_akhir_pendaftaran:
            tgl_akhir_pendaftaran_dt = tgl_mulai_pendaftaran_dt + datetime.timedelta(days=3)
            tgl_akhir_pendaftaran = tgl_akhir_pendaftaran_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_akhir_pendaftaran_dt = datetime.datetime.strptime(tgl_akhir_pendaftaran, '%Y-%m-%d %H:%M:%S')

        if not tgl_mulai_seleksi:
            tgl_mulai_seleksi_dt = tgl_akhir_pendaftaran_dt
            tgl_mulai_seleksi = tgl_mulai_seleksi_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_mulai_seleksi_dt = datetime.datetime.strptime(tgl_mulai_seleksi, '%Y-%m-%d %H:%M:%S')

        if not tgl_akhir_seleksi:
            tgl_akhir_seleksi_dt = tgl_mulai_seleksi_dt + datetime.timedelta(days=3)
            tgl_akhir_seleksi = tgl_akhir_seleksi_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_akhir_seleksi_dt = datetime.datetime.strptime(tgl_akhir_seleksi, '%Y-%m-%d %H:%M:%S')

        if not tgl_pengumuman_hasil_seleksi:
            tgl_pengumuman_hasil_seleksi_dt = tgl_akhir_seleksi_dt + datetime.timedelta(days=2)
            tgl_pengumuman_hasil_seleksi = tgl_pengumuman_hasil_seleksi_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tgl_pengumuman_hasil_seleksi_dt = datetime.datetime.strptime(tgl_pengumuman_hasil_seleksi, '%Y-%m-%d %H:%M:%S')

        # Format tanggal manual dalam bahasa Indonesia
        def format_tanggal_manual(dt):
            bulan_indonesia = [
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            return f"{dt.day} {bulan_indonesia[dt.month - 1]} {dt.year}"

        # Format tanggal untuk ditampilkan di halaman
        tgl_mulai_pendaftaran_formatted = format_tanggal_manual(tgl_mulai_pendaftaran_dt)
        tgl_akhir_pendaftaran_formatted = format_tanggal_manual(tgl_akhir_pendaftaran_dt)
        tgl_mulai_seleksi_formatted = format_tanggal_manual(tgl_mulai_seleksi_dt)
        tgl_akhir_seleksi_formatted = format_tanggal_manual(tgl_akhir_seleksi_dt)
        tgl_pengumuman_hasil_seleksi_formatted = format_tanggal_manual(tgl_pengumuman_hasil_seleksi_dt)


        html_response = f"""
            <!DOCTYPE html>
<html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>PSB - Daarul Qur'an Istiqomah</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
                <link href=" https://cdn.jsdelivr.net/npm/sweetalert2@11.14.5/dist/sweetalert2.min.css " rel="stylesheet">
                <style>

                    body {{
                        background: linear-gradient(to bottom left, #065c5c 18%, #f5e505 100%) !important;
                    }}

                    .offcanvas.offcanvas-end {{
                        
                        width: 250px; /* Lebar kustom untuk offcanvas */
                    }}
                    
                    .offcanvas .nav-link {{
                        color: #ffffff; /* teks warna putih */
                    }}
                    
                    .offcanvas .btn-close {{
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        filter: invert(1);
                    }}

                    .judul {{
                        height: 81px;
                        display: flex;
                        align-items: end;
                    }}

                    .teks-judul {{
                        height: 72px;
                    }}

                    .background {{
					    background: linear-gradient(to bottom left, #065c5c 18%, #f5e505 100%) !important;
					}}

					a.effect {{
						transition: .1s !important;
					}}

					a.effect:hover {{
						box-shadow: 0 3px 10px rgba(0,0,0,0.2) !important;
					}}

                    /* Desain Dropdown */
                    .dropdown {{
                        position: relative;
                    }}

                    .dropdown-link {{
                        cursor: pointer;
                    }}

                    .dropdown-content {{
                        display: none;
                        position: absolute;
                        top: 100%;
                        right: 0;
                        background-color: #ffffff;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                        border-radius: 5px;
                        min-width: 150px;
                        z-index: 1;
                        overflow: hidden;
                    }}

                    .dropdown-content a {{
                        color: #333;
                        padding: 10px 15px;
                        display: block;
                        text-decoration: none;
                        transition: background-color 0.2s;
                    }}

                    .dropdown-content a:hover {{
                        background-color: #f1f1f1;
                    }}

                    /* Menampilkan dropdown saat hover */
                    .dropdown:hover .dropdown-content {{
                        display: block;
                        animation: fadeIn 0.3s;
                    }}

                    #daftar {{
                        transition: .3s;
                    }}

                    #daftar:hover {{ 
                        background-color: #f5407d !important;
                    }}

                    /* Animasi fade-in */
                    @keyframes fadeIn {{
                        from {{
                        opacity: 0;
                        transform: translateY(-10px);
                        }}
                        to {{
                        opacity: 1;
                        transform: translateY(0);
                        }}
                    }}

                </style>
            </head>
            <body>

            <nav class="navbar navbar-expand-lg" style="height: 65px;">
                <div class="container-fluid">
                    <a class="navbar-brand ms-5 text-white fw-semibold" href="/psb">
                    	<img src="https://i.ibb.co.com/SmWmBTW/SAVE-20220114-075750-removebg-preview-4.png" alt="1731466812700" width="50" alt="Logo Pesantren">       Daarul Qur'an Istiqomah
                	</a>
                    <button class="navbar-toggler ms-auto" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar" aria-controls="offcanvasNavbar">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item me-3">
                                <a class="nav-link text-white" href="/psb"><i class="fa-solid fa-house me-2"></i>Beranda</a>
                            </li>
                            {f'<li class="nav-item me-3">'
                            f'<a class="nav-link text-white" href="/pendaftaran" {"data-bs-toggle='modal' data-bs-target='#modalPendaftaranTutup'" if not is_halaman_pendaftaran else ""}>'
                            f'<i class="fa-solid fa-note-sticky me-2"></i>Pendaftaran</a>'
                            f'</li>'}
                            <li class="nav-item dropdown">
                                <a href="#" class="dropdown-link nav-link"
                                    style="color: white !important;">
                                    <i class="fa-solid fa-fingerprint me-2"></i>Login</a>
                                <div class="dropdown-content">
                                    <a href="/login">Login PSB</a>
                                    <a href="/web/login">Login Orang Tua</a>
                                </div>
                            </li>
                            <li class="nav-item me-3">
                                <a class="nav-link text-white" href="/bantuan"><i class="fa-solid fa-lock me-2"></i>Bantuan</a>
                            </li>
                            {f'<li class="nav-item dropdown">'
                            f'<a href="#" class="dropdown-link nav-link text-white"><i class="fa-solid fa-bullhorn me-2"></i>Pengumuman</a>'
                            f'<div class="dropdown-content">'
                            f'<a href="/pengumuman/sd-mi">SD / MI</a>'
                            f'<a href="/pengumuman/smp-mts">SMP / MTS</a>'
                            f'<a href="/pengumuman/sma-ma">SMA / MA</a>'
                            f'</div>'
                            f'</li>' if is_halaman_pengumuman else ''}
                        </ul>
                    </div>
                </div>
            </nav>

            <div class="offcanvas offcanvas-end background" tabindex="-1" id="offcanvasNavbar" aria-labelledby="offcanvasNavbarLabel">
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas" aria-label="Close"></button>
                <a class="navbar-brand mt-1 text-white fw-semibold" href="/psb" style="display: flex; flex-direction: column; align-items: center;">
                    <img src="https://i.ibb.co.com/SmWmBTW/SAVE-20220114-075750-removebg-preview-4.png" alt="1731466812700" width="50" alt="Logo Pesantren">
                    Daarul Qur'an Istiqomah
                </a>
                <div class="offcanvas-body">
                    <ul class="navbar-nav justify-content-end flex-grow-1 pe-3">
                        <li class="nav-item me-3">
                            <a class="nav-link text-white" href="/psb"><i class="fa-solid fa-house me-2"></i>Beranda</a>
                        </li>
                        {f'<li class="nav-item me-3">'
                        f'<a class="nav-link text-white" href="/pendaftaran" {"data-bs-toggle='modal' data-bs-target='#modalPendaftaranTutup'" if not is_halaman_pendaftaran else ""}>'
                        f'<i class="fa-solid fa-note-sticky me-2"></i>Pendaftaran</a>'
                        f'</li>'}
                        <li class="nav-item dropdown">
                            <a href="#" class="dropdown-link nav-link"
                                style="color: white !important;">
                                <i class="fa-solid fa-fingerprint me-2"></i>Login</a>
                            <div class="dropdown-content">
                                <a href="/login">Login PSB</a>
                                <a href="/web/login">Login Orang Tua</a>
                            </div>
                        </li>
                        <li class="nav-item me-3">
                            <a class="nav-link text-white" href="/bantuan"><i class="fa-solid fa-lock me-2"></i>Bantuan</a>
                        </li>
                        {f'<li class="nav-item dropdown">'
                        f'<a href="#" class="dropdown-link nav-link text-white"><i class="fa-solid fa-bullhorn me-2"></i>Pengumuman</a>'
                        f'<div class="dropdown-content">'
                        f'<a href="/pengumuman/sd-mi">SD / MI</a>'
                        f'<a href="/pengumuman/smp-mts">SMP / MTS</a>'
                        f'<a href="/pengumuman/sma-ma">SMA / MA</a>'
                        f'</div>'
                        f'</li>' if is_halaman_pengumuman else ''}
                    </ul>
                </div>
            </div>

            <div style="display: flex; justify-content: center;" class="mt-5">
                <div class="text-center text-white">
                    <h4 class="fs-2 fw-semibold mb-2">Aplikasi penerimaan santri baru</h4>
                    <span>Daarul Qur'an Istiqomah Tanah Laut Kalimantan Selatan</span> <br><br>
                    {f'<a href="/pendaftaran" {"data-bs-toggle='modal' data-bs-target='#modalPendaftaranTutup'" if not is_halaman_pendaftaran else ""} style="background-color: #e91e63; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px;" class=" id="daftar">Daftar Sekarang</a>'}
                </div>
            </div>

            <div class="container mt-5 mb-5">
                <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
                    <div class="bg-white shadow-lg rounded p-3" style="width: 270px; display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
                        <span class="text-uppercase text-secondary mb-3">Program Pendidikan</span>
                        <div>
                            <i class="fa-solid fa-graduation-cap fs-1 border rounded-circle p-5" style="color: #e91e63 !important;"></i>
                        </div>
                        <span class="text-uppercase text-center fs-3 judul">Jenjang Pendidikan</span>
                        <div class="text-center mb-4 teks-judul">
                            <span class="text-secondary" style="font-size: 14px;">1. Paud baby Qu (KB dan TK)</span>
                            <span class="text-secondary" style="font-size: 14px;">2. SD Tahfizh bilingual</span>
                            <span class="text-secondary" style="font-size: 14px;">3. SMP Tahfizh bilingual</span>
                            <span class="text-secondary" style="font-size: 14px;">4. MA Tahfizh bilingual</span>
                        </div>
                        <div class="text-uppercase">
                            <a href="" data-bs-toggle="modal" data-bs-target="#detailProgramPendidikan" class="effect" style="background-color: #9F1FB2 !important; padding: 10px 20px; border-radius: 20px; text-decoration: none; color: white;">Detail</a>
                        </div>
                    </div>
                    <div class="bg-white shadow-lg rounded p-3" style="width: 270px; display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
                        <span class="text-uppercase text-secondary mb-3">Jadwal Kegiatan</span>
                        <div>
                            <i class="fa-regular fa-calendar fs-1 border rounded-circle p-5" style="color: #e91e63 !important;"></i>
                        </div>
                        <span class="text-uppercase fs-3 judul">Jadwal Kegiatan</span>
                        <div class="text-center mb-4 teks-judul">
                            <span class="text-secondary" style="font-size: 14px;">Jadwal kegiatan PSB dan Kuota Test </span>
                        </div>
                        <div class="text-uppercase">
                            <a href="" data-bs-toggle="modal" data-bs-target="#detailJadwalKegiatan" class="effect" style="background-color: #9F1FB2 !important; padding: 10px 20px; border-radius: 20px; text-decoration: none; color: white;">Detail</a>
                        </div>
                    </div>
                    <div class="bg-white shadow-lg rounded p-3" style="width: 270px; display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
                        <span class="text-uppercase text-secondary mb-3">Persyaratan</span>
                        <div>
                            <i class="fa-solid fa-clipboard-list fs-1 border rounded-circle p-5" style="color: #e91e63 !important;"></i>
                        </div>
                        <span class="text-uppercase fs-3 text-center judul">Syarat pendaftaran</span>
                        <div class="text-center mb-4 teks-judul">
                            <span class="text-secondary" style="font-size: 14px;">Persyaratan Pendaftaran dapat dilihat disini</span>
                        </div>
                        <div class="text-uppercase">
                            <a href="" data-bs-toggle="modal" data-bs-target="#detailPersyaratan" class="effect" style="background-color: #9F1FB2 !important; padding: 10px 20px; border-radius: 20px; text-decoration: none; color: white;">Detail</a>
                        </div>
                    </div>
                    <div class="bg-white shadow-lg rounded p-3" style="width: 270px; display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
                        <span class="text-uppercase text-secondary mb-3">Bantuan</span>
                        <div>
                            <i class="fa-solid fa-lock fs-1 border rounded-circle p-5" style="color: #e91e63 !important;"></i>
                        </div>
                        <span class="text-uppercase fs-3 judul">Hubungi Kami</span>
                        <div class="text-center mb-4 teks-judul">
                            <span class="text-secondary" style="font-size: 14px;">Jika memerlukan bantuan : Telp / WA : 0853-9051-1124 </span>
                        </div>
                        <div class="text-uppercase">
                            <a href="/bantuan" class="effect" style="background-color: #9F1FB2 !important; padding: 10px 20px; border-radius: 20px; text-decoration: none; color: white;">Detail</a>
                        </div>
                    </div>
                </div>
                
            </div>

            <footer class="text-white p-2" style="display: flex; justify-content: space-between; flex-wrap: wrap;">
            	<div class="ms-5">
            		<ul style="list-style-type: none; display: flex; text-transform: uppercase; font-size: 13px;" class="fw-semibold">
            			<li><a href="/psb" class="me-4" style="text-decoration: none; color: white;">Home</a></li>
            			<li><a href="/beranda" class="me-4" style="text-decoration: none; color: white;" target="_blank">Info Pondok</a></li>
            			<li><a href="https://drive.google.com/drive/folders/1KxQ0V4bd7RpSFqJKJfQ6JGn1z2-Ld7Wr" class="me-4" style="text-decoration: none; color: white;" target="_blank">Brosur</a></li>
            			<li><a href="" class="me-4" style="text-decoration: none; color: white;">Panduan</a></li>
            		</ul>
            	</div>
            	<div class="me-5">
            		<p class="text-center mt-1">© 2024 TIM IT PPIB</p>
            	</div>
            </footer>


            <div class="modal fade" id="detailProgramPendidikan" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5 text-secondary" id="exampleModalLabel">Pendaftaran Santri Baru</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
<div class="modal-body">
                    <div class="row mb-3">
                        <div class="col-md-8">
                            <div>
                                <span class="fw-semibold">PEMBUKAAN PROGRAM PENDIDIKAN (Putra dan Putri)</span>
                                <ul class="text-secondary">                                   
                                    <li>KB (2 - 3tahun)</li>
                                    <li>TK ( 4 - 5tahun)</li>
                                    <li>SD Tahfizh Bilinglual</li>
                                    <li>SMP Tahfizh bilingual</li>
                                    <li>MA Tahfizh bilingual</li>
                                </ul>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <img src="https://i.ibb.co.com/wRNC9B0/img1.jpg" alt="Gambar Pondok" width="150"
                                class="rounded">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-8">
                            <div>
                                <span class="fw-semibold">PELAKSANAAN TEST MASUK</span>
                                <p class="text-secondary">Seluruh test dilaksanakan dalam 2 Gelombang <br>
                                    Test
                                    dilaksanakan secara OFFLINE</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <img src="https://i.ibb.co.com/hW8F8Qs/img2.jpg" alt="Gambar Pondok" width="150"
                                class="rounded">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-8">
                            <div>
                                <span class="fw-semibold">MATERI UJIAN SELEKSI</span>
                                <ul>
                                    <li>Membaca Al Qur’an dan Tulis Arab</li>
                                    <li>Tes wawancara anak dan wawancara orangtua</li>
                                </ul>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <img src="https://i.ibb.co.com/jZznN6Q/img3.jpg" alt="Gambar Pondok" width="150"
                                class="rounded">
                        </div>
                    </div>
                </div>
                </div>
            </div>
            </div>

<div class="modal fade" id="detailJadwalKegiatan" tabindex="-1" aria-labelledby="exampleModalLabel"
        aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5 text-secondary" id="exampleModalLabel">Jadwal Pelaksanaan PSB</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row mb-3">
                        <div class="col-md-8">
                            <div>
                                <span class="fw-semibold">1. Pendaftaran Online</span>
                                <p class="text-secondary">Pendaftaran dilaksanakan pada: <br>
                                        Gel 1: {tgl_mulai_pendaftaran_formatted} - {tgl_akhir_pendaftaran_formatted} <br>
                                        Gel 2: {tgl_mulai_pendaftaran_formatted} - {tgl_akhir_pendaftaran_formatted} <br> melalui website <a href="/pendaftaran"
                                    class="text-decoration-none text-primary">https://aplikasi.dqi.ac.id/psb</a></p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <img src="https://i.ibb.co.com/KKKwWG1/img4.jpg" alt="Gambar Pondok" width="150"
                                class="rounded">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-8">
                            <div>
                                <span class="fw-semibold">2. Pelaksanaan Test Masuk</span>
                                <p class="text-secondary">Gel 1: {tgl_mulai_seleksi_formatted} - {tgl_akhir_seleksi_formatted} <br> Gel 2: {tgl_mulai_seleksi_formatted} - {tgl_akhir_seleksi_formatted} <br> (Test seleksi dilaksanakan secara ONLINE dengan
                                    kuota
                                    sebanyak 100 peserta per hari).</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <img src="https://i.ibb.co.com/s9g5nM2/img5.jpg" alt="Gambar Pondok" width="150"
                                class="rounded">
                        </div>
                    </div>
                    <div>
                        <span class="fw-semibold">4. Pengumuman Hasil Seleksi</span>
                        <p class="text-secondary">Gel 1: {tgl_pengumuman_hasil_seleksi_formatted} <br>
                                                Gel 2: {tgl_pengumuman_hasil_seleksi_formatted}
                        </p>
                    </div>
                    <div>
                        <p class="text-secondary">Catatan : Seluruh kegiatan akan mengikuti protokol kesehatan sesuai
                            ketentuan dari pemerintah.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="modal fade" id="detailPersyaratan" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5 text-secondary" id="exampleModalLabel">Persyaratan Test Masuk</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row mb-3">
                        <div class="col-md-12">
                            <div>
                                <span class="fw-semibold">SYARAT UTAMA PENDAFTARAN :</span>
                                <ol class="text-secondary">
                                    <li>Mengisi formulir online secara lengkap dan benar melalui laman https://dqi.ac.id/psb</li>
                                    <li>Membayar biaya pendaftran untuk program Paud baby Qu KB A & B(usia 2 - 3th) sebesar Rp.350.000</li>
                                    <li>Membayar biaya pendaftran untuk program TK sebesar Rp.300.000</li>
                                    <li>Membayar biaya pendaftran untuk program SD Tahfizh bilingual sebesar Rp.300.000</li>
                                    <li>Membayar biaya pendaftran untuk program SMP Tahfizh bilingual sebesar Rp.300.000</li>
                                    <li>Membayar biaya pendaftran untuk program MA Tahfizh bilingual sebesar Rp.300.000</li>
                                    <li>
                                        Syarat Pendaftaran :
                                        <ul type="disc" class="text-secondary">
                                            <li>Fotocopy Akta Kelahiran 2 lembar</li>
                                            <li>Fotocopy KK 1 lembar</li>
                                            <li>Fotocopy KTP Orangtua (Masing-masing 1 lembar)</li>
                                            <li>Fotocopy Raport Semester akhir (menyusul)</li>
                                            <li>Pas Foto berwarna ukuran 3x4 4lembar</li>
                                            <li>Pas Foto Orangtua masing-masing 1lembar (Khusus Pendaftar KB dan TK)</li>
                                            <li>Berkas dimasukkan dalam Map warna hijau dan diberi nama serta lembaga pendidikan</li>
                                        </ul>
                                    </li>
                                </ol>
                            </div>
                        </div>
                    </div>
                    <div>
                        <p class="text-secondary">Seluruh persyaratan yang harus di upload / diunggah ke website
                            pendaftaran
                            harus sesuai format yang ditentukan</p>
                    </div>
                </div>
                </div>
            </div>
            </div>


                        <!-- Modal -->
            <div class="modal fade" id="modalPendaftaranTutup" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="exampleModalLabel">Pendaftaran ditutup!</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Mohon maaf, pendaftaran telah ditutup.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Tutup</button>
                </div>
                </div>
            </div>
            </div>



            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
            <script src=" https://cdn.jsdelivr.net/npm/sweetalert2@11.14.5/dist/sweetalert2.all.min.js "></script>


            </body>
            </html>
        """

        return request.make_response(html_response)
    

class UbigPendaftaranController(http.Controller):
    @http.route('/pendaftaran', type='http', auth='public')
    def pendaftaran_form(self, **kwargs):

        # Mengambil nilai kuota pendaftaran dari ir.config_parameter
        config_param = request.env['ir.config_parameter'].sudo()
        is_halaman_pengumuman = config_param.get_param('pesantren_pendaftaran.is_halaman_pengumuman')

        pendidikan_list = request.env['ubig.pendidikan'].sudo().search([])
        return request.render('pesantren_pendaftaran.pendaftaran_form_template', {
            'pendidikan_list': pendidikan_list,
            'is_halaman_pengumuman': is_halaman_pengumuman,
        })

    @http.route('/pendaftaran/submit', type='http', auth='public', methods=['POST'], csrf=True)
    def pendaftaran_submit(self, **post):

        # Ambil data dari form
        # kode_akses             = post.get('kode_akses')
        nama                   = post.get('nama')
        nik                    = post.get('nik')
        email                  = post.get('email')
        password               = post.get('password')
        jenjang_id             = post.get('jenjang_id')
        gender                 = request.params.get('gender')
        kota_lahir             = post.get('kota_lahir')
        tanggal_lahir_str      = request.params.get('tanggal_lahir')
        # Mengonversi format tanggal dd/mm/yyyy menjadi date
        tanggal_lahir          = datetime.datetime.strptime(tanggal_lahir_str, '%d/%m/%Y').date()
        alamat                 = post.get('alamat')
        provinsi_id            = request.params.get('provinsi_id')
        kota_id                = request.params.get('kota_id')
        kecamatan_id           = request.params.get('kecamatan_id')
        golongan_darah         = request.params.get('golongan_darah') if request.params.get('golongan_darah') else ''
        kewarganegaraan        = request.params.get('kewarganegaraan')
        nisn                   = post.get('nisn') if post.get('nisn') else ''
        anak_ke                = post.get('anak_ke') if post.get('anak_ke') else ''
        jml_saudara_kandung    = post.get('jml_saudara_kandung') if post.get('jml_saudara_kandung') else ''
        cita_cita              = post.get('cita_cita') if post.get('cita_cita') else ''

        # Data Orang Tua - Ayah
        nama_ayah              = post.get('nama_ayah')
        ktp_ayah               = post.get('ktp_ayah')
        tanggal_lahir_ayah_str = request.params.get('tanggal_lahir_ayah')
        # Mengonversi format tanggal dd/mm/yyyy menjadi date
        tanggal_lahir_ayah     = datetime.datetime.strptime(tanggal_lahir_ayah_str, '%d/%m/%Y').date()
        telepon_ayah           = post.get('telepon_ayah')
        pekerjaan_ayah         = request.params.get('pekerjaan_ayah')
        penghasilan_ayah       = request.params.get('penghasilan_ayah')
        # email_ayah             = post.get('email_ayah')
        kewarganegaraan_ayah   = request.params.get('kewarganegaraan_ayah')
        pendidikan_ayah        = request.params.get('pendidikan_ayah')

        # Data Orang Tua - Ibu
        nama_ibu               = post.get('nama_ibu')
        ktp_ibu                = post.get('ktp_ibu')
        tanggal_lahir_ibu_str  = request.params.get('tanggal_lahir_ibu')
        # Mengonversi format tanggal dd/mm/yyyy menjadi date
        tanggal_lahir_ibu      = datetime.datetime.strptime(tanggal_lahir_ibu_str, '%d/%m/%Y').date()
        telepon_ibu            = post.get('telepon_ibu')
        pekerjaan_ibu          = request.params.get('pekerjaan_ibu')
        penghasilan_ibu        = request.params.get('penghasilan_ibu')
        # email_ibu              = post.get('email_ibu')
        kewarganegaraan_ibu    = request.params.get('kewarganegaraan_ibu')
        pendidikan_ibu         = request.params.get('pendidikan_ibu')
        
        # Data Wali
        wali_nama              = post.get('wali_nama') if post.get('wali_nama') else ''

        # Mendapatkan nilai tanggal lahir dari parameter
        wali_tgl_lahir_str = request.params.get('wali_tgl_lahir')

        # Mengecek apakah parameter tidak kosong atau tidak None
        if wali_tgl_lahir_str:
            try:
                # Mengonversi format tanggal dd/mm/yyyy menjadi date
                wali_tgl_lahir = datetime.datetime.strptime(wali_tgl_lahir_str, '%d/%m/%Y').date()
            except ValueError:
                # Jika format tanggal tidak valid
                wali_tgl_lahir = None  # Atau bisa beri nilai default seperti datetime.date(1900, 1, 1) atau lainnya
        else:
            # Jika tidak ada input tanggal
            wali_tgl_lahir = None  # Atau beri nilai default jika diperlukan

        # wali_tgl_lahir_str     = request.params.get('wali_tgl_lahir')
        # Mengonversi format tanggal dd/mm/yyyy menjadi date
        # wali_tgl_lahir         = datetime.datetime.strptime(wali_tgl_lahir_str, '%d/%m/%Y').date()
        wali_telp              = post.get('wali_telp') if post.get('wali_telp') else ''
        wali_email             = post.get('wali_email') if post.get('wali_email') else ''
        # wali_password          = post.get('password') if post.get('password') else ''
        wali_hubungan          = request.params.get('wali_hubungan') if request.params.get('wali_hubungan') else ''

        # Data Pendidikan
        asal_sekolah           = post.get('asal_sekolah') if post.get('asal_sekolah') else ''
        alamat_asal_sek        = post.get('alamat_asal_sek') if post.get('alamat_asal_sek') else ''
        telp_asal_sek          = post.get('telp_asal_sek') if post.get('telp_asal_sek') else ''
        status_sekolah_asal    = request.params.get('status_sekolah_asal') if request.params.get('status_sekolah_asal') else ''
        npsn                   = post.get('npsn') if post.get('npsn') else ''

        # Ambil file dari request
        uploaded_files = request.httprequest.files

        # Data Berkas
        # akta_kelahiran         = request.params.get('akta_kelahiran')
        # kartu_keluarga         = request.params.get('kartu_keluarga')
        # ijazah                 = request.params.get('ijazah') if request.params.get('ijazah') else ''
        # surat_kesehatan        = request.params.get('surat_kesehatan') if request.params.get('surat_kesehatan') else ''
        # pas_foto               = request.params.get('pas_foto')
        # raport_terakhir        = request.params.get('raport_terakhir') if request.params.get('raport_terakhir') else ''
        # ktp_ortu               = request.params.get('ktp_ortu')
        # skhun                  = request.params.get('skhun') if request.params.get('skhun') else ''

        # Ambil setiap file, konversi ke Base64, dan proses
        akta_kelahiran = uploaded_files.get('akta_kelahiran')
        kartu_keluarga = uploaded_files.get('kartu_keluarga')
        ijazah = uploaded_files.get('ijazah')
        surat_kesehatan = uploaded_files.get('surat_kesehatan')
        pas_foto = uploaded_files.get('pas_foto')
        raport_terakhir = uploaded_files.get('raport_terakhir')
        ktp_ortu = uploaded_files.get('ktp_ortu')
        skhun = uploaded_files.get('skhun')

        # Fungsi bantu untuk memproses file
        def process_file(file):
            if file:
                # Baca file dan konversi ke Base64
                file_content = file.read()
                file_base64 = base64.b64encode(file_content)
                return file_base64
            return None

        # Konversi file yang diunggah
        akta_kelahiran_b64 = process_file(akta_kelahiran)
        kartu_keluarga_b64 = process_file(kartu_keluarga)
        ijazah_b64 = process_file(ijazah)
        surat_kesehatan_b64 = process_file(surat_kesehatan)
        pas_foto_b64 = process_file(pas_foto)
        raport_terakhir_b64 = process_file(raport_terakhir)
        ktp_ortu_b64 = process_file(ktp_ortu)
        skhun_b64 = process_file(skhun)

        wali_terdaftar = request.env['ubig.pendaftaran'].sudo().search([('wali_email', '=', wali_email)])

        # if wali_terdaftar:
        #     kode_akses = wali_terdaftar[0].kode_akses

        # Simpan data ke model ubig.pendaftaran
        pendaftaran = request.env['ubig.pendaftaran'].sudo().create({
            # 'kode_akses'             : kode_akses,
            'name'                   : nama,
            'nik'                    : nik,
            'email'                  : email,
            'password'               : password,
            'jenjang_id'             : int(jenjang_id),
            'gender'                 : gender,
            'kota_lahir'             : kota_lahir,
            'tanggal_lahir'          : tanggal_lahir,
            'alamat'                 : alamat,
            'provinsi_id'            : provinsi_id,
            'kota_id'                : kota_id,
            'kecamatan_id'           : kecamatan_id,
            'golongan_darah'         : golongan_darah,
            'kewarganegaraan'        : kewarganegaraan,
            'nisn'                   : nisn,
            'anak_ke'                : anak_ke,
            'jml_saudara_kandung'    : jml_saudara_kandung,
            'cita_cita'              : cita_cita,

            # Data Orang Tua - Ayah
            'nama_ayah'              : nama_ayah,
            'ktp_ayah'               : ktp_ayah,
            'tanggal_lahir_ayah'     : tanggal_lahir_ayah,
            'telepon_ayah'           : telepon_ayah,
            'pekerjaan_ayah'         : pekerjaan_ayah,
            'penghasilan_ayah'       : penghasilan_ayah,
            # 'email_ayah'             : email_ayah,
            'kewarganegaraan_ayah'   : kewarganegaraan_ayah,
            'pendidikan_ayah'        : pendidikan_ayah,

            # Data Orang Tua - Ibu
            'nama_ibu'               : nama_ibu,
            'ktp_ibu'                : ktp_ibu,
            'tanggal_lahir_ibu'      : tanggal_lahir_ibu,
            'telepon_ibu'            : telepon_ibu,
            'pekerjaan_ibu'          : pekerjaan_ibu,
            'penghasilan_ibu'        : penghasilan_ibu,
            # 'email_ibu'              : email_ibu,
            'kewarganegaraan_ibu'    : kewarganegaraan_ibu,
            'pendidikan_ibu'         : pendidikan_ibu,
            
            # Data Wali
            'wali_nama'              : wali_nama,
            'wali_tgl_lahir'         : wali_tgl_lahir,
            'wali_telp'              : wali_telp,
            'wali_email'             : wali_email,
            # 'wali_password'          : wali_password,
            'wali_hubungan'          : wali_hubungan,

            # Data Pendidikan
            'asal_sekolah'           : asal_sekolah,
            'alamat_asal_sek'        : alamat_asal_sek,
            'telp_asal_sek'          : telp_asal_sek,
            'status_sekolah_asal'    : status_sekolah_asal,
            'npsn'                   : npsn,

            # Data Berkas
            'akta_kelahiran'         : akta_kelahiran_b64 if akta_kelahiran_b64 else False,
            'kartu_keluarga'         : kartu_keluarga_b64 if kartu_keluarga_b64 else False,
            'ijazah'                 : ijazah_b64 if ijazah_b64 else False,
            'surat_kesehatan'        : surat_kesehatan_b64 if surat_kesehatan_b64 else False,
            'pas_foto'               : pas_foto_b64 if pas_foto_b64 else False,
            'raport_terakhir'        : raport_terakhir_b64 if raport_terakhir_b64 else False,
            'ktp_ortu'               : ktp_ortu_b64 if ktp_ortu_b64 else False,
            'skhun'                  : skhun_b64 if skhun_b64 else False,
            'state'                  : 'draft'  # set status awal menjadi 'terdaftar'
        })

        token = pendaftaran.token

        # Redirect ke halaman sukses atau halaman lain yang diinginkan
        return request.redirect(f'/pendaftaran/success?token={token}')

    @http.route('/pendaftaran/success', type='http', auth='public')
    def pendaftaran_success(self, token=None, **kwargs):

        Pendaftaran = request.env['ubig.pendaftaran']

        # Mengambil nilai kuota pendaftaran dari ir.config_parameter
        config_param = request.env['ir.config_parameter'].sudo()
        is_halaman_pengumuman = config_param.get_param('pesantren_pendaftaran.is_halaman_pengumuman')
        no_rekening = config_param.get_param('pesantren_pendaftaran.no_rekening', default='7181863913')
        # Menangkap Token pendaftaran dari URL
        token = request.params.get('token')

        if not token:
            return request.not_found()

        # Cari pendaftaran berdasarkan token
        pendaftaran = Pendaftaran.sudo().search([('token', '=', token)], limit=1)
        if not pendaftaran:
            return request.not_found()

        # Kirim email
        if pendaftaran.email:
            # Contoh password (validasi minimal 8 karakter sudah dilakukan)
            password = pendaftaran.password

            # Sembunyikan bagian tengah kecuali dua karakter awal dan dua karakter akhir
            masked_password = password[:2] + '*' * (len(password) - 4) + password[-2:]
            biaya_formatted = f"Rp. {pendaftaran.biaya:,.0f}".replace(",", ".")

            email_values = {
                'subject': "Informasi Login Sistem Pesantren Daarul Qur'an Istiqomah",
                'email_to': pendaftaran.email,
                'body_html': f'''
                    <div style="background-color: #d9eaf7; padding: 20px; font-family: Arial, sans-serif;">
                        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                            <!-- Header -->
                            <div style="background-color: #0066cc; color: #ffffff; text-align: center; padding: 20px;">
                                <h1 style="margin: 0; font-size: 24px;">Pesantren Daarul Qur'an Istiqomah</h1>
                            </div>
                            <!-- Body -->
                            <div style="padding: 20px; color: #555555;">
                                <p style="margin: 0 0 10px;">Assalamualaikum Wr. Wb,</p>
                                <p style="margin: 0 0 20px;">
                                    Bapak/Ibu <strong>{pendaftaran.wali_nama}</strong>,<br>
                                    Akun Login telah dibuat di sistem pesantren kami. Berikut adalah informasi login Anda:
                                </p>
                                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                    <h3>Akun Login</h3>
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">Email :</td>
                                            <td style="padding: 8px; color: #555555;">{pendaftaran.email}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">Kata Sandi :</td>
                                            <td style="padding: 8px; color: #555555;">{masked_password}</td>
                                        </tr>
                                    </table>

                                    <h3>Data Pendaftaran</h3>
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">Nama :</td>
                                            <td style="padding: 8px; color: #555555;">{pendaftaran.partner_id.name}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">TTL :</td>
                                            <td style="padding: 8px; color: #555555;">{pendaftaran.kota_lahir}, {pendaftaran.get_formatted_tanggal_lahir()}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">Alamat :</td>
                                            <td style="padding: 8px; color: #555555;">{pendaftaran.alamat}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">NIK :</td>
                                            <td style="padding: 8px; color: #555555;">{pendaftaran.nik}</td>
                                        </tr>
                                    </table>

                                    <h3>Jenjang Pendidikan Yang Dipilih</h3>
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">Jenjang :</td>
                                            <td style="padding: 8px; color: #555555;">{pendaftaran.jenjang_id.name}</td>
                                        </tr>
                                    </table>

                                    <h3>Informasi Pembayaran</h3>
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">Bank :</td>
                                            <td style="padding: 8px; color: #555555;">BSI</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">Nomor Rekening :</td>
                                            <td style="padding: 8px; color: #555555;">{no_rekening}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px; font-weight: bold; color: #333333;">Sejumlah :</td>
                                            <td style="padding: 8px; color: #555555;">{biaya_formatted}</td>
                                        </tr>
                                    </table>

                                </div>
                                <p style="text-align: center;">
                                    <a href="https://aplikasi.dqi.ac.id/login" style="background-color: #0066cc; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                                        Masuk Ke Akun Anda
                                    </a>
                                </p>
                                <p style="margin: 20px 0;">
                                    Apabila terdapat kesulitan atau membutuhkan bantuan, silakan hubungi tim teknis kami melalui nomor:
                                </p>
                                <ul style="margin: 0; padding-left: 20px; color: #555555;">
                                    <li>0822 5207 9785</li>
                                    <li>0853 9051 1124</li>
                                </ul>
                                <p style="margin: 20px 0;">
                                    Kami berharap portal ini dapat membantu Bapak/Ibu memantau perkembangan putra/putri selama berada di pesantren.
                                </p>
                            </div>
                            <!-- Footer -->
                            <div style="background-color: #f1f1f1; text-align: center; padding: 10px;">
                                <p style="font-size: 12px; color: #888888; margin: 0;">
                                    &copy; 2024 Pesantren Tahfizh Daarul Qur'an Istiqomah. All rights reserved.
                                </p>
                            </div>
                        </div>
                    </div>
                ''',
            }

            mail = request.env['mail.mail'].sudo().create(email_values)
            mail.send()

        return request.render('pesantren_pendaftaran.pendaftaran_success_template', {
            'pendaftaran': pendaftaran,
            'is_halaman_pengumuman': is_halaman_pengumuman,
            'no_rekening': no_rekening,
        })

class PesantrenCetakPembayaran(http.Controller):
    @http.route('/pendaftaran/cetak', type='http', auth='public')
    def pendaftaran_cetak(self, token=None, **kwargs):

        Pendaftaran = request.env['ubig.pendaftaran']

        # Mengambil nilai kuota pendaftaran dari ir.config_parameter
        config_param = request.env['ir.config_parameter'].sudo()
        no_rekening = config_param.get_param('pesantren_pendaftaran.no_rekening', default='7181863913')

        # Menangkap Token pendaftaran dari URL
        token = request.params.get('token')

        # Cek apakah Token ada
        if not token:
            return request.not_found()

        # Mengambil data pendaftaran berdasarkan Token
        pendaftaran = Pendaftaran.sudo().search([('token', '=', token)], limit=1)
        if not pendaftaran:
            return request.not_found()

        return request.render('pesantren_pendaftaran.pendaftaran_cetak_form_pembayaran_template', {
            'pendaftaran': pendaftaran,
            'no_rekening': no_rekening,
        })

class PesantrenPsbBantuan(http.Controller):
    @http.route('/bantuan', auth='public')
    def index(self, **kw):

        # Ambil nilai dari field konfigurasi
        config_obj = http.request.env['ir.config_parameter'].sudo()

        is_halaman_pengumuman = config_obj.get_param('pesantren_pendaftaran.is_halaman_pengumuman')
        is_halaman_pendaftaran = config_obj.get_param('pesantren_pendaftaran.is_halaman_pendaftaran')

        html_response = f"""
                <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Bantuan - Daarul Qur'an Istiqomah</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
                <link href=" https://cdn.jsdelivr.net/npm/sweetalert2@11.14.5/dist/sweetalert2.min.css " rel="stylesheet">


                <style>

                    body {{
                        background: linear-gradient(to bottom left, #065c5c 18%, #f5e505 100%) !important;
                    }}

                    .offcanvas.offcanvas-end {{
                        
                        width: 250px; /* Lebar kustom untuk offcanvas */
                    }}
                    
                    .offcanvas .nav-link {{
                        color: #ffffff; /* teks warna putih */
                    }}
                    
                    .offcanvas .btn-close {{
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        filter: invert(1);
                    }}

                    .timeline {{
                        position: relative;
                        padding: 20px 0;
                    }}

                    .timeline::before {{
                        content: '';
                        position: absolute;
                        left: 5px;
                        top: 50px;
                        bottom: 0;
                        width: 4px;
                        background: white;
                    }}

                    .timeline-item {{
                        position: relative;
                        margin-left: 50px;
                        margin-bottom: 40px;
                    }}

                    .timeline-icon {{
                        position: absolute;
                        left: -63px;
                        top: 20px;
                        width: 40px;
                        height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 50%;
                        color: #fff;
                        font-size: 18px;
                        box-shadow: 0px 3px 20px rgba(0, 0, 0, 0.5);
                    }}

                    .timeline-icon::after {{
                        content: "";
                        position: absolute;
                        top: 50%;
                        left: 84%;  /* Mengarahkan panah ke ikon */
                        border-width: 15px;
                        border-style: solid;
                        border-color: transparent transparent transparent white;  /* Panah segitiga mengarah ke ikon */
                        transform: translateY(-50%) rotate(180deg);
                    }}

                    .timeline-content {{
                        padding: 20px;
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}

                    .judul {{
                        height: 81px;
                        display: flex;
                        align-items: end;
                    }}

                    .teks-judul {{
                        height: 72px;
                    }}

                    .background {{
                        background: linear-gradient(to bottom left, #065c5c 18%, #f5e505 100%) !important;
                    }}

                    a.effect {{
                        transition: .1s !important;
                    }}

                    a.effect:hover {{
                        box-shadow: 0 3px 10px rgba(0,0,0,0.2) !important;
                    }}

                    /* Desain Dropdown */
                    .dropdown {{
                        position: relative;
                    }}

                    .dropdown-link {{
                        cursor: pointer;
                    }}

                    .dropdown-content {{
                        display: none;
                        position: absolute;
                        top: 100%;
                        right: 0;
                        background-color: #ffffff;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                        border-radius: 5px;
                        min-width: 150px;
                        z-index: 1;
                        overflow: hidden;
                    }}

                    .dropdown-content a {{
                        color: #333;
                        padding: 10px 15px;
                        display: block;
                        text-decoration: none;
                        transition: background-color 0.2s;
                    }}

                    .dropdown-content a:hover {{
                        background-color: #f1f1f1;
                    }}

                    /* Menampilkan dropdown saat hover */
                    .dropdown:hover .dropdown-content {{
                        display: block;
                        animation: fadeIn 0.3s;
                    }}

                    /* Animasi fade-in */
                    @keyframes fadeIn {{
                        from {{
                        opacity: 0;
                        transform: translateY(-10px);
                        }}
                        to {{
                        opacity: 1;
                        transform: translateY(0);
                        }}
                    }}

                </style>
                
            </head>
            <body>

            <nav class="navbar navbar-expand-lg" style="height: 65px;">
                <div class="container-fluid">
                    <a class="navbar-brand ms-5 text-white fw-semibold" href="/psb">
                        <img src="https://i.ibb.co.com/SmWmBTW/SAVE-20220114-075750-removebg-preview-4.png" alt="1731466812700" width="50" alt="Logo Pesantren">
                        Daarul Qur'an Istiqomah
                    </a>
                    <button class="navbar-toggler ms-auto" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar" aria-controls="offcanvasNavbar">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item me-3">
                                <a class="nav-link text-white" style="color: white !important;" href="/psb"><i class="fa-solid fa-house me-2"></i>Beranda</a>
                            </li>
                            {f'<li class="nav-item me-3">'
                            f'<a class="nav-link text-white" href="/pendaftaran" {"data-bs-toggle='modal' data-bs-target='#modalPendaftaranTutup'" if not is_halaman_pendaftaran else ""}>'
                            f'<i class="fa-solid fa-note-sticky me-2"></i>Pendaftaran</a>'
                            f'</li>'}
                            <li class="nav-item dropdown">
                                <a href="#" class="dropdown-link nav-link"
                                    style="color: white !important;">
                                    <i class="fa-solid fa-fingerprint me-2"></i>Login</a>
                                <div class="dropdown-content">
                                    <a href="/login">Login PSB</a>
                                    <a href="/web/login">Login Orang Tua</a>
                                </div>
                            </li>
                            <li class="nav-item me-3">
                                <a class="nav-link text-white" href="/bantuan"><i class="fa-solid fa-lock me-2"></i>Bantuan</a>
                            </li>
                            {f'<li class="nav-item dropdown">'
                            f'<a href="#" class="dropdown-link nav-link text-white"><i class="fa-solid fa-bullhorn me-2"></i>Pengumuman</a>'
                            f'<div class="dropdown-content">'
                            f'<a href="/pengumuman/sd-mi">SD / MI</a>'
                            f'<a href="/pengumuman/smp-mts">SMP / MTS</a>'
                            f'<a href="/pengumuman/sma-ma">SMA / MA</a>'
                            f'</div>'
                            f'</li>' if is_halaman_pengumuman else ''}
                            </ul>
                    </div>
                </div>
            </nav>

            <div class="offcanvas offcanvas-end background" tabindex="-1" id="offcanvasNavbar" aria-labelledby="offcanvasNavbarLabel">
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas" aria-label="Close"></button>
                <a class="navbar-brand mt-1 text-white fw-semibold" href="/psb" style="display: flex; flex-direction: column; align-items: center;">
                    <img src="https://i.ibb.co.com/SmWmBTW/SAVE-20220114-075750-removebg-preview-4.png" alt="1731466812700" width="50" alt="">
                    Daarul Qur'an Istiqomah
                </a>
                <div class="offcanvas-body">
                    <ul class="navbar-nav justify-content-end flex-grow-1 pe-3">
                        <li class="nav-item me-3">
                            <a class="nav-link text-white" style="color: white !important;" href="/psb"><i class="fa-solid fa-house me-2"></i>Beranda</a>
                        </li>
                        {f'<li class="nav-item me-3">'
                        f'<a class="nav-link text-white" href="/pendaftaran" {"data-bs-toggle='modal' data-bs-target='#modalPendaftaranTutup'" if not is_halaman_pendaftaran else ""}>'
                        f'<i class="fa-solid fa-note-sticky me-2"></i>Pendaftaran</a>'
                        f'</li>'}
                        <li class="nav-item dropdown">
                            <a href="#" class="dropdown-link nav-link"
                                style="color: white !important;">
                                <i class="fa-solid fa-fingerprint me-2"></i>Login</a>
                            <div class="dropdown-content">
                                <a href="/login">Login PSB</a>
                                <a href="/web/login">Login Orang Tua</a>
                            </div>
                        </li>
                        <li class="nav-item me-3">
                            <a class="nav-link text-white" href="/bantuan"><i class="fa-solid fa-lock me-2"></i>Bantuan</a>
                        </li>
                        {f'<li class="nav-item dropdown">'
                        f'<a href="#" class="dropdown-link nav-link text-white"><i class="fa-solid fa-bullhorn me-2"></i>Pengumuman</a>'
                        f'<div class="dropdown-content">'
                        f'<a href="/pengumuman/sd-mi">SD / MI</a>'
                        f'<a href="/pengumuman/smp-mts">SMP / MTS</a>'
                        f'<a href="/pengumuman/sma-ma">SMA / MA</a>'
                        f'</div>'
                        f'</li>' if is_halaman_pengumuman else ''}
                        </ul>
                    </ul>
                </div>
            </div>

            <div class="container mt-5 mb-5">
            <div class="row">
                <!-- Timeline -->
                <div class="col-lg-6 mb-5">
                <div class="timeline">
                    <!-- Panduan Pendaftaran Online -->
                    <div class="timeline-item">
                    <div class="timeline-icon bg-danger">
                        <i class="fa-solid fa-briefcase text-white"></i>
                    </div>
                    <div class="timeline-content bg-white rounded p-3">
                        <span class="badge text-bg-danger text-uppercase mb-2">Panduan Pendaftaran Online</span>
                        <p>Panduan pendaftaran online dapat didownload dengan klik link di bawah ini :</p>
                        <div class="ratio ratio-16x9 my-4">
                        <iframe src="https://www.youtube.com/embed/N7eYT3LQ7tQ" title="YouTube video player" allowfullscreen></iframe>
                        </div>
                    </div>
                    </div>

                    <!-- Alur Pendaftaran Santri Baru -->
                    <div class="timeline-item">
                    <div class="timeline-icon bg-success">
                        <i class="fa-solid fa-puzzle-piece text-white"></i>
                    </div>
                    <div class="timeline-content bg-white rounded p-3">
                        <span class="badge text-bg-success text-uppercase mb-3">Alur Pendaftaran Santri Baru</span>
                        <ul>
                        <li>Buka website <a href="/psb" class="text-decoration-none" style="color: purple;">https://aplikasi.dqi.ac.id/psb</a></li>
                        <li>Klik menu daftar dan isikan data yang tersedia.</li>
                        <li>Login di <a href="/login" class="text-decoration-none" style="color: purple;">https://aplikasi.dqi.ac.id/login</a></li>
                        <li>Upload berkas yang dipersyaratkan dan bukti pembayaran.</li>
                        <li>Tunggu verifikasi maksimal 3 hari.</li>
                        <li>Ikuti tes seleksi Offline.</li>
                        <li>Lihat hasil tes di <a href="/" class="text-decoration-none" style="color: purple;">https://aplikasi.dqi.ac.id/psb</a></li>
                        <li>Setelah pembayaran daftar ulang, tunggu pengumuman serah terima santri baru.</li>
                        </ul>
                    </div>
                    </div>

                    <!-- Video Profil -->
                    <div class="timeline-item">
                    <div class="timeline-icon bg-info">
                        <i class="fa-solid fa-fingerprint text-white"></i>
                    </div>
                    <div class="timeline-content bg-white rounded p-3">
                        <span class="badge text-bg-info text-white text-uppercase">Video Profil Ponpes <br> Daarul Qur'an Istiqomah</span>
                        <div class="ratio ratio-16x9 my-4">
                        <iframe width="437" height="315" src="https://www.youtube.com/embed/OiPEDy0Sv1U" title="" frameborder="0" allowfullscreen></iframe>
                        </div>
                    </div>
                    </div>
                </div>
                </div>

                <!-- Informasi Kontak -->
                <div class="col-lg-6">
                <div class="bg-white rounded p-3 text-center">
                    <span style="font-size: 60px; font-weight: bold;">"</span>
                    <div class="text-secondary mb-4">
                    <span>Pondok Pesantren Daarul Qur'an Istiqomah</span><br>
                    <span>Jl. Ambawang, RT.03/RW.01, Karang Taruna, Kec. Pelaihari, Kabupaten Tanah Laut, Kalimantan Selatan 70815 </span><br>
                    <span>Telp/Whatsapp: <a href="https://api.whatsapp.com/send?phone=%2B6282252079785" class="text-decoration-none" style="color: purple;">0822-5207-9785</a></span><br>
                    </div>
                    <div class="text-secondary mb-4">
                    <span>Informasi PSB & Konsultasi Pendidikan:</span><br>
                    <a href="#" class="text-decoration-none" style="color: purple;">0853-9051-1124</a><br>
                    </div>
                    <h5>Media Sosial Kami</h5>
                    <span class="text-uppercase" style="color: purple;">Instagram : @daqubanat_</span><br>
                    <span class="text-uppercase" style="color: purple;">Facebook  : @Daarul Quran Istiqomah</span><br>
                    <span class="text-uppercase" style="color: purple;">Youtube   : @dqimedia</span><br>
                </div>
                </div>
            </div>
            </div>

            <footer class="text-white p-2" style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                <div class="ms-5">
                    <ul style="list-style-type: none; display: flex; text-transform: uppercase; font-size: 13px;" class="fw-semibold">
                        <li><a href="/psb" class="me-4" style="text-decoration: none; color: white;">Home</a></li>
                        <li><a href="/beranda" class="me-4" style="text-decoration: none; color: white;" target="_blank">Info Pondok</a></li>
                        <li><a href="https://drive.google.com/drive/folders/1KxQ0V4bd7RpSFqJKJfQ6JGn1z2-Ld7Wr" class="me-4" style="text-decoration: none; color: white;" target="_blank">Brosur</a></li>
                        <li><a href="" class="me-4" style="text-decoration: none; color: white;">Panduan</a></li>
                    </ul>
                    </ul>
                </div>
                <div class="me-5">
                    <p class="text-center mt-1">© 2024 TIM IT PPIB</p>
                </div>
            </footer>

            <!-- Modal -->
            <div class="modal fade" id="modalPendaftaranTutup" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="exampleModalLabel">Pendaftaran ditutup!</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Mohon maaf, pendaftaran telah ditutup karena kuota telah terpenuhi.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Tutup</button>
                </div>
                </div>
            </div>
            </div>

            <!-- Modal -->
            <div class="modal fade" id="modalPendaftaranTutup" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="exampleModalLabel">Pendaftaran ditutup!</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Mohon maaf, pendaftaran telah ditutup.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Tutup</button>
                </div>
                </div>
            </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
            <script src=" https://cdn.jsdelivr.net/npm/sweetalert2@11.14.5/dist/sweetalert2.all.min.js "></script>
            </body>
            </html>
        """

        return request.make_response(html_response)

class PendaftaranSeleksiSdMi(http.Controller):
    @http.route('/pengumuman/sd-mi', type='http', auth='public')
    def pengumuman(self, **kwargs):

        # Mengambil nilai kuota pendaftaran dari ir.config_parameter
        config_param = request.env['ir.config_parameter'].sudo()
        is_halaman_pendaftaran = config_param.get_param('pesantren_pendaftaran.is_halaman_pendaftaran')
        is_halaman_pengumuman = config_param.get_param('pesantren_pendaftaran.is_halaman_pengumuman')

        if is_halaman_pengumuman:
            # Render form pendaftaran HTML
            calon_santri = request.env['ubig.pendaftaran'].sudo().search([('state', 'in', ['diterima', 'ditolak']), ('jenjang_id.jenjang', '=', 'sdmi')])
            
            return request.render('pesantren_pendaftaran.pendaftaran_seleksi_sdmi_template', {
                'santri': calon_santri,
                'is_halaman_pendaftaran': is_halaman_pendaftaran,
            })
        else:
            return request.redirect('/psb')


class PendaftaranSeleksiSmpMts(http.Controller):
    @http.route('/pengumuman/smp-mts', type='http', auth='public')
    def pengumuman(self, **kwargs):

        # Mengambil nilai kuota pendaftaran dari ir.config_parameter
        config_param = request.env['ir.config_parameter'].sudo()
        is_halaman_pendaftaran = config_param.get_param('pesantren_pendaftaran.is_halaman_pendaftaran')
        is_halaman_pengumuman = config_param.get_param('pesantren_pendaftaran.is_halaman_pengumuman')

        if is_halaman_pengumuman:
            # Render form pendaftaran HTML
            calon_santri = request.env['ubig.pendaftaran'].sudo().search([('state', 'in', ['diterima', 'ditolak']), ('jenjang_id.jenjang', '=', 'smpmts')])
            return request.render('pesantren_pendaftaran.pendaftaran_seleksi_smpmts_template', {
                'santri': calon_santri,
                'is_halaman_pendaftaran': is_halaman_pendaftaran,
            })
        else:
            return request.redirect('/psb')
    
class PendaftaranSeleksiSmaMa(http.Controller):
    @http.route('/pengumuman/sma-ma', type='http', auth='public')
    def pengumuman(self, **kwargs):

        # Mengambil nilai kuota pendaftaran dari ir.config_parameter
        config_param = request.env['ir.config_parameter'].sudo()
        is_halaman_pendaftaran = config_param.get_param('pesantren_pendaftaran.is_halaman_pendaftaran')
        is_halaman_pengumuman = config_param.get_param('pesantren_pendaftaran.is_halaman_pengumuman')

        if is_halaman_pengumuman:
            # Render form pendaftaran HTML
            calon_santri = request.env['ubig.pendaftaran'].sudo().search([('state', 'in', ['diterima', 'ditolak']), ('jenjang_id.jenjang', '=', 'smama')])
            return request.render('pesantren_pendaftaran.pendaftaran_seleksi_smama_template', {
                'santri': calon_santri,
                'is_halaman_pendaftaran': is_halaman_pendaftaran,
            })
        else:
            return request.redirect('/psb')


class RefDataController(http.Controller):
    @http.route('/get_provinsi', type='http', auth='public', methods=['POST'], csrf=False)
    def get_provinsi(self, **kwargs):
        # Ambil parameter 'query' dari permintaan
        query = request.httprequest.json.get('query', '').lower()
        
        provinces = request.env['cdn.ref_propinsi'].sudo().search([('name', 'ilike', query)])
        data = [{'id': prov.id, 'name': prov.name} for prov in provinces]
        
        if request.httprequest.headers.get('Content-Type') == 'application/json':
            # Permintaan JSON
            return json.dumps(data)
        else:
            # Permintaan HTTP biasa
            return request.make_response(
                json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/get_kota/<int:provinsi_id>', type='http', auth='public', methods=['POST'], csrf=False)
    def get_kota(self, provinsi_id, **kwargs):
        kota = request.env['cdn.ref_kota'].sudo().search([('propinsi_id', '=', provinsi_id)])
        data = [{'id': city.id, 'name': city.name} for city in kota]
        
        if request.httprequest.headers.get('Content-Type') == 'application/json':
            # Permintaan JSON
            return json.dumps(data)
        else:
            # Permintaan HTTP biasa
            return request.make_response(
                json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/get_kecamatan/<int:kota_id>', type='http', auth='public', methods=['POST'], csrf=False)
    def get_kecamatan(self, kota_id, **kwargs):
        kecamatan = request.env['cdn.ref_kecamatan'].sudo().search([('kota_id', '=', kota_id)])
        data = [{'id': kec.id, 'name': kec.name} for kec in kecamatan]
        
        if request.httprequest.headers.get('Content-Type') == 'application/json':
            # Permintaan JSON
            return json.dumps(data)
        else:
            # Permintaan HTTP biasa
            return request.make_response(
                json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )


# class ViewKartuSantri(http.Controller):
#     @http.route('/kartusantri', type='http', auth='user', methods=['GET'])
#     def index(self, santri_id, **kwargsj):

#         # Ambil data santri berdasarkan ID
#         santri = request.env['cdn.siswa'].sudo().browse(int(santri_id))
#         if not santri.exists():
#             return request.not_found()

#         html_response = f"""
#                     <html lang="en">

#                         <head>
#                             <meta charset="UTF-8">
#                             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                             <title>Kartu Santri</title>
#                             <link rel="stylesheet" href="styles.css">
#                         </head>
#                         <style>
#                             @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500&display=swap');

#                             .card-number {{
#                                 font-family: 'Roboto Mono', monospace;
#                                 /* Monospace font mirip ATM */
#                                 font-size: 17.5px;
#                                 /* Ukuran font */
#                                 letter-spacing: 3px;
#                                 font-weight: bold;
#                                 padding: 10px 0px;
#                                 display: inline-block;
#                                 width: fit-content;
#                                 /* Sesuaikan lebar */
#                             }}

#                             * {{
#                                 margin: 0;
#                                 padding: 0;
#                                 box-sizing: border-box;
#                             }}

#                             body {{
#                                 font-family: Arial, sans-serif;
#                                 background-color: #eaf2f7;
#                                 display: flex;
#                                 justify-content: center;
#                                 align-items: center;
#                                 height: 100vh;
#                             }}

#                             .card-container {{
#                                 display: flex;
#                                 justify-content: space-between;
#                                 align-items: center;
#                                 flex-direction: column-reverse;
#                                 gap: 10px;
#                             }}

#                             .card {{
#                                 width: 450px;
#                                 height: 260px;
#                                 border-radius: 10px;
#                                 box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#                                 position: relative;
#                                 overflow: hidden;
#                             }}

#                             .front {{
#                                 background: linear-gradient(to top right, #339966 0%, #00cc66 100%);
#                                 color: white;
#                                 display: flex;
#                                 flex-direction: column;
#                                 justify-content: space-between;
#                                 padding: 15px;
#                             }}

#                             .back .card-header {{
#                                 font-size: 20px;
#                                 font-weight: bold;
#                                 display: flex;
#                                 align-items: center;
#                                 gap: 5px;
#                             }}

#                             .front .subtitle {{
#                                 font-size: 14px;
#                                 margin-top: 5px;
#                             }}

#                             /* 
#                             .front .barcode {{
#                                 width: 100%;
#                             }} */

#                             .front .barcode img {{
#                                 width: 15rem;
#                                 height: 5rem;
#                                 background-color: #eaf2f7;
#                                 border-radius: 5px;
#                             }}

#                             .back {{
#                                 background: linear-gradient(to top right, #339966 0%, #00cc66 100%);
#                                 color: white;
#                                 display: flex;
#                                 flex-direction: column;
#                                 justify-content: space-between;
#                                 padding: 15px;
#                             }}

#                             .back .card-header {{
#                                 font-size: 20px;
#                                 font-weight: bold;
#                             }}

#                             .back .card-info {{
#                                 margin-top: 10px;
#                             }}

#                             .back .id {{
#                                 font-size: 16px;
#                                 font-weight: bold;
#                             }}

#                             .back .info {{
#                                 font-size: 14px;
#                             }}

#                             .back .qr-code img {{
#                                 margin-top: 20px;
#                                 height: 140px;
#                                 width: 120px;
#                                 background-color: #eaf2f7;
#                                 border-radius: 10px;
#                                 z-index: 10;
#                                 display: flex;
#                                 flex-direction: column;
#                                 position: relative;
#                             }}


#                             .title {{
#                                 font-size: 17px;
#                             }}

#                             .right-s {{
#                                 position: absolute;
#                                 rotate: -40deg;
#                                 right: 0px;
#                                 bottom: 5rem;
#                                 display: flex;
#                                 z-index: 4;
#                             }}

#                             .sprite {{
#                                 position: relative;
#                                 background-color: #ffb901;
#                                 height: 400px;
#                                 width: 20px;
#                             }}

#                             .site {{
#                                 position: relative;
#                                 background-color: #0000cc;
#                                 z-index: 3;
#                                 height: 400px;
#                                 width: 120px;
#                             }}

#                             .icon-card {{
#                                 position: absolute;
#                                 z-index: 100;
#                                 right: 1rem;
#                                 top: 10px;
#                                 width: 2.5rem;
#                                 height: 2.5rem;
#                             }}

#                             .banner {{
#                                 border-radius: 50%;
#                                 position: absolute;
#                                 background-image: url('https://i.ibb.co.com/wRNC9B0/img1.jpg');
#                                 width: 12rem;
#                                 height: 12rem;
#                                 background-position: center;
#                                 background-repeat: no-repeat;
#                                 background-size: auto;
#                                 right: -4.7rem;
#                                 top: 13.5%;
#                                 box-shadow: #000000ad 3px 4px 30px;
#                             }}
#                         </style>

#                         <body>
#                             <div class="card-container">
#                                 <!-- Kartu Santri Depan -->
#                                 <div class="card front">
#                                     <div style="display: flex; align-items: center; gap: 5px;">
#                                         <img src="credit-card.png" style="width: 2rem; " alt="">
#                                         <p>Universal Big Data</p>
#                                     </div>
#                                     <div class="card-header">
#                                         <div>
#                                             <h1 class="title" style="font-size: 1.7rem;">Kartu Santri</h1>
#                                             <h3 class="subtitle" style="font-size: 1.4rem;">Daarul Qu`ran Istiqomah</h3>
#                                         </div>
#                                     </div>
#                                     <div class="barcode">
#                                         <img src="credit-card.png" alt="Barcode">
#                                         <p>Jln. Kenanga no 5 perempatan pasar</p>
#                                     </div>
#                                     <div class="banner"></div>
#                                 </div>

#                                 <!-- Kartu Santri Belakang -->
#                                 <div class="card back">
#                                     <div class="card-header">
#                                         <img src="credit-card.png" class="icon-card" alt="">
#                                         <div class="right-s">
#                                             <div class="sprite"></div>
#                                             <div class="site"></div>
#                                         </div>
#                                         <img src="../dqi.png" width="45px" height="45px" alt="img">
#                                         <div>
#                                             <span class="title">Kartu Santri</span>
#                                             <br>
#                                             <span class="subtitle">Daarul Qu`ran Istiqomah</span>
#                                         </div>
#                                     </div>
#                                     <div style="display: flex; align-items: end; justify-content: space-between;">
#                                         <div class="card-info">
#                                             <p class="card-number">1234.5678.1234.5678</p>
#                                             <p class="info">Nama: {santri.name}</p>
#                                             <p class="info">Telp: {santri.phone}</p>
#                                             <p class="info">Alamat: {santri.street}</p>
#                                         </div>
#                                         <div class="qr-code">
#                                             <img src="qr-code.png" alt="QR Code">
#                                             <p style="font-weight: bold; text-align: center; margin-top: 5px;">
#                                                 DQI 14
#                                             </p>
#                                         </div>
#                                     </div>
#                                 </div>
#                             </div>
#                         </body>

#                         </html>
        
#                 """

#         return request.make_response(html_response)

# class PortalOrangTua(http.Controller):
    # @http.route('/validate_kode_akses', type='http', auth='public', methods=['POST'], csrf=False)
    # def validate_kode_akses(self, **kwargs):
    #     try:
    #         # Parse JSON dari body request
    #         data = json.loads(request.httprequest.data)
    #         kode_akses = data.get('kode_akses')

    #         # Cari kode akses di model Odoo
    #         record = request.env['ubig.pendaftaran'].sudo().search([('kode_akses', '=', kode_akses)], limit=1)
    #         if record:
    #             return request.make_response(json.dumps({'success': True, 'message': 'Kode akses valid!'}), 
    #                     headers=[('Content-Type', 'application/json')])
    #         return request.make_response(json.dumps({'success': False, 'message': 'Kode akses tidak ditemukan.'}),
    #                     headers=[('Content-Type', 'application/json')])
    #     except Exception as e:
    #         return request.make_response(json.dumps({'success': False, 'message': str(e)}),
    #                     headers=[('Content-Type', 'application/json')])


class PortalOrangTua(http.Controller):
    @http.route('/portal_orang_tua', type='http', auth='public', website=True)
    def portal_orang_tua(self, *kwargs):
        # Ambil data dari sesi
        user_id = request.session.get('user_id')
        
        record = request.env['ubig.pendaftaran'].sudo().search([('id', '=', user_id)])

        if not user_id or not record:
            return request.redirect('/login')

        email = record.email

        records = request.env['ubig.pendaftaran'].sudo().search([('email', '=', email)])

        first_record = records[0]

        # Prioritaskan nama
        display_name = first_record['wali_nama'] or first_record['nama_ayah'] or first_record['nama_ibu']
        
        # Ambil nilai dari field konfigurasi
        config_obj = http.request.env['ir.config_parameter'].sudo()

        is_halaman_pengumuman = config_obj.get_param('pesantren_pendaftaran.is_halaman_pengumuman')
        is_halaman_pendaftaran = config_obj.get_param('pesantren_pendaftaran.is_halaman_pendaftaran')
        no_rekening = config_obj.get_param('pesantren_pendaftaran.no_rekening', default='7181863913')

        # Daftar status yang akan ditampilkan
        state_list = [
            ('batal', 'Batal'),
            ('draft', 'Draft'),
            ('terdaftar', 'Terdaftar'),
            ('seleksi', 'Seleksi'),
            ('diterima', 'Diterima'),
            ('ditolak', 'Ditolak'),
        ]

        state_progress = {
            'batal': 0,
            'draft': 25,
            'terdaftar': 50,
            'seleksi': 75,
            'diterima': 100,
        }

        state_tooltip_messages = {
            'batal': "Status ini menunjukkan bahwa pendaftaran dibatalkan oleh peserta atau sistem.",
            'draft': "Status ini menunjukkan bahwa pendaftaran masih dalam tahap draft, Calon Sudah terdaftar, tetapi belum membayar biaya pendaftaran.",
            'terdaftar': "Status ini menunjukkan bahwa pendaftaran sudah berhasil, dan data sudah konfirmasi oleh Ponpes.",
            'seleksi': "Status ini menunjukkan bahwa pendaftaran sedang dalam tahap seleksi, Calon Santri Melalukan Membaca Al-Qur'an & Wawancara.",
            'diterima': "Status ini menunjukkan bahwa pendaftaran telah diterima, dan peserta memenuhi syarat.",
            'ditolak': "Status ini menunjukkan bahwa pendaftaran ditolak karena tidak memenuhi kriteria atau persyaratan.",
        }

        # Membuat HTML dinamis untuk setiap record
        rows_html = ''
        for rec in records:
            csrf_token = request.csrf_token()  # Ambil CSRF token
            # Tentukan status pembayaran dan kelas badge
            status_text = rec.status_pembayaran.replace('belumbayar', 'Belum Bayar').replace('sudahbayar', 'Sudah Bayar')
            badge_class = 'success' if rec.status_pembayaran == 'sudahbayar' else 'danger'
            is_disabled = 'disabled' if rec.status_pembayaran == 'sudahbayar' else ''
            state_html = ''
            # Buat HTML untuk status pendaftaran siswa
            for state_key, state_label in state_list:
                tooltip_message = state_tooltip_messages.get(state_key, "Tidak ada informasi status.")
                if state_key == rec.state:
                    state_html += f'<span class="badge me-1 mb-2 text-bg-primary" title="Ini adalah status pendaftaran saat ini dari anak anda. {tooltip_message}" data-bs-toggle="tooltip" data-bs-placement="bottom">{state_label}</span>'
                else:
                    state_html += f'<span class="badge text-bg-secondary me-1 mb-2 inactive" title="{tooltip_message}" data-bs-toggle="tooltip" data-bs-placement="bottom">{state_label}</span>'
            
            # Progress bar untuk pendaftaran
            if rec.state == "ditolak":
                progress_html = ''
            else:
                progress_html = f"""
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar" role="progressbar" style="width: {state_progress.get(rec.state, 0)}%" 
                        aria-valuenow="{state_progress.get(rec.state, 0)}" aria-valuemin="0" aria-valuemax="100">
                    </div>
                </div>
                Pendaftaran: {state_progress.get(rec.state, 0)}%
                """

            # Menambahkan HTML untuk satu baris data siswa
            rows_html += f"""
            <tr>
                <td><span class="text-capitalize">{rec.partner_id.name}</span></td>
                <td>
                    <div class="d-flex justify-content-center">
                        <div class="mb-2">
                            {state_html}
                        </div>
                    </div>
                    {progress_html}
                </td>
                <td>
                    <span class="badge text-bg-{badge_class}">{status_text}</span>
                </td>
                <td>
                    <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#uploadModal-{rec.id}" {is_disabled}>
                    Upload Bukti
                    </button>
                    
                    <!-- Modal -->
                    <div class="modal fade" id="uploadModal-{rec.id}" tabindex="-1" aria-labelledby="uploadModalLabel-{rec.id}" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="uploadModalLabel-{rec.id}">Upload Bukti Pembayaran</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <form action="/upload_bukti_pembayaran" method="post" enctype="multipart/form-data">
                                        <input type="hidden" name="csrf_token" value="{csrf_token}">
                                        <input type="hidden" name="record_id" value="{rec.id}">
                                        <div class="mb-3">
                                            <label for="buktiPembayaran-{rec.id}" class="form-label">Pilih File</label>
                                            <input type="file" class="form-control" id="buktiPembayaran-{rec.id}" name="bukti_pembayaran" required>
                                        </div>
                                        <button type="submit" class="btn btn-success">Upload</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
            """

        # Membuat HTML dinamis
        html_content = f"""
                <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Portal Orang Tua - Daarul Qur'an Istiqomah</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />

                <style>

                    body {{
                        background: linear-gradient(to bottom left, #065c5c 18%, #f5e505 100%) !important;
                    }}

                    .offcanvas.offcanvas-end {{
                        
                        width: 250px; /* Lebar kustom untuk offcanvas */
                    }}
                    
                    .offcanvas .nav-link {{
                        color: #ffffff; /* teks warna putih */
                    }}
                    
                    .offcanvas .btn-close {{
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        filter: invert(1);
                    }}

                    .background {{
                        background: linear-gradient(to bottom left, #065c5c 18%, #f5e505 100%) !important;
                    }}

                    a.effect {{
                        transition: .1s !important;
                    }}

                    a.effect:hover {{
                        box-shadow: 0 3px 10px rgba(0,0,0,0.2) !important;
                    }}

                    /* Desain Dropdown */
                    .dropdown {{
                        position: relative;
                    }}

                    .dropdown-link {{
                        cursor: pointer;
                    }}

                    .dropdown-content {{
                        display: none;
                        position: absolute;
                        top: 100%;
                        right: 0;
                        background-color: #ffffff;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                        border-radius: 5px;
                        min-width: 150px;
                        z-index: 1;
                        overflow: hidden;
                    }}

                    .dropdown-content a {{
                        color: #333;
                        padding: 10px 15px;
                        display: block;
                        text-decoration: none;
                        transition: background-color 0.2s;
                    }}

                    .dropdown-content a:hover {{
                        background-color: #f1f1f1;
                    }}

                    /* Menampilkan dropdown saat hover */
                    .dropdown:hover .dropdown-content {{
                        display: block;
                        animation: fadeIn 0.3s;
                    }}

                    /* Animasi fade-in */
                    @keyframes fadeIn {{
                        from {{
                        opacity: 0;
                        transform: translateY(-10px);
                        }}
                        to {{
                        opacity: 1;
                        transform: translateY(0);
                        }}
                    }}

                    .card-header {{
                    background-color: #9fc912;
                    color: white;
                    font-size: 1.2rem;
                    font-weight: bold;
                }}

                .card-body {{
                    background-color: white;
                    color: #333;
                }}

                .table th, .table td {{
                    vertical-align: middle;
                }}

                .progress-bar {{
                    background-color: #28a745;
                }}

                .status-card {{
                    border-left: 5px solid #4CAF50;
                }}

                .inactive {{
                    opacity: 0.6;
                }}

                .progress-bar {{
                    transition: width 1s ease-in-out;
                }}

                @media (max-width: 767px) {{
                    .table thead {{
                        display: none;
                    }}

                    .table, .table tbody, .table tr, .table td {{
                        display: block;
                        width: 100%;
                    }}

                    .table td {{
                        text-align: right;
                        position: relative;
                        padding-left: 50%;
                    }}

                    .table td::before {{
                        content: attr(data-label);
                        position: ab        solute;
                        left: 10px;
                        font-weight: bold;
                    }}
                }}

                </style>
                
            </head>
            <body>

            <nav class="navbar navbar-expand-lg" style="height: 65px;">
                <div class="container-fluid">
                    <a class="navbar-brand ms-5 text-white fw-semibold" href="/psb">
                        <img src="https://i.ibb.co.com/SmWmBTW/SAVE-20220114-075750-removebg-preview-4.png" alt="1731466812700" width="50" alt="Logo Pesantren">
                        Daarul Qur'an Istiqomah
                    </a>
                    <button class="navbar-toggler ms-auto" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar" aria-controls="offcanvasNavbar">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item me-3">
                                <a class="nav-link text-white" style="color: white !important;" href="/psb"><i class="fa-solid fa-house me-2"></i>Beranda</a>
                            </li>
                            {f'<li class="nav-item me-3">'
                            f'<a class="nav-link text-white" href="/pendaftaran" {"data-bs-toggle='modal' data-bs-target='#modalPendaftaranTutup'" if not is_halaman_pendaftaran else ""}>'
                            f'<i class="fa-solid fa-note-sticky me-2"></i>Pendaftaran</a>'
                            f'</li>'}
                            <li class="nav-item dropdown">
                                <a href="#" class="dropdown-link nav-link"
                                    style="color: white !important;">
                                    <i class="fa-solid fa-fingerprint me-2"></i>Login</a>
                                <div class="dropdown-content">
                                    <a href="/login">Login PSB</a>
                                    <a href="/web/login">Login Orang Tua</a>
                                </div>
                            </li>
                            <li class="nav-item me-3">
                                <a class="nav-link text-white" href="/bantuan"><i class="fa-solid fa-lock me-2"></i>Bantuan</a>
                            </li>
                            {f'<li class="nav-item dropdown">'
                            f'<a href="#" class="dropdown-link nav-link text-white"><i class="fa-solid fa-bullhorn me-2"></i>Pengumuman</a>'
                            f'<div class="dropdown-content">'
                            f'<a href="/pengumuman/sd-mi">SD / MI</a>'
                            f'<a href="/pengumuman/smp-mts">SMP / MTS</a>'
                            f'<a href="/pengumuman/sma-ma">SMA / MA</a>'
                            f'</div>'
                            f'</li>' if is_halaman_pengumuman else ''}
                            <li class="nav-item me-3">
                                <a class="nav-link text-white" href="/logout" onclick="return confirm('Apakah anda yakin untuk logout?');"><i class="fa-solid fa-right-from-bracket me-2"></i>Logout</a>
                            </li>
                            </ul>
                    </div>
                </div>
            </nav>

            <div class="offcanvas offcanvas-end background" tabindex="-1" id="offcanvasNavbar" aria-labelledby="offcanvasNavbarLabel">
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas" aria-label="Close"></button>
                <a class="navbar-brand mt-1 text-white fw-semibold" href="/psb" style="display: flex; flex-direction: column; align-items: center;">
                    <img src="https://i.ibb.co.com/SmWmBTW/SAVE-20220114-075750-removebg-preview-4.png" alt="1731466812700" width="50" alt="">
                    Daarul Qur'an Istiqomah
                </a>
                <div class="offcanvas-body">
                    <ul class="navbar-nav justify-content-end flex-grow-1 pe-3">
                        <li class="nav-item me-3">
                            <a class="nav-link text-white" style="color: white !important;" href="/psb"><i class="fa-solid fa-house me-2"></i>Beranda</a>
                        </li>
                        {f'<li class="nav-item me-3">'
                        f'<a class="nav-link text-white" href="/pendaftaran" {"data-bs-toggle='modal' data-bs-target='#modalPendaftaranTutup'" if not is_halaman_pendaftaran else ""}>'
                        f'<i class="fa-solid fa-note-sticky me-2"></i>Pendaftaran</a>'
                        f'</li>'}
                        <li class="nav-item dropdown">
                            <a href="#" class="dropdown-link nav-link"
                                style="color: white !important;">
                                <i class="fa-solid fa-fingerprint me-2"></i>Login</a>
                            <div class="dropdown-content">
                                <a href="/login">Login PSB</a>
                                <a href="/web/login">Login Orang Tua</a>
                            </div>
                        </li>
                        <li class="nav-item me-3">
                            <a class="nav-link text-white" href="/bantuan"><i class="fa-solid fa-lock me-2"></i>Bantuan</a>
                        </li>
                        {f'<li class="nav-item dropdown">'
                        f'<a href="#" class="dropdown-link nav-link text-white"><i class="fa-solid fa-bullhorn me-2"></i>Pengumuman</a>'
                        f'<div class="dropdown-content">'
                        f'<a href="/pengumuman/sd-mi">SD / MI</a>'
                        f'<a href="/pengumuman/smp-mts">SMP / MTS</a>'
                        f'<a href="/pengumuman/sma-ma">SMA / MA</a>'
                        f'</div>'
                        f'</li>' if is_halaman_pengumuman else ''}
                        <li class="nav-item me-3">
                            <a class="nav-link text-white" href="/logout" onclick="return confirm('Apakah anda yakin untuk logout?');"><i class="fa-solid fa-right-from-bracket me-2"></i>Logout</a>
                        </li>
                        </ul>
                    </ul>
                </div>
            </div>

            <div class="container my-5">
                <h2 class="text-center mb-4 text-white">Selamat Datang Bapak/Ibu, <span class="text-capitalize">{display_name}</span></h2>

                <!-- Progres PSB Anak -->
                <div class="card mb-4">
                    <div class="card-header">
                        Progres PSB Anak Anda
                    </div>
                    <div class="card-body">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Nama Siswa</th>
                                    <th>Status Pendaftaran</th>
                                    <th>Status Pembayaran</th>
                                    <th>Aksi</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows_html}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Info Pembayaran PSB -->
                <div class="card mb-4">
                    <div class="card-header">
                        Informasi Pembayaran PSB
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h5 class="mb-3">Biaya PSB:</h5>
                                {''.join([f"""
                                <div class="mb-1" style="border-bottom: 1px solid black;">
                                    <h6>- {data.partner_id.name}</h6>
                                    <p>Jenjang : {data.jenjang.replace('sdmi', 'SD / MI').replace('smpmts', 'SMP / MTS').replace('smama', 'SMA / MA').replace('paud', 'PAUD').replace('tk', 'TK')}</p>
                                    <p>
                                        <strong>
                                            {'Rp ' + str(f"{int(data.biaya):,}").replace(',', '.') + ' (Belum Bayar)' if data.status_pembayaran == 'belumbayar' else 
                                            'Rp 0 (Sudah Bayar)' if data.status_pembayaran == 'sudahbayar' else 
                                            'Pendaftaran Dibatalkan' if data.state == 'ditolak' else ''}
                                        </strong>

                                    </p>
                                </div>
                                """ for data in records])}
                                <div class="mt-3 mb-3">
                                    <h6><strong>Total Bayar : Rp {str(f"{sum(int(data.biaya) if data.status_pembayaran == 'belumbayar' else 0 for data in records):,}").replace(',', '.')}</strong></h6>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h5>Instruksi Pembayaran:</h5>
                                <span>Melalui Mobile Bank BSI:</span>
                                <ul>
                                <li>Login ke aplikasi BSI Mobile.</li>
                                <li>Pilih menu Transfer.</li>
                                <li>Masukkan nomor rekening tujuan.</li>
                                <li>Masukkan jumlah pembayaran.</li>
                                <li>Tambahkan catatan (opsional) jika diperlukan.</li>
                                <li>Pembayaran berhasil dan Anda akan menerima bukti transaksi.</li>
                                </ul>
                                <span>Melalui ATM Bank BSI:</span>
                                <ul>
                                <li>Masukkan kartu ATM dan PIN.</li>
                                <li>Pilih menu Transfer.</li>
                                <li>Pilih tujuan transfer:</li>
                                <li>Masukkan nomor rekening tujuan.</li>
                                <li>Verifikasi pembayaran dan lanjutkan.</li>
                                <li>Pembayaran berhasil dan Anda menerima bukti pembayaran.</li>
                                </ul>
                                <p>Silakan melakukan pembayaran melalui transfer bank ke rekening yang tertera di bawah ini.</p>
                                <p><strong>Rekening: BSI {no_rekening}</strong></p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Riwayat Pembayaran -->
                <!-- <div class="card mb-4">
                    <div class="card-header">
                        Riwayat Pembayaran
                    </div>
                    <div class="card-body">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Tanggal Pembayaran</th>
                                    <th>Jumlah Pembayaran</th>
                                    <th>Status Pembayaran</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>15 Jan 2024</td>
                                    <td>IDR 1.250.000,-</td>
                                    <td><span class="badge bg-success">Lunas</span></td>
                                </tr>
                                <tr>
                                    <td>20 Jan 2024</td>
                                    <td>IDR 1.250.000,-</td>
                                    <td><span class="badge bg-warning">Menunggu Konfirmasi</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div> -->
            </div>

            <footer class="text-white p-2" style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                <div class="ms-5">
                    <ul style="list-style-type: none; display: flex; text-transform: uppercase; font-size: 13px;" class="fw-semibold">
                        <li><a href="/psb" class="me-4" style="text-decoration: none; color: white;">Home</a></li>
                        <li><a href="/beranda" class="me-4" style="text-decoration: none; color: white;" target="_blank">Info Pondok</a></li>
                        <li><a href="https://drive.google.com/drive/folders/1KxQ0V4bd7RpSFqJKJfQ6JGn1z2-Ld7Wr" class="me-4" style="text-decoration: none; color: white;" target="_blank">Brosur</a></li>
                        <li><a href="" class="me-4" style="text-decoration: none; color: white;">Panduan</a></li>
                    </ul>
                    </ul>
                </div>
                <div class="me-5">
                    <p class="text-center mt-1">© 2024 TIM IT PPIB</p>
                </div>
            </footer>

            <!-- Modal -->
            <div class="modal fade" id="modalPendaftaranTutup" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="exampleModalLabel">Pendaftaran ditutup!</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Mohon maaf, pendaftaran telah ditutup.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Tutup</button>
                </div>
                </div>
            </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>

            <script>

            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
            console.log(tooltipTriggerList)
            const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

            </script>
            </body>
            </html>
        """
        return request.make_response(html_content, headers=[('Content-Type', 'text/html')])

class PesantrenLogin(http.Controller):
    @http.route('/login', type='http', auth='public')
    def index(self, **kwargs):
        # Ambil data dari sesi
        user_id = request.session.get('user_id')
        # Ambil nilai dari field konfigurasi
        config_obj = http.request.env['ir.config_parameter'].sudo()

        is_halaman_pendaftaran = config_obj.get_param('pesantren_pendaftaran.is_halaman_pendaftaran')
        is_halaman_pengumuman = config_obj.get_param('pesantren_pendaftaran.is_halaman_pengumuman')

        if user_id:
            return request.redirect('/portal_orang_tua')
        
        return request.render('pesantren_pendaftaran.pendaftaran_login_template', {
            'is_halaman_pengumuman': is_halaman_pengumuman,
            'is_halaman_pendaftaran': is_halaman_pendaftaran,

        })
    
    @http.route('/login/submit', type='http', auth='public', methods=['POST'], csrf=True)
    def login(self, **post):
        email = post.get('email')
        
        record = request.env['ubig.pendaftaran'].sudo().search([('email', '=', email)], limit=1)

        if record:
            password = post.get('password')
            if record.password == password:
                request.session['user_id'] = record.id
                return request.redirect('/portal_orang_tua')
            else:
                return """
                    <html>
                        <head>
                            <script>
                                alert('Kata sandi salah!');
                                window.location.href = '/login'; // Redirect ke halaman login
                            </script>
                        </head>
                    </html>
                """
        else:
            return """
                    <html>
                        <head>
                            <script>
                                alert('Email belum terdaftar!');
                                window.location.href = '/login'; // Redirect ke halaman login
                            </script>
                        </head>
                    </html>
                """

    @http.route('/logout', type='http', auth='public')
    def logout(self, **kwargs):
        request.session.logout()  # Menghapus semua data dalam sesi
        return request.redirect('/login')


class UploadBuktiPembayaran(http.Controller):
    @http.route('/upload_bukti_pembayaran', type='http', auth='public', methods=['POST'], csrf=True)
    def upload_bukti_pembayaran(self, **post):
        record_id = post.get('record_id')
        # Ambil file dari request
        uploaded_files = request.httprequest.files

        bukti_pembayaran = uploaded_files.get('bukti_pembayaran')

        # Fungsi bantu untuk memproses file
        def process_file(file):
            if file:
                # Baca file dan konversi ke Base64
                file_content = file.read()
                file_base64 = base64.b64encode(file_content)
                return file_base64
            return None
        
        bukti_pembayaran_b64 = process_file(bukti_pembayaran)

        if record_id and bukti_pembayaran_b64:
            # Cari record berdasarkan ID
            record = request.env['ubig.pendaftaran'].sudo().browse(int(record_id))
            if record:
                # Update field dengan file yang diunggah
                record.sudo().write({
                    'bukti_pembayaran': bukti_pembayaran_b64,
                })
                return request.redirect('/portal_orang_tua')
