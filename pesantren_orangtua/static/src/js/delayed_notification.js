/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";

export class NotificationForSpecificAction extends Component {
    setup() {
        this.notification = useService("notification");
        this.state = useState({ name: this.env.config.getDisplayName() });


        return this.notification.add("Notifikasi untuk Action-683 berhasil ditampilkan!", {
            title: "Informasi",
            type: "info",
            sticky: false, // Jika false, notifikasi akan hilang setelah beberapa detik
        });
    }
}
