/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { NumberPopup } from "@point_of_sale/app/components/popups/number_popup/number_popup";
import { ErrorPopup } from "@point_of_sale/app/components/popups/error_popup/error_popup";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

export class CustomPaymentScreen extends Component {
    static template = "point_of_sale.PaymentScreen";
    
    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
    }

    async _isOrderValid(isForceValidate) {
        console.log("Step 1 - Validating Order");
        const currentOrder = this.pos.get_order();
        const client = currentOrder.get_partner();

        // Cek apakah klien memiliki wallet_pin
        if (client && client.has_wallet_pin) {
            const { confirmed, payload } = await this.showPopup("NumberPopup", {
                title: "Masukkan PIN",
                startingValue: "",
            });

            if (confirmed) {
                // Validasi PIN
                if (payload.pin === client.wallet_pin) {
                    return super._isOrderValid(...arguments);
                } else {
                    await this.showPopup("ErrorPopup", {
                        title: "PIN Salah",
                        body: "PIN yang Anda masukkan salah! Silakan coba lagi.",
                    });
                    return false;
                }
            } else {
                // Jika popup dibatalkan
                return false;
            }
        } else {
            // Jika client tidak memiliki wallet_pin
            return super._isOrderValid(...arguments);
        }
    }
}

// Kode untuk Popup Kustom PIN
export class CustomNumberPopup extends NumberPopup {
    setup() {
        super.setup();
        this.state = useState({
            inputPIN: '',
            inputHasError: false,
        });
    }

    confirm() {
        try {
            // Memastikan input PIN valid
            parse.integer(this.state.inputPIN);
            return super.confirm();
        } catch (error) {
            this.state.inputHasError = true;
            return;
        }
    }

    getPayload() {
        return {
            pin: this.state.inputPIN,
        };
    }
}

// Menambahkan komponen ke registri Odoo
import { Registries } from "@web/core/registry";

Registries.Component.extend(PaymentScreen, CustomPaymentScreen);
Registries.Component.add("NumberPopup", CustomNumberPopup);
