/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { Numpad as NumpadCustom } from "@point_of_sale/app/generic_components/numpad/numpad";

patch(NumpadCustom.prototype, {
    setup() {
        super.setup();
        // Store reference to original onClick
        const originalOnClick = this.onClick;
        
        // Replace onClick with new implementation
        this.onClick = async (buttonValue) => {
            // console.log('Button clicked:', buttonValue);
            
            const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
            
            // Handle special cases for multiple zeros
            if (['00', '000', '0000'].includes(buttonValue)) {
                const times = buttonValue.length; // Get number of zeros from button value
                
                for (let i = 0; i < times; i++) {
                    originalOnClick.call(this, '0');
                    if (i < times - 1) { // Don't delay after the last zero
                        await delay(202);
                    }
                }
            } else {
                originalOnClick.call(this, buttonValue);
            }
        };
    }
});