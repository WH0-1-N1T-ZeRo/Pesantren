/** @odoo-module **/
const { Component, onWillStart, onMounted, onWillUpdateProps, onWillUnmount } = owl;
import { useService } from "@web/core/utils/hooks";

export class KpiCard extends Component {
    setup() {
        this.orm = useService('orm');
        this.actionService = useService('action');

        this.state = {
            kpiData: [],
            animations: {},
            currentStartDate: this.props.startDate,
            currentEndDate: this.props.endDate,
            isFiltered: false
        };

        // Countdown related properties
        this.countdownInterval = null;
        this.countdownTime = 10;
        this.isCountingDown = false;

        // Set default dates if not provided
        const today = new Date();
        const firstDayOfYear = new Date(today.getFullYear(), 0, 1);
        
        this.defaultStartDate = firstDayOfYear.toISOString().split('T')[0];
        this.defaultEndDate = today.toISOString().split('T')[0];

        if (this.props.startDate && this.props.endDate) {
            this.state.isFiltered = true;
        }

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.startDate !== this.props.startDate || 
                nextProps.endDate !== this.props.endDate) {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                this.state.isFiltered = !!(nextProps.startDate && nextProps.endDate);
                await this.fetchData(this.state.currentStartDate, this.state.currentEndDate);
            }
        });

        onMounted(() => {
            // Attach event listener to the main dashboard timer button
            const timerButton = document.getElementById("timerButton");
            if (timerButton) {
                timerButton.addEventListener("click", () => this.handleTimerClick());
            }
            this.startKpiAnimations();
        });

        onWillStart(async () => {
            try {
                await this.checkModelAccess();
                await this.fetchData(
                    this.state.currentStartDate || this.defaultStartDate,
                    this.state.currentEndDate || this.defaultEndDate
                );
            } catch (error) {
                console.error("Failed to fetch KPI data:", error);
            }
        });

        onWillUnmount(() => {
            this.cleanup();
            // Remove event listener when component unmounts
            const timerButton = document.getElementById("timerButton");
            if (timerButton) {
                timerButton.removeEventListener("click", () => this.handleTimerClick());
            }
        });
    }

    async checkModelAccess() {
        try {
            const models = ['cdn.siswa', 'cdn.orangtua', 'hr.employee'];
            for (const model of models) {
                const access = await this.orm.call(
                    'ir.model.access',
                    'check',
                    [model, 'read'],
                    { context: this.env.context }
                );
            }
        } catch (error) {
            console.error('Error checking model access:', error);
        }
    }

    handleTimerClick() {
        if (this.isCountingDown) {
            this.stopCountdown();
        } else {
            this.startCountdown();
        }
        this.isCountingDown = !this.isCountingDown;
    }

    startCountdown() {
        this.countdownTime = 10;
        this.updateTimerUI();
        this.countdownInterval = setInterval(() => {
            this.countdownTime--;
            if (this.countdownTime < 0) {
                this.countdownTime = 10;
                this.refreshData();
            }
            this.updateTimerUI();
        }, 1000);
    }

    stopCountdown() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
        this.updateTimerUI(true);
    }

    updateTimerUI(stopped = false) {
        const timerIcon = document.getElementById("timerIcon");
        const timerCountdown = document.getElementById("timerCountdown");
        
        if (timerIcon) {
            timerIcon.className = stopped ? "fas fa-stopwatch" : "fas fa-stop d-none";
        }
        if (timerCountdown) {
            timerCountdown.textContent = stopped ? "" : this.countdownTime;
        }
    }

    cleanup() {
        this.stopCountdown();
        Object.values(this.state.animations).forEach(animationId => {
            cancelAnimationFrame(animationId);
        });
        this.state.animations = {};
    }

    // New method to start KPI animations
    startKpiAnimations() {
        this.state.kpiData.forEach((kpi, index) => {
            const countElement = document.getElementById(`counter-${index}`);
            if (countElement) {
                this.animateNumber(countElement, 0, kpi.value);
            }
        });
    }

    animateNumber(element, start, end, duration = 500) {
        if (!element) return;
        
        const range = end - start;
        const minFrame = 16;
        const steps = Math.max(Math.floor(duration / minFrame), 1);
        const increment = range / steps;
        let current = start;
        let step = 0;

        // Clear any existing animation
        const animationKey = element.id;
        if (this.state.animations[animationKey]) {
            cancelAnimationFrame(this.state.animations[animationKey]);
        }

        const animate = () => {
            step++;
            current += increment;
            
            if (step <= steps) {
                element.textContent = Math.round(current).toLocaleString();
                this.state.animations[animationKey] = requestAnimationFrame(animate);
            } else {
                element.textContent = Math.round(end).toLocaleString();
                delete this.state.animations[animationKey];
            }
        };

        this.state.animations[animationKey] = requestAnimationFrame(animate);
    }

    async fetchData(startDate, endDate) {
        try {
            // Ensure dates are defined
            startDate = startDate || this.defaultStartDate;
            endDate = endDate || this.defaultEndDate;
    
            // Create date domain filter
            const dateDomain = [
                ['create_date', '>=', startDate],
                ['create_date', '<=', endDate]
            ];
    
            // Wrap each ORM call in try-catch to handle individual model access errors
            let siswaData = [], orangtuaData = [], employeeData = [];
    
            try {
                siswaData = await this.orm.call(
                    'cdn.siswa', 
                    'search_read', 
                    [[...dateDomain], ['id', 'complete_name', 'jns_kelamin', 'last_tahfidz', 'pelanggaran_count', 'tahfidz_quran_count', 'create_date']],
                    { context: this.env.context }
                );
            } catch (error) {
                console.warn('Error fetching siswa data:', error);
            }
    
            try {
                orangtuaData = await this.orm.call(
                    'cdn.orangtua', 
                    'search_read', 
                    [[...dateDomain], ['id', 'complete_name', 'create_date']],
                    { context: this.env.context }
                );
            } catch (error) {
                console.warn('Error fetching orangtua data:', error);
            }
    
            try {
                employeeData = await this.orm.call(
                    'hr.employee', 
                    'search_read', 
                    [[...dateDomain], ['id', 'jns_pegawai', 'create_date']],
                    { context: this.env.context }
                );
            } catch (error) {
                console.warn('Error fetching employee data:', error);
            }
    
            // Calculate totals (with null checks)
            const totalSiswa = siswaData?.length || 0;
            const totalOrangtua = orangtuaData?.length || 0;
            const musyrifCount = employeeData?.filter(employee => employee.jns_pegawai === 'musyrif')?.length || 0;
            const guruQuranCount = employeeData?.filter(employee => employee.jns_pegawai === 'guruquran')?.length || 0;
    
            // Update state with new data
            this.state.kpiData = [
                {
                    name: 'Santri',
                    value: totalSiswa,
                    icon: 'fa-user-graduate',
                    color: '#00e396',
                    res_model: 'cdn.siswa',
                    domain: [...dateDomain],
                },
                {
                    name: 'Orangtua',
                    value: totalOrangtua,
                    icon: 'fa-users',
                    color: '#00e396',
                    res_model: 'cdn.orangtua',
                    domain: [...dateDomain],
                },
                {
                    name: 'Musyrif',
                    value: musyrifCount,
                    icon: 'fa-user-tie',
                    color: '#00e396',
                    res_model: 'hr.employee',
                    domain: [...dateDomain, ['jns_pegawai', '=', 'musyrif']],
                },
                {
                    name: 'Guru Quran',
                    value: guruQuranCount,
                    icon: 'fa-book',
                    color: '#00e396',
                    res_model: 'hr.employee',
                    domain: [...dateDomain, ['jns_pegawai', '=', 'guruquran']],
                },
            ];
    
            // Start animations for new values only if there's data
            if (this.state.kpiData.some(kpi => kpi.value > 0)) {
                this.startKpiAnimations();
            }
                
        } catch (error) {
            console.error('Error in fetchData:', error);
            // Optionally show a notification to the user
            this.env.services.notification.notify({
                title: 'Error',
                message: 'Failed to fetch KPI data. Please check your permissions or try again later.',
                type: 'danger',
            });
        }
    }

    async refreshData() {
        const startDate = this.state.isFiltered ? this.state.currentStartDate : this.defaultStartDate;
        const endDate = this.state.isFiltered ? this.state.currentEndDate : this.defaultEndDate;
        await this.fetchData(startDate, endDate);
    }

    attachEventListeners() {
        // Attach existing listeners
        const kpiCards = document.querySelectorAll('.kpi-card');
        kpiCards.forEach(card => {
            card.addEventListener('click', (evt) => {
                this.handleKpiCardClick(evt);
            });
        });

        // Add timer button listener
        const timerButton = document.getElementById("kpiTimerButton");
        if (timerButton) {
            timerButton.addEventListener("click", this.toggleCountdown.bind(this));
        }
    }

    handleKpiCardClick(evt) {
        const cardName = evt.currentTarget.dataset.name;
        const cardData = this.state.kpiData.find(kpi => kpi.name === cardName);

        if (cardData) {
            const { res_model, domain } = cardData;

            this.actionService.doAction({
                name: `${cardName}`,
                type: 'ir.actions.act_window',
                res_model: res_model,
                view_mode: 'list,form',
                views: [[false, 'list'], [false, 'form']],
                target: 'current',
                domain: domain,
            });
        }
    }
}

KpiCard.template = "owl.KpiCard";

KpiCard.props = {
    startDate: { type: String, optional: true },
    endDate: { type: String, optional: true },
};