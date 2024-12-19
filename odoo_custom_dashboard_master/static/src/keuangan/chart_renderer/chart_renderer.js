/** @odoo-module */
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const { Component, onWillStart, useRef, onMounted, onWillUnmount, onWillUpdateProps } = owl;
import { useService } from "@web/core/utils/hooks";

export class KeuanganChartRenderer extends Component {
    static props = {
        type: { type: String },
        title: { type: String },
        startDate: { type: String, optional: true },
        endDate: { type: String, optional: true }
    };
 
    setup() {
        this.chartRef = useRef("chart");
        this.loadingOverlayRef = useRef("loadingOverlay");
        this.orm = useService('orm');
        this.actionService = useService("action");
        this.state = {
            chartData: { series: [], labels: [] }
        };
        this.chartInstance = null;
        this.countdownInterval = null;
        this.countdownTime = 10;
        this.isCountingDown = false;

        if (this.props.startDate && this.props.endDate) {
            this.state.isFiltered = true;
        }

        this.fetchData(this.props.startDate, this.props.endDate);

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.startDate !== this.props.startDate || 
                nextProps.endDate !== this.props.endDate
            ) {
                this.showLoading();
                try {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                this.state.isFiltered = !!(nextProps.startDate && nextProps.endDate);

                await Promise.all([
                    await this.fetchData(this.state.currentStartDate, this.state.currentEndDate)
                ]);
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                this.hideLoading();
            }
        }
        });

        onWillStart(async () => {
            this.showLoading();
            try {
            await loadJS("https://cdn.jsdelivr.net/npm/apexcharts");
            await Promise.all([
                await this.fetchData(this.state.currentStartDate, this.state.currentEndDate)
            ]);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            this.hideLoading();
        }
        });

        onMounted(() => {
            this.renderChart();
            this.attachEventListeners();
        });

        onWillUnmount(() => {
            this.cleanup();
        });
    }

    showLoading() {
        // Create loading overlay if it doesn't exist
        if (!this.loadingOverlay) {
          this.loadingOverlay = document.createElement('div');
          this.loadingOverlay.innerHTML = `
            <div class="musyrif-loading-overlay" style="
              position: fixed;
              top: 0;
              left: 0;
              width: 100%;
              height: 100%;
              background: rgba(0, 0, 0, 0.3);
              display: flex;
              justify-content: center;
              align-items: center;
              z-index: 9999;
            ">
              <div class="loading-spinner">
                <i class="fas fa-sync-alt fa-spin fa-3x text-white"></i>
              </div>
            </div>
          `;
          document.body.appendChild(this.loadingOverlay);
        }
            // Ensure loading overlay is visible
            if (this.loadingOverlay) {
              this.loadingOverlay.style.display = 'flex';
            }
            
            this.state.isLoading = true;
          }
    
          hideLoading() {
            // Hide loading overlay
            if (this.loadingOverlay) {
              this.loadingOverlay.style.display = 'none';
            }
            
            this.state.isLoading = false;
          }

    cleanup() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
        this.clearIntervals();
    }

    toggleCountdown() { 
        if (this.isCountingDown) { 
          this.clearIntervals(); 
          document.getElementById("timerIcon").className = "fas fa-stopwatch "; 
          document.getElementById("timerCountdown").textContent = ""; 
        } else { 
          this.startCountdown(); 
          document.getElementById("timerIcon").className = "fas fa-stop d-none"; 
        } 
        this.isCountingDown = !this.isCountingDown; 
    } 
     
    startCountdown() { 
        this.countdownTime = 10; 
        this.updateCountdownDisplay(); 
        this.countdownInterval = setInterval(() => { 
            this.countdownTime--; 
            if (this.countdownTime < 0) { 
                this.countdownTime = 10; 
                this.refreshChart(); 
            } 
            this.updateCountdownDisplay(); 
        }, 1000); 
    } 
     
    updateCountdownDisplay() { 
        document.getElementById("timerCountdown").textContent = this.countdownTime; 
    } 

    async refreshChart() {
        this.showLoading();
        // Use filtered dates if filtering is active
        const startDate = this.state.isFiltered ? this.state.currentStartDate : null;
        const endDate = this.state.isFiltered ? this.state.currentEndDate : null;

        try {
            await Promise.all([
                await this.fetchData(startDate, endDate)
            ]);
        
        
        if (this.chartInstance) {
            this.chartInstance.updateOptions({
                series: this.state.chartData.series,
                xaxis: {
                    categories: this.state.chartData.labels
                }
            }, true, true);
        }
    } catch (error) {
        console.error("Error fetching data:", error);
    } finally {
        this.hideLoading();
    }
}
     
    clearIntervals() { 
        if (this.countdownInterval) clearInterval(this.countdownInterval); 
        if (this.refreshInterval) clearInterval(this.refreshInterval); 
    }

    attachEventListeners() {
        const timerButton = document.getElementById("timerButton");
        if (timerButton) {
            const timerButton = document.getElementById("timerButton"); 
            timerButton.addEventListener("click", this.toggleCountdown.bind(this));
        }

        // Add date filter listeners
        const startDateInput = document.querySelector('input[name="start_date"]');
        const endDateInput = document.querySelector('input[name="end_date"]');

        if (startDateInput && endDateInput) {
            startDateInput.addEventListener('change', () => this.handleDateFilter());
            endDateInput.addEventListener('change', () => this.handleDateFilter());
        }
    }

    handleDateFilter() {
        const startDateInput = document.querySelector('input[name="start_date"]');
        const endDateInput = document.querySelector('input[name="end_date"]');
    
        if (startDateInput && endDateInput) {
            const startDate = startDateInput.value;
            const endDate = endDateInput.value;
    
            // Cek apakah tanggal yang dimasukkan valid
            if (this.isValidDate(startDate) && this.isValidDate(endDate)) {
                // Format tanggal agar sesuai dengan format yang diharapkan oleh Odoo
                const formattedStartDate = this.formatDateToOdoo(startDate);
                const formattedEndDate = this.formatDateToOdoo(endDate);
    
                // Update state dengan nilai filter baru
                this.state.currentStartDate = formattedStartDate;
                this.state.currentEndDate = formattedEndDate;
                this.state.isFiltered = true;
    
                // Ambil data baru berdasarkan rentang tanggal
                this.fetchData(formattedStartDate, formattedEndDate);
            } else {
                // Jika tanggal tidak valid atau kosong, reset filter dan ambil data tanpa filter
                this.state.currentStartDate = null;
                this.state.currentEndDate = null;
                this.state.isFiltered = false;
                this.fetchData();
            }
        }
    }
    
    // Fungsi untuk memeriksa apakah tanggal valid
    isValidDate(date) {
        const regex = /^\d{4}-\d{2}-\d{2}$/; // Format YYYY-MM-DD
        return regex.test(date); // Cek apakah tanggal sesuai dengan format
    }
    
    // Fungsi untuk format tanggal ke format Odoo (misalnya, YYYY-MM-DD)
    formatDateToOdoo(date) {
        const parsedDate = new Date(date);
        const year = parsedDate.getFullYear();
        const month = (parsedDate.getMonth() + 1).toString().padStart(2, '0'); // Menambahkan leading zero jika bulan kurang dari 10
        const day = parsedDate.getDate().toString().padStart(2, '0'); // Menambahkan leading zero jika hari kurang dari 10
    
        return `${year}-${month}-${day}`;
    }
    

    formatDateToOdoo(dateString) {
        const date = new Date(dateString);
        return date.toISOString().split('.')[0] + 'Z';
    }

    async fetchData(startDate = null, endDate = null) {
        try {
            // Reset chartData to a safe state before fetching
            this.state.chartData = { series: [], labels: [] };
    
            // Existing fetch logic remains the same
            switch (this.props.title) {
                case 'Tagihan Siswa':
                    await this.fetchTagihanData(startDate, endDate);
                    break;
                case 'Uang Saku Masuk':
                    await this.fetchUangSakuMasukData(startDate, endDate);
                    break;
                case 'Uang Saku Keluar':
                    await this.fetchUangSakuKeluarData(startDate, endDate);
                    break;
            }
            
            // Aggressive validation and fallback
            const isEmptyData = !this.state.chartData.series || 
                                this.state.chartData.series.length === 0 || 
                                this.state.chartData.series.every(series => 
                                    !series.data || series.data.length === 0 || 
                                    series.data.every(value => value === 0)
                                );
    
            if (isEmptyData) {
                this.state.chartData = {
                    labels: [],
                    series: [{
                        name: this.props.title,
                        type: this.props.type === 'bar' ? 'bar' : 'area',
                        data: []
                    }]
                };
            }
    
            // Consistent rendering logic
            if (this.chartRef.el) {
                this.renderChart();
            }
    
        } catch (error) {
            console.error('Error in fetchData:', error);
            
            // Ensure a clean, fallback chart state
            this.state.chartData = {
                labels: [],
                series: [{
                    name: this.props.title,
                    type: this.props.type === 'bar' ? 'bar' : 'area',
                    data: []
                }]
            };
            
            if (this.chartRef.el) {
                this.renderChart();
            }
        }
    }
    // Add this new method to validate chart data
    isValidChartData(chartData) {
        return chartData && 
               Array.isArray(chartData.series) && 
               chartData.series.length > 0 &&
               Array.isArray(chartData.labels) &&
               chartData.labels.length > 0;
    }

    // Add this new method to reset the chart
    resetChart() {
        this.state.chartData = { series: [], labels: [] };
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    }

    updateChart() {
        if (!this.isValidChartData(this.state.chartData)) {
            console.warn('Attempting to update chart with invalid data');
            return;
        }

        if (this.chartInstance) {
            const updatedSeries = this.state.chartData.series.map(series => ({
                ...series,
                data: series.data.map(value => value || 0) // Ensure all values are numbers
            }));

            this.chartInstance.updateOptions({
                xaxis: {
                    categories: this.state.chartData.labels
                },
                series: updatedSeries
            }, true, true);
        }
    }


    formatDate(date) {
        return date.toISOString().split('.')[0] + 'Z';
    }

    parseDate(dateStr) {
        const date = new Date(dateStr);
        return new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
    }

    processDateData(data, field) {
        return data.reduce((acc, record) => {
            const date = this.parseDate(record.create_date);
            const dateStr = date.toLocaleDateString('id-ID', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });

            if (!acc[dateStr]) {
                acc[dateStr] = 0;
            }
            acc[dateStr] += record[field] || 0;
            return acc;
        }, {});
    }

    async fetchTagihanData(startDate = null, endDate = null) {
        try {
            // Existing invoice domain
            const domain = [
                ['move_id.move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']],
                ['display_type', 'in', ['product']],
                ['product_id', '!=', false]
            ];

            // Add date filters if provided
            if (startDate) {
                domain.push(['date', '>=', startDate]);
            }
            if (endDate) {
                domain.push(['date', '<=', endDate]);
            }

            // Fetch both debit and credit data
            const result = await this.orm.searchRead(
                'account.move.line',
                domain,
                ['date', 'product_id', 'move_id', 'parent_state', 'name', 'quantity', 'credit'],
                { order: 'date asc' }
            );

            if (!result || result.length === 0) {
                this.state.chartData = { series: [], labels: [] };
                return;
            }

            // Process data including credit
            const processedData = this.processTagihanData(result);
            this.state.chartData = processedData;
            this.renderChart();
        } catch (error) {
            console.error('Error fetching tagihan data:', error);
            this.state.chartData = { series: [], labels: [] };
            this.renderChart();
        }
    }

    async fetchUangSakuMasukData(startDate = null, endDate = null) {
        try {
            if (this.loading) return; // Prevent stacked calls
            this.loading = true;
    
            const today = new Date();
            startDate = startDate || new Date(today.getFullYear(), today.getMonth(), 1).toISOString();
            endDate = endDate || new Date(today.getFullYear(), today.getMonth() + 1, 0).toISOString();
    
            const domain = [
                ['amount_in', '>', 0],
                ['create_date', '>=', startDate],
                ['create_date', '<=', endDate]
            ];
    
            const result = await this.orm.searchRead(
                'cdn.uang_saku',
                domain,
                ['create_date', 'amount_in', 'state'],
                { order: 'create_date asc', limit: 1000 } // Add a reasonable limit
            );
    
            // Handle empty result explicitly
            if (!result || result.length === 0) {
                this.state.chartData = { 
                    labels: [],
                    series: [{
                        name: 'Uang Masuk', 
                        type: 'area', 
                        data: []
                    }]
                };
                
                if (this.chartInstance) {
                    this.renderChart(); // Force render to show "No Data" state
                }
            } else {
                this.processUangSakuData(result, 'amount_in', 'Uang Masuk');
            }
    
            this.state.currentViewRange = {
                startDate,
                endDate,
                viewType: 'masuk'
            };
        } catch (error) {
            console.error('Error fetching uang saku masuk data:', error);
            this.state.chartData = { 
                labels: [], 
                series: [{ 
                    name: 'Uang Masuk', 
                    type: 'area', 
                    data: [] 
                }] 
            };
            
            if (this.chartInstance) {
                this.renderChart(); // Force render to show "No Data" state
            }
        } finally {
            this.loading = false; // Reset loading flag
        }
    }
    
    async fetchUangSakuKeluarData(startDate = null, endDate = null) {
        try {
            // Validate dates to ensure they are not null
            const safeStartDate = startDate || this.getFirstDayOfMonth();
            const safeEndDate = endDate || this.getLastDayOfMonth();
    
            const domain = [
                ['amount_out', '>', 0],
                ['create_date', '>=', safeStartDate],
                ['create_date', '<=', safeEndDate]
            ];
    
            const result = await this.orm.searchRead(
                'cdn.uang_saku',
                domain,
                ['create_date', 'amount_out', 'state'],
                { order: 'create_date asc', limit: 1000 } // Add a reasonable limit
            );
    
            // Handle empty result explicitly
            if (!result || result.length === 0) {
                this.state.chartData = { 
                    labels: [],
                    series: [{
                        name: 'Uang Keluar', 
                        type: 'area', 
                        data: []
                    }]
                };
                
                if (this.chartInstance) {
                    this.renderChart(); // Force render to show "No Data" state
                }
            } else {
                this.processUangSakuData(result, 'amount_out', 'Uang Keluar');
            }
    
            // Store view range in state
            this.state.currentViewRange = {
                startDate: safeStartDate,
                endDate: safeEndDate,
                viewType: 'keluar'
            };
    
        } catch (error) {
            console.error('Error fetching uang saku keluar data:', error);
            this.state.chartData = { 
                labels: [], 
                series: [{ 
                    name: 'Uang Keluar', 
                    type: 'area', 
                    data: [] 
                }] 
            };
            
            if (this.chartInstance) {
                this.renderChart(); // Force render to show "No Data" state
            }
        } finally {
            this.loading = false; 
        }
    }
    
    // Helper to get first day of current month
    getFirstDayOfMonth() {
        const date = new Date();
        date.setDate(1);
        return date.toISOString().split('T')[0]; // Format YYYY-MM-DD
    }
    
    // Helper to get last day of current month
    getLastDayOfMonth() {
        const date = new Date();
        date.setMonth(date.getMonth() + 1);
        date.setDate(0);
        return date.toISOString().split('T')[0]; // Format YYYY-MM-DD
    }
    
    
    
    // isCustomDateRange() {
    //     if (!this.state.currentViewRange) return false;
        
    //     const today = new Date();
    //     const weekAgo = new Date();
    //     weekAgo.setDate(weekAgo.getDate() - 6);
        
    //     const currentStartDate = new Date(this.state.currentViewRange.startDate);
    //     const currentEndDate = new Date(this.state.currentViewRange.endDate);
        
    //     return !(
    //         currentStartDate.toISOString().split('T')[0] === weekAgo.toISOString().split('T')[0] &&
    //         currentEndDate.toISOString().split('T')[0] === today.toISOString().split('T')[0]
    //     );
    // }

    processTagihanData(data) {
        if (!Array.isArray(data) || data.length === 0) {
            return { series: [], labels: [] };
        }
    
        const lunasData = new Map();
        const belumLunasData = new Map();
        const creditData = new Map();
    
        data.forEach(record => {
            const productName = record.product_id && record.product_id[1] ? record.product_id[1] : 'Unknown Product';
            const quantity = record.quantity || 1;
            const credit = record.credit || 0;
    
            if (record.parent_state === 'posted') {
                lunasData.set(productName, (lunasData.get(productName) || 0) + quantity);
            } else {
                belumLunasData.set(productName, (belumLunasData.get(productName) || 0) + quantity);
            }
            

            creditData.set(productName, (creditData.get(productName) || 0) + credit);
        });
    
        // Combine and sort products based on total volume
        const allProducts = new Set([...lunasData.keys(), ...belumLunasData.keys(), ...creditData.keys()]);
        const sortedProducts = Array.from(allProducts)
            .map(product => ({
                name: product,
                total: (lunasData.get(product) || 0) + 
                       (belumLunasData.get(product) || 0)
            }))
            .sort((a, b) => b.total - a.total)
            .slice(0, 10)
            .map(item => item.name);
    
        return {
            labels: sortedProducts,
            series: [
                {
                    name: 'Lunas',
                    data: sortedProducts.map(product => lunasData.get(product) || 0),
                    type: 'bar'
                },
                {
                    name: 'Belum Lunas',
                    data: sortedProducts.map(product => belumLunasData.get(product) || 0),
                    type: 'bar'
                },
                {
                    name: 'Credit',
                    data: sortedProducts.map(product => creditData.get(product) || 0),
                    type: 'line'
                }
            ]
        };
    }

    processUangSakuData(data, field, label) {
        // Ensure data is valid before processing
        if (!data || !Array.isArray(data) || data.length === 0) {
            console.warn('No data available for chart rendering');
            this.state.chartData = { 
                labels: [], 
                series: [{ 
                    name: label, 
                    type: 'area', 
                    data: [] 
                }] 
            };
            return;
        }
    
        try {
            const dateData = this.processDateData(data, field);
            const sortedDates = Object.keys(dateData)
                .sort((a, b) => new Date(a) - new Date(b));
    
            // Ensure data is always an array of numbers
            const processedData = sortedDates.map(date => 
                Math.max(0, Number(dateData[date]) || 0)
            );
    
            this.state.chartData = {
                labels: sortedDates,
                series: [{
                    name: label,
                    type: 'area',
                    data: processedData
                }]
            };
        } catch (error) {
            console.error('Error processing Uang Saku data:', error);
            this.state.chartData = { 
                labels: [], 
                series: [{ 
                    name: label, 
                    type: 'area', 
                    data: [] 
                }] 
            };
        }
    }

    getChartConfig() {
        const baseConfig = {
            chart: {
                height: 450,
                type: this.props.type === 'bar' ? 'bar' : 'area',
                toolbar: {
                    show: false,
                    tools: {
                        download: false,
                        selection: false,
                        zoom: false,
                        zoomin: false,
                        zoomout: false,
                        pan: false,
                    }
                },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800,
                    dynamicAnimation: {
                        enabled: true,
                        speed: 350
                    }
                },
                stacked: true
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '50%',
                    endingShape: 'rounded',
                    borderRadius: 4
                }
            },
            stroke: {
                show: true,
                width: this.props.type === 'bar' ? [0, 0, 3] : [3],
                curve: 'smooth'
            },
            dataLabels: {
                enabled: true,  // Menyalakan data labels untuk bar dan area
                formatter: function (val) {
                    return val.toLocaleString('id-ID');
                },
                style: {
                    colors: this.props.type === 'bar' ? ['#FFFFFF'] : ['#000000']  // Putih untuk bar, hitam untuk area/line
                },
                dropShadow: {
                    enabled: true,
                    top: 1,
                    left: 1,
                    blur: 1,
                    opacity: 0.3
                }
            },
            colors: this.props.type === 'bar'
                ? ['#00E396', '#FF4560', '#2E93fA']
                : ['#00E396'], 
            xaxis: {
                categories: this.state.chartData.labels.map(label => 
                    label.length > 10 ? label.substring(0, 10) + '...' : label
                ),
                labels: {
                    rotate: -45,
                    style: {
                        fontSize: '12px'
                    }
                }
            },
            yaxis: this.props.type === 'bar' ? [
                {
                    title: {
                        text: '',
                        style: {
                            fontSize: '14px',
                            fontWeight: 600
                        }
                    },
                    labels: {
                        formatter: function (value) {
                            return Math.round(value).toLocaleString('id-ID');
                        }
                    }
                },
                {
                    title: {
                        text: '',
                        style: {
                            fontSize: '14px',
                            fontWeight: 600
                        }
                    },
                    labels: {
                        formatter: function (value) {
                            return Math.round(value).toLocaleString('id-ID');
                        }
                    }
                },
                {
                    opposite: true,
                    title: {
                        text: '',
                        style: {
                            fontSize: '14px',
                            fontWeight: 600
                        }
                    },
                    labels: {
                        formatter: function (value) {
                            return value.toLocaleString('id-ID', {
                                style: 'currency',
                                currency: 'IDR',
                                maximumFractionDigits: 0 // Hapus desimal
                            });
                        }
                    }
                }
            ] : {
                title: {
                    text: '',
                    style: {
                        fontSize: '14px',
                        fontWeight: 600
                    }
                },
                labels: {
                    formatter: function (value) {
                        return value.toLocaleString('id-ID', {
                            style: 'currency',
                            currency: 'IDR',
                            maximumFractionDigits: 0 // Hapus desimal
                        });
                    }
                }
            },
            title: {
                text: this.props.title,
                align: 'center',
                style: {
                    fontSize: '16px',
                    fontWeight: 'bold'
                }
            },
            legend: {
                position: 'top',
                horizontalAlign: 'center'
            },
            fill: {
                opacity: this.props.type === 'bar' ? 1 : 0.7,
                type: this.props.type === 'bar' ? 'solid' : 'gradient',
                gradient: this.props.type === 'bar' ? undefined : {
                    shadeIntensity: 1,
                    opacityFrom: 0.7,
                    opacityTo: 0.9,
                    stops: [0, 90, 100]
                }
            },
            tooltip: {
                shared: true,
                intersect: false,
                y: this.props.type === 'bar' ? [
                    {
                        formatter: function (value) {
                            return Math.round(value).toLocaleString('id-ID');
                        }
                    },
                    {
                        formatter: function (value) {
                            return Math.round(value).toLocaleString('id-ID');
                        }
                    },
                    {
                        formatter: function (value) {
                            return value.toLocaleString('id-ID', {
                                style: 'currency',
                                currency: 'IDR',
                                maximumFractionDigits: 0 // Hapus desimal
                            });
                        }
                    }
                ] : {
                    formatter: function (value) {
                        return value.toLocaleString('id-ID', {
                            style: 'currency',
                            currency: 'IDR',
                            maximumFractionDigits: 0 // Hapus desimal
                        });
                    }
                }
            },
            noData: {
                text: 'Tidak ada data',
                align: 'center',
                verticalAlign: 'middle',
                style: {
                    color: '#1f2937',
                    fontSize: '16px',
                    fontFamily: 'Inter'
                }
            }
        };
    
        return baseConfig;
    }
    
    renderChart() {
        // Validate chart reference and data
        if (!this.chartRef.el) {
            console.warn('Cannot render chart: invalid chart element');
            return;
        }
    
        // Destroy existing chart instance if it exists
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
    
        // Clear previous chart content
        this.chartRef.el.innerHTML = '';
    
        // Check if data is completely empty or invalid
        const isEmptyData = !this.state.chartData.series || 
                            this.state.chartData.series.length === 0 || 
                            this.state.chartData.series.every(series => 
                                !series.data || 
                                series.data.length === 0 || 
                                series.data.every(value => value === 0)
                            );
    
        const config = {
            ...this.getChartConfig(),
            series: isEmptyData 
                ? [{ name: 'No Data', data: [] }] 
                : this.state.chartData.series.map(series => ({
                    ...series,
                    data: series.data ? series.data.map(value => Number(value) || 0) : []
                })),
                chart: {
                    ...this.getChartConfig().chart,
                    events: {
                        dataPointSelection: (event, chartContext, config) => {
                            this.onChartClick(event, chartContext, config);
                        },
                        click: (event, chartContext, config) => {
                            if (config.dataPointIndex !== undefined && config.seriesIndex !== undefined) {
                                this.onChartClick(event, chartContext, {
                                    dataPointIndex: config.dataPointIndex,
                                    seriesIndex: config.seriesIndex
                                });
                            }
                        }
                    }
                },
            noData: {
                text: 'Tidak ada data untuk ditampilkan',
                align: 'center',
                verticalAlign: 'middle',
                style: {
                    color: '#6b7280',
                    fontSize: '18px',
                    fontWeight: 'bold'
                }
            }
        };
    
        try {
            this.chartInstance = new ApexCharts(this.chartRef.el, config);
            this.chartInstance.render();
        } catch (error) {
            console.error('Error rendering chart:', error);
            // Potentially add fallback handling or user notification
        }
    }
    
    
    onChartClick(event, chartContext, config) {
        const dataPointIndex = config.dataPointIndex;
        const seriesIndex = config.seriesIndex;
    
        if (dataPointIndex === -1 || seriesIndex === -1) return;

        if (!this.state?.chartData?.labels || !this.state?.chartData?.series) {
            console.error('Chart data is not properly initialized');
            return;
        }
    
        const label = this.state.chartData.labels[dataPointIndex];
        // Pastikan series ada dan memiliki properti name
        const seriesName = this.state.chartData.series[seriesIndex]?.name || 'Unknown';
    
        // Pastikan label ada
        if (!label) {
            console.error('Label not found for dataPointIndex:', dataPointIndex);
            return;
        }
    
        let actionConfig = {
            type: 'ir.actions.act_window',
            name: `${this.props.title} - ${seriesName}`,
            view_mode: 'list,form',
            target: 'current',
            views: [[false, 'list'], [false, 'form']],
            context: {},
        };
    
        switch (this.props.title) {
            case 'Tagihan Siswa': {
                actionConfig.res_model = 'account.move.line';
                const domain = [
                    ['move_id.move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']],
                    ['display_type', 'in', ['product']]
                ];
    
                // Hanya tambahkan product_id.name ke domain jika label valid
                if (label) {
                    domain.push(['product_id.name', '=', label]);
                }
            
                // Menambahkan kondisi berdasarkan status Lunas/Belum Lunas
                if (seriesName === 'Lunas') {
                    domain.push(['parent_state', '=', 'posted']);
                } else {
                    domain.push(['parent_state', 'in', ['draft', 'cancel']]);
                }
            
                // Pengecekan tanggal yang lebih aman
                if (this.state?.currentStartDate) {
                    try {
                        const start = new Date(this.state.currentStartDate);
                        if (!isNaN(start.getTime())) {
                            start.setUTCHours(0, 0, 0, 0);
                            domain.push(['date', '>=', start.toISOString().split('.')[0] + 'Z']);
                        }
                    } catch (e) {
                        console.error('Invalid start date:', e);
                    }
                }
    
                if (this.state?.currentEndDate) {
                    try {
                        const end = new Date(this.state.currentEndDate);
                        if (!isNaN(end.getTime())) {
                            end.setUTCHours(23, 59, 59, 999);
                            domain.push(['date', '<=', end.toISOString().split('.')[0] + 'Z']);
                        }
                    } catch (e) {
                        console.error('Invalid end date:', e);
                    }
                }
            
                actionConfig.domain = domain;
                break;
            }
    
            case 'Uang Saku Masuk':
            case 'Uang Saku Keluar': {
                actionConfig.res_model = 'cdn.uang_saku';
                try {
                    const [day, month, year] = label.split('/');
                    if (!day || !month || !year) {
                        console.error('Invalid date format in label:', label);
                        return;
                    }
    
                    const startDate = new Date(year, month - 1, day);
                    const endDate = new Date(year, month - 1, day);
    
                    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
                        console.error('Invalid date created from label:', label);
                        return;
                    }
    
                    startDate.setHours(0, 0, 0, 0);
                    endDate.setHours(23, 59, 59, 999);
    
                    const formattedStartDate = startDate.toISOString().split('.')[0];
                    const formattedEndDate = endDate.toISOString().split('.')[0];
    
                    actionConfig.domain = this.props.title === 'Uang Saku Masuk'
                        ? [
                            ['amount_in', '>', 0],
                            ['create_date', '>=', formattedStartDate],
                            ['create_date', '<=', formattedEndDate]
                        ]
                        : [
                            ['amount_out', '>', 0],
                            ['create_date', '>=', formattedStartDate],
                            ['create_date', '<=', formattedEndDate]
                        ];
                } catch (e) {
                    console.error('Error processing date:', e);
                    return;
                }
                break;
            }
    
            default:
                console.error('Unhandled title:', this.props.title);
                return;
        }
    
        // Pastikan actionService tersedia sebelum memanggil
        if (this.actionService?.doAction) {
            this.actionService.doAction(actionConfig);
        } else {
            console.error('Action service not available');
        }
    }
}

KeuanganChartRenderer.template = 'owl.KeuanganChartRenderer';