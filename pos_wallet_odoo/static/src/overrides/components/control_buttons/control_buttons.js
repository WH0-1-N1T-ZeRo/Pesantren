/** @odoo-module */

import { PaymentScreen as BaypasPayment } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { rpc } from "@web/core/network/rpc";

let pinAttempt = 0; // Counter untuk percobaan PIN

patch(BaypasPayment.prototype, {
    async clickSetSubTotal() {
        const currentOrder = this.pos.get_order();
        const client = currentOrder.get_partner();

        if (!client) {
            this.dialog.add(AlertDialog, {
                title: _t('Pelanggan Tidak Dipilih'),
                body: _t('Silakan pilih pelanggan dari daftar sebelum memasukkan PIN.'),
            });
            return;
        }

        // Ambil PIN siswa
        // console.log(client.name);
        const clientData = await this.getData(client.name);
        if (clientData) {
            const clientPin = clientData.pin || "654321";
            const walletBalance = clientData.wallet_balance || 0;
            this.showPinInputPopup(clientPin, walletBalance, client.id);
        }
    },

    async getData(name) {
        const apiUrl = "/siswa/get_data";
        // console.log("Memanggil RPC ke:", apiUrl); // Debug log
        try {
            // console.log("Fetching data from:", apiUrl);
            const domainFilter = [['name', 'like', name]];

            const data = await rpc(apiUrl, { domain: domainFilter }, {
                headers: {
                    "accept": "application/json"
                }
            });
            // console.log("Data fetched successfully:", data);
            return data[0] || null;
        } catch (error) {
            console.error("Kesalahan saat mengambil data:", error);
            return null;
        }
    },

    showPinInputPopup(clientPin, walletBalance, clientId) {
        const popup = document.createElement('div');
        popup.innerHTML = `
            <div style="
                position: fixed; 
                top: 0; 
                left: 0; 
                width: 100%; 
                height: 100%; 
                background: rgba(0,0,0,0.5); 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                z-index: 9999;">
                <div style="
                    background: white; 
                    padding: 20px 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2); 
                    text-align: center; 
                    animation: fadeIn 0.3s ease;">
                    <h3 style="margin: 0; color: #333;">Masukkan PIN Pelanggan</h3>
                    <p style="font-size: 14px; color: #666; margin: 10px 0;">Pastikan PIN sesuai untuk melanjutkan transaksi.</p>
                    <input 
                        type="password" 
                        id="pinInput" 
                        placeholder="Masukkan PIN Anda" 
                        style="padding: 10px; width: 100%; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px;">
                    <br><br>
                    <button id="submitPinButton" 
                        style="padding: 10px 20px; font-size: 16px; color: white; background: #007BFF; border: none; border-radius: 5px; cursor: pointer;">
                        Submit
                    </button>
                    <button id="cancelButton" 
                        style="padding: 10px 20px; font-size: 16px; color: #333; background: #f0f0f0; border: 1px solid #ccc; border-radius: 5px; cursor: pointer; margin-left: 10px;">
                        Cancel
                    </button>
                </div>
            </div>
        `;
    
        document.body.appendChild(popup);
    
        const submitButton = document.getElementById('submitPinButton');
        const cancelButton = document.getElementById('cancelButton');
        const pinInput = document.getElementById('pinInput');
    
        // Event handler untuk tombol submit
        submitButton.onclick = async () => {
            const enteredPin = pinInput.value.trim();
            if (!enteredPin) {
                alert("PIN tidak boleh kosong!");
                return;
            }
            document.body.removeChild(popup);
            await this.apply_pin(enteredPin, clientPin, walletBalance, clientId);
        };
    
        // Event handler untuk tombol cancel
        cancelButton.onclick = () => {
            document.body.removeChild(popup);
        };
    
        // Tambahkan event listener untuk close popup saat klik di luar box
        popup.addEventListener('click', (e) => {
            if (e.target === popup) {
                document.body.removeChild(popup);
            }
        });
    },    

    async apply_pin(enteredPin, clientPin, walletBalance, clientId) {
        if (pinAttempt >= 3) {
            this.dialog.add(AlertDialog, {
                title: _t('PIN Diblokir'),
                body: _t('Anda telah memasukkan PIN yang salah 3 kali. Silakan tunggu 1 jam untuk mencoba lagi.'),
            });
            return;
        } else if (walletBalance <= 0) {
            this.dialog.add(AlertDialog, {
                title: _t('Saldo Anda Kurang'),
                body: _t('Anda tidak bisa melanjutkan transaksi karena saldo anda kurang.'),
            });
            return;
        }

        if (enteredPin === clientPin) {
            pinAttempt = 0; // Reset counter PIN
            const currentOrder = this.pos.get_order();
            const totalAmount = currentOrder.get_total_with_tax();

            if (totalAmount > walletBalance) {
                this.dialog.add(AlertDialog, {
                    title: _t('Saldo Tidak Mencukupi'),
                    body: _t('Saldo pelanggan tidak cukup untuk membayar transaksi ini.'),
                });
                return;
            }

            try {
                // Panggil controller untuk mengurangi saldo
                const result = await rpc('/siswa/deduct_wallet', { partner_id: clientId, amount: totalAmount });
                if (result.success) {
                    // console.log("Saldo berhasil dikurangi. Saldo setelah transaksi: " + result.new_balance);
                    this.validateOrder(); // Panggil fungsi validasi order jika diperlukan
                } else {
                    this.dialog.add(AlertDialog, {
                        title: _t('Kesalahan'),
                        body: _t('Terjadi kesalahan saat mengurangi saldo: ' + result.error),
                    });
                }
            } catch (error) {
                console.error("Kesalahan saat mengurangi saldo:", error);
                this.dialog.add(AlertDialog, {
                    title: _t('Kesalahan'),
                    body: _t('Terjadi kesalahan saat mengurangi saldo. Silakan coba lagi.'),
                });
            }
        } else {
            pinAttempt += 1;
            const remainingAttempts = 3 - pinAttempt;
            this.dialog.add(AlertDialog, {
                title: _t(pinAttempt >= 3 ? 'PIN Diblokir' : 'PIN Salah'),
                body: _t(pinAttempt >= 3
                    ? 'Anda telah memasukkan PIN yang salah 3 kali. Silakan tunggu 1 jam untuk mencoba lagi.'
                    : `PIN Salah, Anda memiliki ${remainingAttempts} kesempatan lagi.`),
            });

            if (pinAttempt >= 3) {
                setTimeout(() => { pinAttempt = 0; }, 3600000); // Reset setelah 1 jam
            }
        }
    }
});