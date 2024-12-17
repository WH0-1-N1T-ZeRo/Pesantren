/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
        // this._showPopup();
        this._checkAndShowPopup();
    },

    // Set Popup hanya ditampilkan 1x sehari seperti iklan
    _checkAndShowPopup() {
        const popupKey = `popup_shown_${new Date().toISOString().split("T")[0]}`; // Key unik untuk hari ini

        if (!localStorage.getItem(popupKey)) {
            this._showPopup(); // Tampilkan popup jika belum ditampilkan
            localStorage.setItem(popupKey, true); // Tandai popup sudah ditampilkan hari ini
        }
    },

    _showPopup() {
        const popupHTML = `
        <style>
        /* Gambar latar belakang dengan efek blur */
.pic-box {
    height: 280px;
    background-image: url("https://i.imgur.com/Lduav64.jpeg"); /* Ganti dengan URL gambar yang sesuai */
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center;
    position: relative;
    transform: scaleX(-1);
}

/* Gradien untuk memberikan efek pencahayaan */
.grad {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(70deg, rgba(255,255,255,1), rgba(255,255,255,1), rgba(255,255,255,0));
    z-index: 1;
    transform: scaleX(-1);
    display:flex;
    flex-direction:column;
    justify-content:center;
}

/* Teks di atas gambar */
.text-box {
    width: 70%;
    padding: 2%;
    font-size: 1.1em;
    text-align: left;
}

.text-title {
    padding: 2%;
    text-align: left;
    font-weight: bold;
    font-size: 1.4em;
    z-index: 2;
}

        </style>
            <div class="modal fade show" tabindex="-1" style="display: block; background-color: rgba(0, 0, 0, 0.5);" id="donation-popup">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content rounded-3">
                        <div class="modal-header bg-primary">
                            <h5 class="modal-title" style="color:white;">Ayo Berbuat Kebaikan Hari Ini!</h5>
                            <button type="button" class="btn-close btn-close-white" aria-label="Close"></button>
                        </div>
                        <div class="modal-body text-center" style="position: relative; padding:0">
                            <!-- Gambar latar belakang dengan efek blur -->
                            <div class="pic-box">
                                <div class="grad">
                                    <h2 class="text-title">Ayo Bersedekah Hari Ini</h2>
                                    <p class="text-box">
                                        Assalamu'alaikum Warahmatullahi Wabarakatuh,<br>
                                        Mari dukung program kebaikan Pesantren Daarul Quran Istiqomah
                                        dengan bersedekah hari ini.
                                    </p>
                                    <div class=" ms-3row">
                                        <button class="btn btn-success col-2" id="donate-setting">Cek Donasi</button>
                                        <button class="btn btn-success ms-3 col-3" id="donate-now">Donasi Sekarang</button>
                                        <button type="button" class="btn btn-secondary d-none">Tutup</button>
                                    </div>
                            </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;

        const modalDiv = document.createElement("div");
        modalDiv.innerHTML = popupHTML;
        document.body.appendChild(modalDiv);

        const modal = modalDiv.querySelector("#donation-popup");

        // Menambahkan event listener untuk tombol tutup
        const closeButton = modal.querySelector(".btn-close");
        const closeFooterButton = modal.querySelector(".btn.btn-secondary");
        const donateNowButton = modal.querySelector("#donate-now");

        const settingDonateButton = modal.querySelector("#donate-setting");

        const closeModal = () => {
            modal.classList.remove("show");
            modal.remove();
        };

        // Event listener untuk tutup modal
        closeButton.addEventListener("click", closeModal);
        closeFooterButton.addEventListener("click", closeModal);

        // Event listener untuk klik tombol "Bersedekah Sekarang"
        donateNowButton.addEventListener("click", () => {
            this.DonateNow();
            closeModal();
        });

        settingDonateButton.addEventListener("click", () => {
            this.toggleDropdown();
            closeModal();
        });

        // Tutup modal jika klik di luar area modal
        modalDiv.addEventListener("click", (e) => {
            if (e.target === modalDiv) {
                closeModal();
            }
        });
    },

    // Fungsi untuk toggle visibilitas dropdown
    toggleDropdown() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Setting Donasi",
            res_model: "cdn.donation",
            view_mode: "list",
            views: [[false, "list"], [false, "form"]],
            target: "main", // Mengapa list yang muncul tidak bisa di klik atau masuk ke detailnya
        });
    },

    // Fungsi untuk toggle visibilitas dropdown
    DonateNow() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Setting Donasi",
            res_model: "cdn.donation.detail",
            view_mode: "list",
            views: [[false, "list"], [false, "form"]],
            target: "main",
            domain: [['created_by.name','=',session.partner_display_name]]
        });
    }    
});
