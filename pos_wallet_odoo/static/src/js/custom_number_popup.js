// custom_number_popup.js
odoo.define('pos_wallet_odoo.custom_number_popup', function(require) {
    'use strict';

    const { Component } = owl;
    const { useState } = owl.hooks;
    const { Popup } = require('point_of_sale.popups');

    class CustomNumberPopup extends Popup {
        setup() {
            super.setup();
            this.state = useState({
                inputBuffer: '' // Buffer untuk input pengguna
            });
        }

        // Fungsi untuk menangani input dan menambahkan karakter `*`
        onInput(value) {
            this.state.inputBuffer += value;
            this.render(); // Perbarui tampilan setiap ada input
        }

        // Fungsi konfirmasi dan keluaran input aktual tanpa masking
        confirm() {
            this.trigger('confirm', this.state.inputBuffer); // Kirim hasil input sebenarnya
        }

        // Fungsi untuk menghapus input terakhir
        backspace() {
            this.state.inputBuffer = this.state.inputBuffer.slice(0, -1);
            this.render();
        }
    }

    CustomNumberPopup.template = 'CustomNumberPopup';
    Registries.Component.add(CustomNumberPopup);

    return CustomNumberPopup;
});
