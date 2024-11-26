odoo.define("pesantren_kesantrian.popup_scan", function (require) {
    "use strict";

    const { Component, mount } = owl;
    const Dialog = require("web.Dialog");
    const AbstractAction = require("web.AbstractAction");

    const PopupScan = AbstractAction.extend({
        start() {
            const popup = new Dialog(this, {
                title: "Scan KTS",
                $content: $(`
                    <div>
                        <video id="camera" autoplay></video>
                        <button id="start_scan">Start Scan</button>
                        <p>Hasil: <span id="scan_result"></span></p>
                    </div>
                `),
                buttons: [{ text: "Close", close: true }],
            });
            popup.open();

            this.initScanner();
        },

        initScanner() {
            const video = document.getElementById("camera");
            navigator.mediaDevices
                .getUserMedia({ video: { facingMode: "environment" } })
                .then((stream) => {
                    video.srcObject = stream;
                    video.play();
                })
                .catch((err) => {
                    console.error("Kamera tidak tersedia", err);
                });
        },
    });

    odoo.registry.add("display_popup_scan_kts", PopupScan);
});
