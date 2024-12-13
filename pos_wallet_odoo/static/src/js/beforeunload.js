// odoo.define('pos_wallet_odoo.beforeunload', function (require) {
//     "use strict";

//     var core = require('web.core');
//     var _t = core._t;

//     // Fungsi untuk menangani event sebelum halaman dibuang
//     $(window).on('beforeunload', function () {
//         if (window.document.getElementsByClassName('oe_form_dirty').length) {
//             return _t("Warning, the record has been modified, your changes will be discarded.\n\nAre you sure you want to leave this page ?");
//         }
//     });
// });
