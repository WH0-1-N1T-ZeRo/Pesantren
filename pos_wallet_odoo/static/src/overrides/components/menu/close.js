/** @odoo-module **/

import { LoginScreen as LoginScreenExtension } from '@point_of_sale/app/screens/login_screen/login_screen';
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

const groupXmlId = "point_of_sale.group_pos_manager";

patch(LoginScreenExtension.prototype, {
    async setup() {
        super.setup();
        this.hasGroupPOSUser = false;
        await this.checkGroup(groupXmlId);
    },

    async checkGroup(groupXmlId) {
        try {
            const result = await rpc("/pos/check_user_group",{group_xml_id: groupXmlId},{
                headers: {
                    "accept": "application/json"
                }
            });
            console.log("Group check result:", result); // Debugging tambahan
            if (result.error) {
                console.error("Server error:", result.error);
                this.hasGroupPOSUser = false;
                this.render();
                return;
            }
            this.hasGroupPOSUser = result.has_group;
            this.render();
        } catch (error) {
            console.error("Error during group check:", error);
            this.hasGroupPOSUser = false;
            this.render();
        }
    },
});
