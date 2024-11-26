odoo.define("pesantren_keuangan.PaymentScreen", (require) => {
  "use strict";
  const PaymentScreen = require("point_of_sale.PaymentScreen");
  const Registries = require("point_of_sale.Registries");
  const { _t } = require("web.core");

  const PinPaymentScreen = (PaymentScreen) =>
    class extends PaymentScreen {
      async _isOrderValid() {
        console.log("Setep 1")
        let currentOrder = this.env.pos.get_order();
        let client = currentOrder.get_partner();

        if (client && client.has_wallet_pin) {
          const { confirmed, payload } = await this.showPopup("NumberPopup", {
            title: _t("Masukkan PIN"),
          });

          if (confirmed) {
            if (payload === client.wallet_pin) {
              return super._isOrderValid(...arguments);
            } else {
              await this.showPopup("ErrorPopup", {
                title: _t("PIN Salah"),
                body: _t("PIN yang Anda masukkan salah! Silakan coba lagi."),
              });
              return false;
            }
          } else {
            return false;
          }
        } else {
          return super._isOrderValid(...arguments);
        }
      }
    };

  Registries.Component.extend(PaymentScreen, PinPaymentScreen);
  return PaymentScreen;
});
