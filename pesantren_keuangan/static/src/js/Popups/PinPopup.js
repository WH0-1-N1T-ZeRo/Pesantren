odoo.define('pesantren_keuangan.PinPopup', require => {
    'use strict';
    const NumberPopup = require("point_of_sale.NumberPopup");
    const { parse } = require('web.field_utils');
    const { useState } = require("owl")
    const Registries = require('point_of_sale.Registries');

    const Popup = (NumberPopup) =>
      class extends NumberPopup {
               setup(){
                   this.state = useState({
                       inputPIN : '',
                       inputHasError: false,
                   });
               }
       
               confirm(){
                   try {
                       parse.integer(this.state.inputPIN);
                   } catch (error) {
                       this.state.inputHasError = true;
                       return;
                   }
                   return super.confirm();
               }
       
               getPayload(){
                   return {
                       pin : this.state.inputPIN
                   };
               }
    }
    Registries.Component.extend(NumberPopup, Popup);
         return Popup;
});