/** @odoo-module **/
import { Component, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PelanggaranCardList extends Component {
    static props = {
        startDate: { type: String, optional: true },
        endDate: { type: String, optional: true }
    };

    setup() {
        this.orm = useService('orm');
        this.state = {
            pelanggarans: [],
            isLoading: true,
            hasData: false,
            currentStartDate: this.props.startDate,
            currentEndDate: this.props.endDate,
            sevenDayData: [] // Store rolling 7-day data separately
        };

        onWillStart(async () => {
            await this.fetchPelanggaranSantri();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.startDate !== this.props.startDate || 
                nextProps.endDate !== this.props.endDate) {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                await this.fetchPelanggaranSantri();
            }
        });
    }

    async fetchPelanggaranSantri() {
        try {
            this.state.isLoading = true;

            // Get data for the last 7 days
            const sevenDaysAgo = new Date();
            sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
            const sevenDaysAgoDB = sevenDaysAgo.toISOString().split('T')[0];

            // Base domain for 7-day data
            const sevenDayDomain = [
                ['state', '=', 'approved'],
                ['poin', '>', 0],
                ['tgl_pelanggaran', '>=', sevenDaysAgoDB]
            ];

            // Fetch 7-day data
            const sevenDayPelanggaran = await this.orm.searchRead(
                'cdn.pelanggaran',
                sevenDayDomain,
                [
                    'siswa_id',
                    'pelanggaran_id',
                    'kategori',
                    'poin',
                    'tgl_pelanggaran',
                    'kelas_id',
                    'deskripsi'
                ],
                { 
                    order: 'create_date DESC, poin DESC'
                }
            );

            // Store 7-day data
            this.state.sevenDayData = sevenDayPelanggaran;

            // Now handle filtered data if dates are provided
            let filteredData = [...this.state.sevenDayData]; // Start with 7-day data

            if (this.state.currentStartDate || this.state.currentEndDate) {
                // Additional domain for date filters
                const filterDomain = [
                    ['state', '=', 'approved'],
                    ['poin', '>', 0]
                ];

                if (this.state.currentStartDate) {
                    filterDomain.push(['tgl_pelanggaran', '>=', this.state.currentStartDate]);
                }
                if (this.state.currentEndDate) {
                    filterDomain.push(['tgl_pelanggaran', '<=', this.state.currentEndDate]);
                }

                const filteredPelanggaran = await this.orm.searchRead(
                    'cdn.pelanggaran',
                    filterDomain,
                    [
                        'siswa_id',
                        'pelanggaran_id',
                        'kategori',
                        'poin',
                        'tgl_pelanggaran',
                        'kelas_id',
                        'deskripsi'
                    ],
                    { 
                        order: 'create_date DESC, poin DESC'
                    }
                );

                // Merge filtered data with 7-day data
                const allIds = new Set();
                filteredData = [...filteredData, ...filteredPelanggaran].filter(item => {
                    if (!allIds.has(item.id)) {
                        allIds.add(item.id);
                        return true;
                    }
                    return false;
                });
            }

            if (!filteredData || filteredData.length === 0) {
                this.state.hasData = false;
                this.state.pelanggarans = [];
                return;
            }

            const studentIds = [...new Set(filteredData.map(p => p.siswa_id[0]))];
            const students = await this.orm.searchRead(
                'cdn.siswa',
                [['id', 'in', studentIds]],
                ['id', 'name', 'ruang_kelas_id']
            );
           
            const studentMap = new Map(students.map(s => [s.id, s]));

            this.state.pelanggarans = filteredData
                .map(p => ({
                    student_name: studentMap.get(p.siswa_id[0])?.name || "N/A",
                    pelanggaran_name: p.pelanggaran_id[1] || "N/A",
                    kategori: p.kategori || "N/A",
                    points: p.poin || 0,
                    tanggal: this.formatDate(p.tgl_pelanggaran),
                    kelas: p.kelas_id ? p.kelas_id[1] : "N/A",
                    deskripsi: p.deskripsi || ""
                }))
                .sort((a, b) => new Date(b.tanggal) - new Date(a.tanggal));

            this.state.hasData = this.state.pelanggarans.length > 0;

        } catch (error) {
            console.error("Error fetching pelanggaran data:", error);
            this.state.pelanggarans = [];
            this.state.hasData = false;
        } finally {
            this.state.isLoading = false;
        }
    }

    formatDate(dateStr) {
        if (!dateStr) return "N/A";
        const date = new Date(dateStr);
        return date.toLocaleDateString('id-ID', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
}

PelanggaranCardList.template = 'owl.PelanggaranCardList';

export class TahfidzCardList extends Component {
    static props = {
        startDate: { type: String, optional: true },
        endDate: { type: String, optional: true }
    };

    setup() {
        this.orm = useService('orm');
        this.state = {
            topTahfidz: [],
            isLoading: true,
            hasData: false,
            currentStartDate: this.props.startDate,
            currentEndDate: this.props.endDate,
            sevenDayData: [] // Store rolling 7-day data separately
        };

        onWillStart(async () => {
            await this.fetchTahfidzTertinggi();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.startDate !== this.props.startDate || 
                nextProps.endDate !== this.props.endDate) {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                await this.fetchTahfidzTertinggi();
            }
        });
    }

    async fetchTahfidzTertinggi() {
        try {
            this.state.isLoading = true;
    
            // Get data for the last 7 days
            const sevenDaysAgo = new Date();
            sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
            const sevenDaysAgoDB = sevenDaysAgo.toISOString().split('T')[0];
    
            // Base domain for 7-day data with non-zero jml_baris
            const sevenDayDomain = [
                ['state', '=', 'done'],
                ['siswa_id', '!=', false],
                ['tanggal', '>=', sevenDaysAgoDB],
                ['jml_baris', '>', 0]
            ];
    
            // Fetch 7-day data
            const sevenDayTahfidz = await this.orm.searchRead(
                'cdn.tahfidz_quran',
                sevenDayDomain,
                [
                    'siswa_id',
                    'halaqoh_id',
                    'jml_baris',
                    'state',
                    'tanggal'
                ],
                { order: 'jml_baris desc' }
            );
    
            // Store 7-day data
            this.state.sevenDayData = sevenDayTahfidz;
    
            // Handle filtered data if dates are provided
            let filteredData = [...this.state.sevenDayData];
    
            if (this.state.currentStartDate || this.state.currentEndDate) {
                const filterDomain = [
                    ['state', '=', 'done'],
                    ['siswa_id', '!=', false],
                    ['jml_baris', '>', 0]
                ];
    
                if (this.state.currentStartDate) {
                    filterDomain.push(['tanggal', '>=', this.state.currentStartDate]);
                }
                if (this.state.currentEndDate) {
                    filterDomain.push(['tanggal', '<=', this.state.currentEndDate]);
                }
    
                const filteredTahfidz = await this.orm.searchRead(
                    'cdn.tahfidz_quran',
                    filterDomain,
                    [
                        'siswa_id',
                        'halaqoh_id',
                        'jml_baris',
                        'state',
                        'tanggal'
                    ],
                    { order: 'jml_baris desc' }
                );
    
                // Merge filtered data with 7-day data
                const allIds = new Set();
                filteredData = [...filteredData, ...filteredTahfidz].filter(item => {
                    if (!allIds.has(item.id)) {
                        allIds.add(item.id);
                        return true;
                    }
                    return false;
                });
            }
    
            if (!filteredData || filteredData.length === 0) {
                this.state.hasData = false;
                this.state.topTahfidz = [];
                return;
            }
    
            // Group by student name and get their highest jml_baris
            const studentTahfidz = {};
            filteredData.forEach(record => {
                if (record.jml_baris > 0) {
                    const studentName = record.siswa_id[1];
                    if (!studentTahfidz[studentName] || studentTahfidz[studentName].jml_baris < record.jml_baris) {
                        studentTahfidz[studentName] = {
                            student_name: studentName,
                            jml_baris: record.jml_baris,
                            kelas: record.halaqoh_id ? record.halaqoh_id[1] : "N/A"
                        };
                    }
                }
            });
    
            // Convert to array, sort by jml_baris, and apply sequential numbering
            let sortedData = Object.entries(studentTahfidz)
                .map(([name, data]) => ({
                    name: name,
                    total_baris: data.jml_baris,
                    kelas: data.kelas
                }))
                .sort((a, b) => b.total_baris - a.total_baris)
                .slice(0, 5);
    
            // Apply sequential numbering after sorting
            this.state.topTahfidz = sortedData.map((item, index) => ({
                number: index + 1,  // Sequential numbering starting from 1
                ...item
            }));
    
            this.state.hasData = this.state.topTahfidz.length > 0;
    
        } catch (error) {
            console.error("Error fetching tahfidz data:", error);
            this.state.topTahfidz = [];
            this.state.hasData = false;
        } finally {
            this.state.isLoading = false;
        }
    }
}

TahfidzCardList.template = 'owl.TahfidzCardList';