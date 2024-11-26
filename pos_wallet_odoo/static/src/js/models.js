odoo.define('pos_wallet_odoo.models', function(require){
    'use strict';
    const models = require('point_of_sale.models');
    
    models.load_fields('res.partner', ['has_wallet_pin', 'wallet_pin', 'barcode_santri']);

    const _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            const partner_model = this.models.find(model => model.model === 'res.partner');
            partner_model.fields.push('has_wallet_pin', 'wallet_pin', 'barcode_santri');
            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });
});
