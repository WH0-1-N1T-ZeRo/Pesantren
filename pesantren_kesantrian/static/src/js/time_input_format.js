odoo.define('your_module_name.time_input_format', function (require) {
    "use strict";

    const fieldRegistry = require('web.field_registry');  // Check for correct reference
    const FieldFloatTime = fieldRegistry.get('float_time');  // Ensure float_time exists

    const TimeInputFormat = FieldFloatTime.extend({
        events: {
            'keypress': '_onKeyPress', // Handle keypress event
        },

        _onKeyPress: function (ev) {
            if (ev.key === 'Enter') {
                const value = this.$input.val();
                const timeParts = value.split(':');

                // Ensure input follows HH:MM format
                if (timeParts.length !== 2) {
                    alert("Format waktu tidak valid. Harap masukkan dalam format HH:MM.");
                    return;
                }

                let hours = parseInt(timeParts[0], 10);
                let minutes = parseInt(timeParts[1], 10);

                // Validate and format
                if (isNaN(hours) || isNaN(minutes) || hours < 0 || hours > 23 || minutes < 0 || minutes >= 60) {
                    alert("Format waktu tidak valid. Harap masukkan dalam format HH:MM.");
                    return;
                }

                // Save value as float
                this._setValue((hours + minutes / 60).toFixed(2)); // Store as float
                this.$input.val((hours < 10 ? '0' : '') + hours + ':' + (minutes < 10 ? '0' : '') + minutes); // Format HH:MM
                ev.preventDefault(); // Prevent default event
            }
        },
    });

    fieldRegistry.add('float_time', TimeInputFormat);
});
