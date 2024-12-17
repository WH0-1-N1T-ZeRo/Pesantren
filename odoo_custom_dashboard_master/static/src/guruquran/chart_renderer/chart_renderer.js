  /** @odoo-module */
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const {
  Component,
  onWillStart,
  useRef,
  onMounted,
  onWillUnmount,
  onWillUpdateProps,
} = owl;
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session"; 

export class GuruquranChartRenderer extends Component {
  static props = {
    type: { type: String },
    period: { type: String, optional: true },
    startDate: { type: String, optional: true },
    endDate: { type: String, optional: true },
  };

  setup() {
    this.chartRef = useRef("chart");
    this.donutChartRef = useRef("donutChart");
    this.donutChart2Ref = useRef("donutChart2"); 
    this.loadingOverlayRef = useRef("loadingOverlay");
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.state = {
      chartData: { series: [], labels: [] },
      donutChartData: { series: [], labels: [] },
      donutChart2Data: { series: [], labels: [] }, // Add second donut chart data
      selectedPeriod: this.props.period || "all",
      currentStartDate: this.props.startDate,
      currentEndDate: this.props.endDate,
    };
    this.chartInstance = null;
    this.donutChartInstance = null;
    this.donutChart2Instance = null; // Add second donut chart instance
    this.countdownInterval = null;
    this.countdownTime = 10;
    this.isCountingDown = false;

    if (this.props.startDate && this.props.endDate) {
      this.state.isFiltered = true;
    }

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
        await this.fetchAttendanceData(
          this.state.currentStartDate,
          this.state.currentEndDate
        )
      ]);
    } catch (error) {
      console.error("Error updating props:", error);
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
      await this.fetchAttendanceData(
        this.state.currentStartDate,
        this.state.currentEndDate
      )
    ]);
  } catch (error) {
    console.error("Error in initial data fetch:", error);
  } finally {
    this.hideLoading();
  }
});

    onMounted(() => {
      this.renderDonutChart();
      this.renderDonutChart2(); // Add second donut chart rendering
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
    if (this.donutChartInstance) {
      this.donutChartInstance.destroy();
      this.donutChartInstance = null;
    }
    if (this.donutChart2Instance) { // Add second donut chart cleanup
      this.donutChart2Instance.destroy();
      this.donutChart2Instance = null;
    }
    this.clearIntervals();
  }


    setPeriod(period) {
      this.state.selectedPeriod = period;
      this.fetchAttendanceData();
    }

    toggleCountdown() {
      if (this.isCountingDown) {
        this.clearIntervals();
        document.getElementById("timerIcon").className = "fas fa-stopwatch";
        document.getElementById("timerCountdown").textContent = "";
      } else {
        this.startCountdown();
        document.getElementById("timerIcon").className = "fas fa-stop";
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
      const startDate = this.state.isFiltered
        ? this.state.currentStartDate
        : null;
      const endDate = this.state.isFiltered ? this.state.currentEndDate : null;
      try {
        await Promise.all([
          await this.fetchAttendanceData(startDate, endDate)
        ]);
    
      if (this.donutChartInstance) {
        this.donutChartInstance.updateOptions(
          {
            labels: this.state.donutChartData.labels,
            series: this.state.donutChartData.series,
          },
          true,
          true
        );
      }
    
      if (this.donutChart2Instance) {
        this.donutChart2Instance.updateOptions(
          {
            labels: this.state.donutChart2Data.labels,
            series: this.state.donutChart2Data.series,
          },
          true,
          true
        );
      }
    } catch (eror) {
      console.error("Error refreshing chart:", error);
    } finally {
      this.hideLoading();
    }
  }

    clearIntervals() {
      if (this.countdownInterval) clearInterval(this.countdownInterval);
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
        startDateInput.addEventListener("change", () => this.handleDateFilter());
        endDateInput.addEventListener("change", () => this.handleDateFilter());
      }
    }

    async handleDateFilter() {
      this.clearIntervals(); 
      this.showLoading();
  
      const startDateInput = document.querySelector('input[name="start_date"]');
      const endDateInput = document.querySelector('input[name="end_date"]');
  
      if (startDateInput && endDateInput) {
          const startDate = startDateInput.value;
          const endDate = endDateInput.value;
  
          if (startDate && endDate) {
              const formattedStartDate = this.formatDateToOdoo(startDate);
              const formattedEndDate = this.formatDateToOdoo(endDate);
  
              this.state.currentStartDate = formattedStartDate;
              this.state.currentEndDate = formattedEndDate;
              this.state.isFiltered = true;
            try {
              await Promise.all([
                await this.fetchAttendanceData(formattedStartDate, formattedEndDate)
            ]);
          } catch (error) {
            console.error("Error in date filter:", error);
          } finally {
            this.hideLoading();
          }
        }
      }
  
      if (this.isCountingDown) {
        this.startCountdown();
      }
    }
  

    formatDateToDisplay(date) {
      if (!date) return '';
      
      const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
        'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'
      ];
      
      const dateObj = typeof date === 'string' ? new Date(date) : date;
      
      const day = String(dateObj.getDate()).padStart(2, '0');
      const month = months[dateObj.getMonth()];
      const year = dateObj.getFullYear();
    
      return `${day} ${month} ${year}`;
    }

    formatDateToOdoo(dateString) {
      const date = new Date(dateString);
      return date.toISOString().split(".")[0] + "Z";
    }

    updateChart() {
      if (this.chartInstance) {
        this.chartInstance.updateOptions(
          {
            xaxis: {
              categories: this.state.chartData.labels,
            },
            series: this.state.chartData.series,
          },
          false,
          true
        );
      }

      if (this.donutChartInstance) {
        this.donutChartInstance.updateOptions({
          labels: this.state.donutChartData.labels,
          series: this.state.donutChartData.series,
        });
      }
    }

    async fetchAttendanceData(startDate = null, endDate = null) {
      if (!startDate && !endDate) {
        endDate = new Date();
        startDate = new Date();
        startDate.setDate(startDate.getDate() - 6);
    
        startDate = startDate.toISOString().split("T")[0];
        endDate = endDate.toISOString().split("T")[0];
      } else {
        startDate = new Date(startDate).toISOString().split("T")[0];
        endDate = new Date(endDate).toISOString().split("T")[0];
      }
    
      const domain = [
        ["tanggal", ">=", startDate],
        ["tanggal", "<=", endDate],
        ["penanggung_jawab_id","ilike",session.partner_display_name]
      ];
      
      try {
        // Fetch data for first donut chart (tahfidz)
        const tahfidzData = await this.orm.call(
          "cdn.absen_tahfidz_quran_line",
          "search_read",
          [domain, ["name", "halaqoh_id", "tanggal", "kehadiran", "penanggung_jawab_id"]]
        );
        
        // Fetch data for second donut chart (tahsin)
        const tahsinData = await this.orm.call(
          "cdn.absen_tahsin_quran_line",
          "search_read",
          [domain, ["name", "halaqoh_id", "tanggal", "kehadiran", "penanggung_jawab_id"]]
        );
  
        // Process tahfidz data for first donut chart
        const tahfidzStatus = {};
        tahfidzData.forEach((record) => {
          const status = record.kehadiran || 'Tidak Ada Status';
          tahfidzStatus[status] = (tahfidzStatus[status] || 0) + 1;
        });
  
        // Process tahsin data for second donut chart
        const tahsinStatus = {};
        tahsinData.forEach((record) => {
          const status = record.kehadiran || 'Tidak Ada Status';
          tahsinStatus[status] = (tahsinStatus[status] || 0) + 1;
        });
  
        // Update first donut chart data (tahfidz)
        this.state.donutChartData = {
          labels: Object.keys(tahfidzStatus),
          series: Object.values(tahfidzStatus),
        };
  
        // Update second donut chart data (tahsin)
        this.state.donutChart2Data = {
          labels: Object.keys(tahsinStatus),
          series: Object.values(tahsinStatus),
        };
  
        // Store the current view range in state for reference
        this.state.currentViewRange = {
          startDate,
          endDate,
        };
    
        // Render both charts after updating data
        this.renderDonutChart();
        this.renderDonutChart2();
    
      } catch (error) {
        console.error("Error fetching attendance data:", error);
        this.state.donutChartData = { series: [], labels: [] };
        this.state.donutChart2Data = { series: [], labels: [] };
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

      return !(
        currentStartDate.toISOString().split("T")[0] ===
          weekAgo.toISOString().split("T")[0] &&
        currentEndDate.toISOString().split("T")[0] ===
          today.toISOString().split("T")[0]
      );
    }

    getDonutChartConfig(title = '', isSecondChart = false) {
      return {
        chart: {
          type: 'pie',
          height: 355,
          toolbar: {
            show: false
          },
          animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 800,
            animateGradually: {
              enabled: true,
              delay: 150
            },
            dynamicAnimation: {
              enabled: true,
              speed: 350
            }
          },
          events: {
            dataPointSelection: (event, chartContext, config) =>
              this.onPieClick(event, chartContext, config, isSecondChart),
          },    
        },
        title: {
          text: title,
          align: 'center',
          style: {
            fontSize: '18px',
            fontWeight: '600',
            fontFamily: 'Inter, sans-serif',
          },
        },
        legend: {
          position: 'top',
          horizontalAlign: 'center',
        },
        dataLabels: {
          enabled: false,
        },
        colors: [
          "#16a34a", // green
          "#0891b2", // cyan
          "#22c55e", // emerald
          "#06b6d4", // light blue
          "#15803d", // dark green
          "#0e7490", // dark cyan
          "#86efac", // light green
          "#67e8f9", // light cyan
          "#166534", // forest green
          "#155e75", // ocean blue  
        ],
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 300
            },
            legend: {
              position: 'top'
            }
          }
        }],
        tooltip: {
          y: {
            formatter: function(value) {
              return value + ' orang';
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
    }

    renderDonutChart() {
      if (!this.donutChartRef.el) return;
    
      if (this.donutChartInstance) {
        this.donutChartInstance.destroy();
        this.donutChartInstance = null;
      }
    
      this.donutChartRef.el.innerHTML = "";
    
      const config = {
        ...this.getDonutChartConfig('', false), // Pass false for tahfidz chart
        labels: this.state.donutChartData.labels,
        series: this.state.donutChartData.series,
      };
    
      try {
        this.donutChartInstance = new ApexCharts(this.donutChartRef.el, config);
        this.donutChartInstance.render();
      } catch (error) {
        console.error("Error rendering tahfidz chart:", error);
      }
    }
    
    renderDonutChart2() {
      if (!this.donutChart2Ref.el) return;
    
      if (this.donutChart2Instance) {
        this.donutChart2Instance.destroy();
        this.donutChart2Instance = null;
      }
    
      this.donutChart2Ref.el.innerHTML = "";
    
      const config = {
        ...this.getDonutChartConfig('', true), // Pass true for tahsin chart
        labels: this.state.donutChart2Data.labels,
        series: this.state.donutChart2Data.series,
      };
    
      try {
        this.donutChart2Instance = new ApexCharts(this.donutChart2Ref.el, config);
        this.donutChart2Instance.render();
      } catch (error) {
        console.error("Error rendering tahsin chart:", error);
      }
    }
    
    // Finally, update the onPieClick method to handle each chart correctly
    onPieClick(event, chartContext, config, isSecondChart) {
      const dataPointIndex = config.dataPointIndex;
      if (dataPointIndex === -1) return;
    
      const selectedStatus = isSecondChart 
        ? this.state.donutChart2Data.labels[dataPointIndex]
        : this.state.donutChartData.labels[dataPointIndex];
      
      const domain = [
        ["kehadiran", "=", selectedStatus],
        ["penanggung_jawab_id", "ilike", session.partner_display_name]
      ];
    
      if (this.state.currentViewRange) {
        domain.push(
          ["tanggal", ">=", this.state.currentViewRange.startDate],
          ["tanggal", "<=", this.state.currentViewRange.endDate]
        );
      }
    
      const actionConfig = {
        type: "ir.actions.act_window",
        target: "current",
        name: `${isSecondChart ? 'Absen Tahsin' : 'Absen Tahfidz'} - ${selectedStatus}`,
        res_model: isSecondChart ? "cdn.absen_tahsin_quran_line" : "cdn.absen_tahfidz_quran_line",
        view_mode: "list,form",
        views: [
          [false, "list"],
          [false, "form"],
        ],
        domain: domain,
      };
    
      this.actionService.doAction(actionConfig);
    }
  }

GuruquranChartRenderer.template = "owl.GuruquranChartRenderer";
