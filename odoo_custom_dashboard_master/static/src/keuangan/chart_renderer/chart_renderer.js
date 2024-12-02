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
                nextProps.endDate !== this.props.endDate) {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                this.state.isFiltered = !!(nextProps.startDate && nextProps.endDate);
                await this.fetchData(this.state.currentStartDate, this.state.currentEndDate);
            }
        });

        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/apexcharts");
            await this.fetchData(this.state.currentStartDate, this.state.currentEndDate);
        });

        onMounted(() => {
            this.renderChart();
            this.attachEventListeners();
        });

        onWillUnmount(() => {
            this.cleanup();
        });
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
        // Use filtered dates if filtering is active
        const startDate = this.state.isFiltered ? this.state.currentStartDate : null;
        const endDate = this.state.isFiltered ? this.state.currentEndDate : null;
        
        await this.fetchData(startDate, endDate);
        
        if (this.chartInstance) {
            this.chartInstance.updateOptions({
                series: this.state.chartData.series,
                xaxis: {
                    categories: this.state.chartData.labels
                }
            }, true, true);
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

            if (startDate && endDate) {
                // Format dates to match Odoo's expected format
                const formattedStartDate = this.formatDateToOdoo(startDate);
                const formattedEndDate = this.formatDateToOdoo(endDate);

                // Update state with new filter values
                this.state.currentStartDate = formattedStartDate;
                this.state.currentEndDate = formattedEndDate;
                this.state.isFiltered = true;

                // Fetch new data with date range
                this.fetchData(formattedStartDate, formattedEndDate);
            } else {
                // If either date is cleared, remove filtering
                this.state.currentStartDate = null;
                this.state.currentEndDate = null;
                this.state.isFiltered = false;
                this.fetchData();
            }
        }
    }

    formatDateToOdoo(dateString) {
        const date = new Date(dateString);
        return date.toISOString().split('.')[0] + 'Z';
    }

    async fetchData(startDate = null, endDate = null) {
        // Jika tanggal diberikan, format ke format Odoo
        const formattedStartDate = startDate ? this.formatDateToOdoo(startDate) : null;
        const formattedEndDate = endDate ? this.formatDateToOdoo(endDate) : null;

        switch (this.props.title) {
            case 'Tagihan Siswa':
                await this.fetchTagihanData(formattedStartDate, formattedEndDate);
                break;
            case 'Uang Saku Masuk':
                await this.fetchUangSakuMasukData(formattedStartDate, formattedEndDate);
                break;
            case 'Uang Saku Keluar':
                await this.fetchUangSakuKeluarData(formattedStartDate, formattedEndDate);
                break;
        }
        
        if (this.chartInstance) {
            this.updateChart();
        } else if (this.chartRef.el) {
            this.renderChart();
        }
    }

    updateChart() {
        if (this.chartInstance) {
            this.chartInstance.updateOptions({
                xaxis: {
                    categories: this.state.chartData.labels
                },
                series: this.state.chartData.series
            });
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
            const date = this.parseDate(record.validasi_time);
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
            const domain = [
                ['move_id.move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']],
                ['display_type', 'in', ['product']],
                ['product_id', '!=', false]
            ];

            if (startDate) {
                const start = new Date(startDate);
                start.setUTCHours(0, 0, 0, 0);
                domain.push(['date', '>=', start.toISOString().split('.')[0] + 'Z']);
            }
            if (endDate) {
                const end = new Date(endDate);
                end.setUTCHours(23, 59, 59, 999);
                domain.push(['date', '<=', end.toISOString().split('.')[0] + 'Z']);
            }

            const result = await this.orm.searchRead(
                'account.move.line',
                domain,
                ['date', 'product_id', 'move_id', 'parent_state', 'name', 'quantity'],
                { order: 'date asc' }
            );

            if (!result || result.length === 0) {
                this.state.chartData = { series: [], labels: [] };
                return;
            }
            this.processTagihanData(result);
        } catch (error) {
            console.error('Error fetching tagihan data:', error);
            this.state.chartData = { series: [], labels: [] };
        }
    }


    async fetchUangSakuMasukData(startDate = null, endDate = null) {
        try {
            let domain = [['amount_in', '>', 0]];
    
            // If no dates provided, set default to current week
            if (!startDate || !endDate) {
                const now = new Date();
                const firstDayOfWeek = new Date(now.setDate(now.getDate() - now.getDay()));
                startDate = firstDayOfWeek.toISOString().split('T')[0];
                endDate = new Date().toISOString().split('T')[0];
            }
    
            // Convert dates to ISO string format
            startDate = new Date(startDate).toISOString().split('T')[0];
            endDate = new Date(endDate).toISOString().split('T')[0];
            
            // Add date filtering
            domain.push(
                ['validasi_time', '>=', startDate],
                ['validasi_time', '<=', endDate]
            );
    
            const result = await this.orm.searchRead(
                'cdn.uang_saku',
                domain,
                ['validasi_time', 'amount_in', 'state'],
                { order: 'validasi_time asc' }
            );
    
            if (!result || result.length === 0) {
                this.state.chartData = { series: [], labels: [] };
                return;
            }
    
            // Store the current view range in state
            this.state.currentViewRange = {
                startDate,
                endDate,
                viewType: 'masuk'
            };
    
            this.processUangSakuData(result, 'amount_in', 'Uang Masuk');
        } catch (error) {
            console.error('Error fetching uang saku masuk data:', error);
            this.state.chartData = { series: [], labels: [] };
            this.state.currentViewRange = null;
        }
    }
    
    async fetchUangSakuKeluarData(startDate = null, endDate = null) {
        try {
            let domain = [['amount_out', '>', 0]];
    
            // If no dates provided, set default to current week
            if (!startDate || !endDate) {
                const now = new Date();
                const firstDayOfWeek = new Date(now.setDate(now.getDate() - now.getDay()));
                startDate = firstDayOfWeek.toISOString().split('T')[0];
                endDate = new Date().toISOString().split('T')[0];
            }
    
            // Convert dates to ISO string format
            startDate = new Date(startDate).toISOString().split('T')[0];
            endDate = new Date(endDate).toISOString().split('T')[0];
            
            // Add date filtering
            domain.push(
                ['validasi_time', '>=', startDate],
                ['validasi_time', '<=', endDate]
            );
    
            const result = await this.orm.searchRead(
                'cdn.uang_saku',
                domain,
                ['validasi_time', 'amount_out', 'state'],
                { order: 'validasi_time asc' }
            );
    
            if (!result || result.length === 0) {
                this.state.chartData = { series: [], labels: [] };
                return;
            }
    
            // Store the current view range in state
            this.state.currentViewRange = {
                startDate,
                endDate,
                viewType: 'keluar'
            };
    
            this.processUangSakuData(result, 'amount_out', 'Uang Keluar');
        } catch (error) {
            console.error('Error fetching uang saku keluar data:', error);
            this.state.chartData = { series: [], labels: [] };
            this.state.currentViewRange = null;
        }
    }
    
    isCustomDateRange() {
        if (!this.state.currentViewRange) return false;
        
        const today = new Date();
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 6);
        
        const currentStartDate = new Date(this.state.currentViewRange.startDate);
        const currentEndDate = new Date(this.state.currentViewRange.endDate);
        
        // Check if current range matches default week range
        return !(
            currentStartDate.toISOString().split('T')[0] === weekAgo.toISOString().split('T')[0] &&
            currentEndDate.toISOString().split('T')[0] === today.toISOString().split('T')[0]
        );
    }

    processTagihanData(data) {
        if (!Array.isArray(data) || data.length === 0) {
            this.state.chartData = { series: [], labels: [] };
            return;
        }

        // Separate data into lunas and belum lunas
        const lunasData = new Map();
        const belumLunasData = new Map();

        // Process each record
        data.forEach(record => {
            const productName = record.product_id[1];
            const quantity = record.quantity || 1;

            if (record.parent_state === 'posted') {
                lunasData.set(productName, (lunasData.get(productName) || 0) + quantity);
            } else {
                belumLunasData.set(productName, (belumLunasData.get(productName) || 0) + quantity);
            }
        });

        // Combine and sort products by total quantity
        const allProducts = new Set([...lunasData.keys(), ...belumLunasData.keys()]);
        const sortedProducts = Array.from(allProducts)
            .map(product => ({
                name: product,
                total: (lunasData.get(product) || 0) + (belumLunasData.get(product) || 0)
            }))
            .sort((a, b) => b.total - a.total)
            .slice(0, 10)
            .map(item => item.name);

        // Prepare chart data
        this.state.chartData = {
            labels: sortedProducts,
            series: [
                {
                    name: 'Lunas',
                    data: sortedProducts.map(product => lunasData.get(product) || 0),
                    clickable: true
                },
                {
                    name: 'Belum Lunas',
                    data: sortedProducts.map(product => belumLunasData.get(product) || 0),
                    clickable: true
                }
            ]
        };
    }

    processUangSakuData(data, field, label) {
        if (!Array.isArray(data) || data.length === 0) {
            this.state.chartData = { series: [], labels: [] };
            return;
        }

        const dateData = this.processDateData(data, field);
        const sortedDates = Object.keys(dateData).sort((a, b) => new Date(a) - new Date(b));

        this.state.chartData = {
            labels: sortedDates,
            series: [{
                name: label,
                data: sortedDates.map(date => dateData[date] || 0)
            }]
        };
    }

    getChartConfig() {
        const baseConfig = {
            chart: {
                type: this.props.type === 'bar' ? 'bar' : 'area',
                height: 450,
                stacked: true, // Enable stacking for better visualization
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
                events: {
                    dataPointSelection: (event, chartContext, config) => {
                        this.onChartClick(event, chartContext, config);
                    },
                    click: (event, chartContext, config) => {
                        // Handle area chart clicks
                        if (config.dataPointIndex !== undefined && config.seriesIndex !== undefined) {
                            this.onChartClick(event, chartContext, {
                                dataPointIndex: config.dataPointIndex,
                                seriesIndex: config.seriesIndex
                            });
                        }
                    }
                }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '70%',
                    endingShape: 'rounded',
                    borderRadius: 4,
                    dataLabels: {
                        position: 'top'
                    }
                },
                area: {
                    // Add specific configuration for area chart
                    clickable: true,
                    dataLabels: {
                        enabled: false
                    }
                }
            },
            colors: ['#00E396', '#FF4560'],
            dataLabels: {
                enabled: true,
                formatter: function(val) {
                    return val.toLocaleString('id-ID');
                },
                style: {
                    fontSize: '12px',
                    colors: ['#333']
                },
                offsetY: -20
            },
            title: {
                text: this.props.title,
                align: 'center',
                style: {
                    fontSize: '18px',
                    fontWeight: '600',
                    fontFamily: 'Inter, sans-serif',
                }
            },
            xaxis: {
                categories: this.state.chartData.labels,
                labels: {
                    rotate: -45,
                    style: {
                        fontSize: '12px',
                        fontFamily: 'Inter, sans-serif'
                    }
                },
                axisBorder: {
                    show: true
                },
                axisTicks: {
                    show: true
                }
            },
            yaxis: {
                labels: {
                    formatter: function(value) {
                        if (value === undefined || value === null) return '0';
                        return value.toLocaleString('id-ID');
                    },
                    style: {
                        fontSize: '12px'
                    }
                },
                min: 0,
                tickAmount: 5,
                forceNiceScale: true
            },
            markers: {
                size: 6,
                strokeWidth: 2,
                strokeColor: "#fff",
                strokeOpacity: 1,
                hover: {
                    size: 8
                },
                onClick: (e) => {
                    if (e.dataPointIndex !== undefined && e.seriesIndex !== undefined) {
                        this.onChartClick(e, null, {
                            dataPointIndex: e.dataPointIndex,
                            seriesIndex: e.seriesIndex
                        });
                    }
                }
            },
            points: {
                show: true,
                radius: 10, // Larger click radius
            },
            legend: {
                position: 'top',
                horizontalAlign: 'center',
                offsetY: 0,
                itemMargin: {
                    horizontal: 10,
                    vertical: 5
                }
            },
            tooltip: {
                shared: true,
                intersect: false,
                y: {
                    formatter: function(value) {
                        return value.toLocaleString('id-ID');
                    }
                }
            },
            states: {
                hover: {
                    filter: {
                        type: 'lighten',
                        value: 0.15,
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: {
                        type: 'darken',
                        value: 0.35,
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
        if (!this.chartRef.el) return;
    
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    
        this.chartRef.el.innerHTML = '';
    
        const config = {
            ...this.getChartConfig(),
            series: this.state.chartData.series.map(series => ({
                ...series,
                data: series.data.map(value => value || 0)
            }))
        };
        if (this.props.type !== 'bar') {
            const originalMouseMove = config.chart.events.mouseMove;
            config.chart.events.mouseMove = (event, chartContext, config) => {
                if (originalMouseMove) {
                    originalMouseMove(event, chartContext, config);
                }
                
                const el = event.target;
                if (el.classList.contains('apexcharts-marker')) {
                    el.style.cursor = 'pointer';
                }
            };
        }
    
        try {
            this.chartInstance = new ApexCharts(this.chartRef.el, config);
            this.chartInstance.render();
        } catch (error) {
            console.error('Error rendering chart:', error);
        }
    }
    
    onChartClick(event, chartContext, config) {
        const dataPointIndex = config.dataPointIndex;
        const seriesIndex = config.seriesIndex;
    
        // Guard clause untuk mengecek index yang valid
        if (dataPointIndex === -1 || seriesIndex === -1) return;
    
        // Pastikan data chart tersedia
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
                            ['validasi_time', '>=', formattedStartDate],
                            ['validasi_time', '<=', formattedEndDate]
                        ]
                        : [
                            ['amount_out', '>', 0],
                            ['validasi_time', '>=', formattedStartDate],
                            ['validasi_time', '<=', formattedEndDate]
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