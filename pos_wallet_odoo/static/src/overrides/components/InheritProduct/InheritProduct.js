/** @odoo-module */

import { ProductCard as ProductCardCustom } from "@point_of_sale/app/generic_components/product_card/product_card";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(ProductCardCustom.prototype, {
    setup() {
        super.setup(...arguments);

        // Inisialisasi stok produk
        if (this.props.name) {
            this._fetchProductStock(this.props.name)
                .then((stockData) => {
                    this.props.stock = stockData ? stockData.qty_available : 0;  // Set ke 0 jika tidak ada stok
                    console.log("Stock updated:", this.props.stock);
                    this.triggerUpdate();  // Memastikan tampilan diperbarui setelah stok diubah
                })
                .catch((error) => {
                    console.error("Error fetching stock data:", error);
                    this.props.stock = 0;  // Defaultkan ke 0 jika gagal
                    this.triggerUpdate();  // Memastikan tampilan diperbarui jika gagal
                });
        } else {
            console.warn("Product name is missing, unable to fetch stock.");
        }
    },

    // Fungsi untuk mengambil data stok produk
    async _fetchProductStock(productName) {
        const apiUrl = "/api/product_stock";
        try {
            const response = await rpc(apiUrl, { domain: [['name', 'ilike', productName]] }, {
                headers: { "accept": "application/json" },
            });
            return response.length > 0 ? response[0] : null; // Pastikan ada produk dalam response
        } catch (error) {
            console.error(`Error fetching stock data for Product Name ${productName}:`, error);
            return null;
        }
    },

    triggerUpdate() {
        // Pastikan UI dirender ulang
        this.render();
    },
});
