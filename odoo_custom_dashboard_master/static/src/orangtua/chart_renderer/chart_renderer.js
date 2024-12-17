/** @odoo-module */
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const { Component, onWillStart, useRef, onMounted, onWillUnmount, onWillUpdateProps } = owl;
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

// Penting
export class OrangtuaChartRenderer extends Component {
    static props = {
        type: { type: String },
        title: { type: String },
        period: { type: String, optional: true },
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
            if (
                nextProps.startDate !== this.props.startDate ||
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
                    console.error("Error updating props:", error);
                }
                this.hideLoading();
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
                console.error("Error updating props:", error);
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
        console.error("Error refreshing chart:", error);
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
            case 'Uang Masuk':
                await this.fetchUangSakuMasukData(formattedStartDate, formattedEndDate);
                break;
            case 'Uang Keluar':
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
            const domain = [
                ['move_type', 'in', ['out_invoice', 'out_refund']],
                ['partner_id', '!=', false],
                ['state', '!=', 'cancel'],
                ["orangtua_id", "ilike", session.partner_display_name]
            ];

            if (startDate) domain.push(['invoice_date', '>=', startDate]);
            if (endDate) domain.push(['invoice_date', '<=', endDate]);

            const invoices = await this.orm.searchRead(
                'account.move',
                domain,
                ['partner_id', 'state', 'invoice_line_ids', 'orangtua_id', 'invoice_date']
            );

            if (!invoices || invoices.length === 0) {
                this.state.chartData = { series: [], labels: [] };
                return;
            }

            const allInvoiceLineIds = invoices.flatMap(inv => inv.invoice_line_ids);

            const invoiceLines = await this.orm.searchRead(
                'account.move.line',
                [
                    ['id', 'in', allInvoiceLineIds],
                    ['display_type', 'in', ['product']],
                    ['product_id', '!=', false]
                ],
                ['move_id', 'product_id', 'quantity', 'parent_state', 'price_unit']
            );

            // Create a map of invoice IDs to their states
            const invoiceStateMap = new Map(
                invoices.map(inv => [inv.id, {
                    state: inv.state,
                    partner_id: inv.partner_id,
                    invoice_date: inv.invoice_date
                }])
            );

            // Process invoice lines with complete context
            const enrichedData = invoiceLines.map(line => {
                const invoiceInfo = invoiceStateMap.get(line.move_id[0]);
                if (!invoiceInfo) return null;

                return {
                    ...line,
                    invoice_state: invoiceInfo.state,
                    partner_id: invoiceInfo.partner_id,
                    invoice_date: invoiceInfo.invoice_date
                };
            }).filter(line => line !== null);

            this.processTagihanData(enrichedData);
        } catch (error) {
            console.error('Error fetching tagihan data:', error);
            this.state.chartData = { series: [], labels: [] };
        }
    }

    async fetchUangSakuMasukData(startDate = null, endDate = null) {
        try {
            if (!startDate && !endDate) {
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 6); // Get last 7 days including today

                // Convert to YYYY-MM-DD format for API
                startDate = startDate.toISOString().split('T')[0];
                endDate = endDate.toISOString().split('T')[0];
            }

            const domain = [
                ['amount_in', '>', 0],
                ['create_date', '>=', startDate],
                ['create_date', '<=', endDate],
                ["orangtua_id", "ilike", session.partner_display_name]
            ];

            const result = await this.orm.searchRead(
                'cdn.uang_saku',
                domain,
                ['create_date', 'amount_in', 'state', 'siswa_id', 'orangtua_id'],
                { order: 'create_date asc' }
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
            // If no dates provided, set default range to last 7 days
            if (!startDate && !endDate) {
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 6); // Get last 7 days including today

                // Convert to YYYY-MM-DD format for API
                startDate = startDate.toISOString().split('T')[0];
                endDate = endDate.toISOString().split('T')[0];
            }

            const domain = [
                ['amount_out', '>', 0],
                ['create_date', '>=', startDate],
                ['create_date', '<=', endDate],
                ["orangtua_id", "ilike", session.partner_display_name]
            ];

            const result = await this.orm.searchRead(
                'cdn.uang_saku',
                domain,
                ['create_date', 'amount_out', 'state', 'siswa_id', 'orangtua_id'],
                { order: 'create_date asc' }

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

    // Helper methods for managing date ranges
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

    resetToDefaultWeekView() {
        const viewType = this.state.currentViewRange?.viewType;
        if (viewType === 'masuk') {
            this.fetchUangSakuMasukData();
        } else if (viewType === 'keluar') {
            this.fetchUangSakuKeluarData();
        }
    }

    processTagihanData(data) {
        if (!Array.isArray(data) || data.length === 0) {
            this.state.chartData = { series: [], labels: [] };
            return;
        }

        // Group by student with complete invoice line information
        const studentStats = data.reduce((acc, record) => {
            const partnerId = record.partner_id[0];
            const partnerName = record.partner_id[1];

            if (!acc[partnerId]) {
                acc[partnerId] = {
                    name: partnerName,
                    lunas: [],
                    belumLunas: [],
                    total: 0
                };
            }

            const lineInfo = {
                line_id: record.id,
                move_id: record.move_id[0],
                product_id: record.product_id,
                quantity: record.quantity || 0,
                price_unit: record.price_unit,
                invoice_date: record.invoice_date
            };

            if (record.parent_state === 'posted') {
                acc[partnerId].lunas.push(lineInfo);
            } else {
                acc[partnerId].belumLunas.push(lineInfo);
            }
            acc[partnerId].total += record.quantity || 0;

            return acc;
        }, {});

        // Convert to array and sort
        const processedData = Object.entries(studentStats)
            .map(([id, stats]) => ({
                id,
                name: stats.name,
                lunas: stats.lunas,
                belumLunas: stats.belumLunas,
                lunasCount: stats.lunas.length,
                belumLunasCount: stats.belumLunas.length,
                total: stats.total
            }))
            .sort((a, b) => b.total - a.total)
            .slice(0, 6); // Take top 6 students

        this.state.chartData = {
            labels: processedData.map(student => student.name),
            series: [
                {
                    name: 'Lunas',
                    data: processedData.map(student => student.lunasCount)
                },
                {
                    name: 'Belum Lunas',
                    data: processedData.map(student => student.belumLunasCount)
                }
            ],
            fullData: processedData  // Store complete data for click handling
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
                }
            },
            colors: ['#00E396', '#FF4560'],
            dataLabels: {
                enabled: true,
                formatter: function (val) {
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
                    formatter: function (value) {
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
                    formatter: function (value) {
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
                data: series.data.map(value => value || 0) // Ensure no undefined values
            }))
        };

        try {
            this.chartInstance = new ApexCharts(this.chartRef.el, config);
            this.chartInstance.render();
        } catch (error) {
            console.error('Error rendering chart:', error);
        }
    }

    async onChartClick(event, chartContext, config) {
        const dataPointIndex = config.dataPointIndex;
        const seriesIndex = config.seriesIndex;

        if (dataPointIndex === -1) return;

        let actionConfig = {
            type: 'ir.actions.act_window',
            view_mode: 'list,form',
            target: 'current',
            views: [[false, 'list'], [false, 'form']],
            context: {},
        };

        switch (this.props.title) {
            case 'Tagihan Siswa': {
                const studentData = this.state.chartData.fullData[dataPointIndex];
                const seriesName = this.state.chartData.series[seriesIndex].name;

                actionConfig.res_model = 'account.move.line';
                actionConfig.name = `${this.props.title} - ${studentData.name} - ${seriesName}`;

                // Get the relevant invoice lines based on series clicked
                const relevantLines = seriesName === 'Lunas'
                    ? studentData.lunas
                    : studentData.belumLunas;

                // Extract move_ids and line_ids
                const moveIds = [...new Set(relevantLines.map(line => line.move_id))];
                const lineIds = relevantLines.map(line => line.line_id);

                // Build domain with the specific line IDs and move IDs
                const domain = [
                    ['id', 'in', lineIds],
                    ['move_id', 'in', moveIds],
                    ['display_type', 'in', ['product']],
                    ['product_id', '!=', false],
                    ['move_id.partner_id', '=', parseInt(studentData.id)]
                ];

                // Add date filters if they exist
                if (this.state.isFiltered) {
                    if (this.state.currentStartDate) {
                        domain.push(['move_id.invoice_date', '>=', this.state.currentStartDate]);
                    }
                    if (this.state.currentEndDate) {
                        domain.push(['move_id.invoice_date', '<=', this.state.currentEndDate]);
                    }
                }

                // Add state filter based on series
                if (seriesName === 'Lunas') {
                    domain.push(['parent_state', '=', 'posted']);
                } else {
                    domain.push(['parent_state', '!=', 'posted']);
                }

                actionConfig.domain = domain;
                break;
            }

            case 'Uang Masuk':
            case 'Uang Keluar': {
                const selectedDate = this.state.chartData.labels[dataPointIndex];
                const [day, month, year] = selectedDate.split('/');

                // Create start and end date for the selected day
                const startDate = new Date(year, month - 1, day);
                startDate.setHours(0, 0, 0, 0);
                const endDate = new Date(year, month - 1, day);
                endDate.setHours(23, 59, 59, 999);

                actionConfig.res_model = 'cdn.uang_saku';
                actionConfig.name = `${this.props.title} - ${selectedDate}`;

                const formattedStartDate = startDate.toISOString().split('.')[0] + 'Z';
                const formattedEndDate = endDate.toISOString().split('.')[0] + 'Z';

                const domain = [
                    ['create_date', '>=', formattedStartDate],
                    ['create_date', '<=', formattedEndDate],
                    ["orangtua_id", "ilike", session.partner_display_name]
                ];

                // Add specific amount filter based on chart type
                if (this.props.title === 'Uang Saku Masuk') {
                    domain.push(['amount_in', '>', 0]);
                } else {
                    domain.push(['amount_out', '>', 0]);
                }

                actionConfig.domain = domain;
                break;
            }
        }

        await this.actionService.doAction(actionConfig);
    }
}

OrangtuaChartRenderer.template = 'owl.OrangtuaChartRenderer';