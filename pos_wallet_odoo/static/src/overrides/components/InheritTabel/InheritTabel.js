import { PartnerLine as InheritData } from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import { PartnerList as InheritTabel } from "@point_of_sale/app/screens/partner_list/partner_list";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

// Patch untuk menambahkan fungsi baru ke komponen InheritTabel
patch(InheritTabel.prototype, {
    setup() {
        super.setup();
        this.isCameraVisible = false; // Menandai status kamera
        this.originalTable = null;    // Menyimpan tabel asli
    },
        
    async BarCodeSantri() {
        const tableElement = document.getElementById("barcode");
    
        if (!this.isCameraVisible) {
            if (!tableElement) {
                console.error("Tabel tidak ditemukan.");
                return;
            }
    
            // Siapkan suara berhasil dan gagal
            const successSound = new Audio("/pos_wallet_odoo/static/src/mp3/s1.mp3");
            const failSound = new Audio("/pos_wallet_odoo/static/src/mp3/s2.mp3"); // Buat file `fail.mp3` jika dibutuhkan
    
            // Simpan tabel asli
            this.originalTable = tableElement.cloneNode(true);
    
            // Buat kontainer video untuk scanner
            const videoContainer = document.createElement("div");
            videoContainer.id = "video-container";
            videoContainer.style.width = "100%";
            videoContainer.style.height = "250px";
            videoContainer.style.maxWidth = "400px";
            videoContainer.style.margin = "auto";
            videoContainer.style.border = "2px solid #ddd";
            videoContainer.style.borderRadius = "10px";
            videoContainer.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
            videoContainer.style.overflow = "hidden";
            videoContainer.style.position = "relative";
    
            // Buat elemen untuk hasil barcode
            const resultElement = document.createElement("div");
            resultElement.id = "barcode-result";
            resultElement.innerHTML = `Hasil: <span id="barcode-text">Belum ada hasil</span>`;
            resultElement.style.marginTop = "20px";
            resultElement.style.fontSize = "20px";
            resultElement.style.fontWeight = "bold";
            resultElement.style.color = "#28a745";
            resultElement.style.textAlign = "center";
    
            // Ganti tabel dengan videoContainer dan resultElement
            tableElement.replaceWith(videoContainer);
            videoContainer.after(resultElement);
    
            // Inisialisasi QuaggaJS
            Quagga.init(
                {
                    inputStream: {
                        name: "Live",
                        type: "LiveStream",
                        target: videoContainer,
                        constraints: {
                            facingMode: "environment",
                        },
                    },
                    decoder: {
                        readers: [
                            "code_128_reader",
                            "ean_reader",
                            "ean_8_reader",
                            "upc_reader",
                            "upc_e_reader",
                            "code_39_reader",
                        ],
                    },
                },
                (err) => {
                    if (err) {
                        console.error("QuaggaJS gagal diinisialisasi:", err);
                        return;
                    }
                    Quagga.start();
                }
            );
    
            // Menampilkan hasil barcode
            Quagga.onDetected(async (result) => {
                const code = result.codeResult.code;
                document.getElementById("barcode-text").textContent = code;
                // console.log("Kode hasil scan:", code);
    
                try {
                    // Panggil API untuk mendapatkan data partner berdasarkan kode hasil scan
                    const response = await rpc('/siswa/get_data/bar', { barcode: code }, {
                        headers: {
                            "accept": "application/json"
                        }
                    });
    
                    // console.log("Response dari API:", response);
    
                    if (response && response.partner_id) {
                        // Panggil fungsi clickPartner jika partner ditemukan
                        this.clickPartner(response.partner_id);
                        successSound.play();
                    } else {
                        console.warn("Partner tidak ditemukan atau data tidak lengkap.");
                        failSound.play()
                    }
                } catch (error) {
                    console.error("Error saat mengambil data partner:", error);
                    failSound.play();
                }
    
                // Tutup kamera dan kembalikan tampilan
                this.closeCamera(videoContainer, resultElement);
            });
    
            // Tandai kamera sebagai aktif
            this.isCameraVisible = true;
        } else {
            // Jika kamera sudah aktif, tutup kamera dan kembalikan tampilan
            this.closeCamera(document.getElementById("video-container"), document.getElementById("barcode-result"));
        }
    },
    

    
    closeCamera(videoContainer, resultElement) {
        // Hentikan QuaggaJS jika sudah diinisialisasi
        Quagga.stop();

        // Kembalikan tabel asli
        if (videoContainer) {
            videoContainer.replaceWith(this.originalTable);
        }
        if (resultElement) {
            resultElement.remove();
        }

        // Tandai kamera sebagai tidak aktif
        this.isCameraVisible = false;
    }
});


patch(InheritData.prototype, {
    setup() {
        super.setup();
        this.getWalletBalance(this.props.partner.barcode);
    },

    async getWalletBalance(barcode) {
        try {
            const response = await rpc('/siswa/get_data/bar', { barcode: barcode }, {
                headers: {
                    "accept": "application/json"
                }
            });

            // console.log(response);
            // Set wallet_balance dan lainnya ke props.partner
            if (response && !response.error) {
                this.props.partner.wallet_balance = response.wallet_balance || 0;
                this.props.partner.nis = response.nis || '';
                // Tambahkan properti lain sesuai kebutuhan
            } else {
                console.error("Error fetching data:", response.error);
                this.props.partner.wallet_balance = 0; // Atur ke 0 jika ada error
            }
        } catch (error) {
            console.error("Error fetching wallet balance:", error);
            this.props.partner.wallet_balance = 0; // Atur ke 0 jika ada error
        }
    },
});


