from itertools import count
from odoo import api, fields, models
from datetime import date

class Mutabaah_harian(models.Model):
    _name = 'cdn.mutabaah_harian'
    _description = 'Mutabaah Harian'
    _order = 'tgl Desc'

    #get domain
   
    name        = fields.Char(string='No. Referensi', readonly=True)
    tgl         = fields.Date('Tgl Mutabaah', required=True, default=lambda self: date.today())
    sesi_id     = fields.Many2one(comodel_name='cdn.mutabaah.sesi', string='Sesi', required=True)
    siswa_id    = fields.Many2one('cdn.siswa', string='Siswa', required=True)
    halaqoh_id  = fields.Many2one('cdn.halaqoh', string='Halaqoh', readonly=True, related='siswa_id.halaqoh_id')
    
    mutabaah_lines = fields.One2many('cdn.mutabaah_line', 'mutabaah_harian_id', string='Check Aktivitas')

    total_skor = fields.Integer(string='Total Skor', compute='_compute_total_skor', store=True)
    total_skor_display = fields.Char(string='Skor Mutabaah', compute='_compute_total_skor_display')
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Done','Selesai'),
    ], default='Draft', string='Status')

    # total_skor_adab = fields.Integer(string='Aktivitas Adab', related='mutabaah_lines.total_skor_adab', store=True)
    # total_skor_kedisiplinan = fields.Integer(string='Aktivitas Kedisiplinan', related='mutabaah_lines.total_skor_kedisiplinan', store=True)
    # total_skor_ibadah = fields.Integer(string='Aktivitas ibadah', related='mutabaah_lines.total_skor_ibadah', store=True)
    # total_skor_kebersihan = fields.Integer(string='Aktivitas Kebersihan', related='mutabaah_lines.total_skor_kebersihan', store=True)
    
    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code("cdn.mutabaah_harian")
        return super(Mutabaah_harian, self).create(vals)
    
    #insert one2many
    # @api.onchange('siswa_id')
    # def onchange_siswa_id(self):
        
    
            
    @api.onchange('siswa_id','tgl','sesi_id')
    def onchange_siswa_id(self):
        self.ensure_one()
        if self.siswa_id:
            mutabaah_harian = self.env['cdn.mutabaah_harian'].search([
                ('siswa_id','=', self.siswa_id.id),
                ('tgl','=', self.tgl),
                ('sesi_id','=', self.sesi_id.id),
                ])
            
            # Jika sudah pernah diinput data mutabaah
            if mutabaah_harian:
                return {
                    'warning' : {
                        'title' : "Harap diperhatikan!",
                        'message' : "Santri yang sudah di catat tidak boleh di catat lagi dalam sehari"
                    },
                    'value' : {
                        'mutabaah_lines' : False,
                        'siswa_id' : False
                    }

                }
            # Jika Belum pernah diinput data mutabaah
            else:
                # Cek apakah data diinput jam sekarang melebih batas waktu sesi 
                jam_sekarang = fields.Datetime.now().hour in range(0,24)
                print(jam_sekarang)
                if int(jam_sekarang) > int(self.sesi_id.jam_selesai):
                    return {
                        'warning' : {
                            'title' : "Harap diperhatikan!",
                            'message' : "Waktu sesi mutabaah sudah berakhir"
                        },
                        'value' : {
                            'mutabaah_lines' : False,
                            'siswa_id' : False
                        }
                    }


                nilai = [(5,0,0)] 

                objek_mutabaah = self.env['cdn.mutabaah'].search([('sesi_id','=',self.sesi_id.id)], order = 'id asc')
                
                for ye in objek_mutabaah:
                    nilai.append(
                        (0, 0,{'name': ye.id, 'is_sudah':True, 'keterangan':'-'})
                    )
                return {'value' : {'mutabaah_lines' : nilai}}
            
    @api.depends('mutabaah_lines.is_sudah')
    def _compute_total_skor(self):
        for rec in self:
            rec.total_skor = sum(rec.mutabaah_lines.filtered('is_sudah').mapped('name.skor'))
            
    @api.depends('mutabaah_lines.is_sudah')
    def _compute_total_skor_display(self):
        for rec in self:
            total_records = len(rec.mutabaah_lines)
            completed_records = sum(1 for line in rec.mutabaah_lines if line.is_sudah)
            rec.total_skor_display = f"{completed_records} dari {total_records}"

    def btn_uncheckall(self):
        self.mutabaah_lines.is_sudah = False

    def btn_checkall(self):
        self.mutabaah_lines.is_sudah = True
    
    def action_confirm(self):
        self.state = 'Done'
        
    def action_draft(self):
        self.state = 'Draft'

class Mutabaah_line(models.Model):
    _name = 'cdn.mutabaah_line'
    _description = 'Mutabaah line'

    mutabaah_harian_id = fields.Many2one('cdn.mutabaah_harian', string='mutabaah_harian')
    skor = fields.Integer(string='Skor', related='name.skor')
    siswa_id = fields.Many2one('cdn.siswa', string='Siswa', related='mutabaah_harian_id.siswa_id', readonly=True, store=True)
    tgl = fields.Date('Tgl Mutabaah', related='mutabaah_harian_id.tgl', readonly=True, store=True)
    name = fields.Many2one('cdn.mutabaah', string='Aktivitas / Perbuatan')
    kategori_id = fields.Many2one(comodel_name='cdn.mutabaah.kategori', string='Kategori', related='name.kategori_id')
    
    is_sudah = fields.Boolean(string='Dilakukan', )
    keterangan = fields.Char(string='Keterangan')

    # total_skor_adab = fields.Integer(string='Aktivitas Adab', compute='_compute_total_skor', store=True)
    # total_skor_kedisiplinan = fields.Integer(string='Aktivitas Kedisiplinan', compute='_compute_total_skor', store=True)
    # total_skor_ibadah = fields.Integer(string='Aktivitas Ibadah', compute='_compute_total_skor', store=True)
    # total_skor_kebersihan = fields.Integer(string='Aktivitas Kebersihan', compute='_compute_total_skor', store=True)
    
    # @api.depends('siswa_id','is_sudah')
    # def _compute_total_skor(self):

        # for rec in self:

        #     adab = self.env['cdn.mutabaah'].search([
        #         ('kategori','=', 'adab'),
        #         ('is_tampil','=',True)]).mapped('skor')

        #     if rec.siswa_id:    
        #         rec.total_skor_adab = sum(adab)
        #     # elif rec.is_sudah == False:
        #     #     rec.total_skor_adab = sum(adab) - adab  

        #     disiplin = self.env['cdn.mutabaah'].search([
        #         ('kategori','=', 'disiplin'),
        #         ('is_tampil','=',True)]).mapped('skor')
            
        #     if rec.siswa_id:    
        #         rec.total_skor_kedisiplinan = sum(disiplin)

        #     ibadah = self.env['cdn.mutabaah'].search([
        #         ('kategori','=', 'ibadah'),
        #         ('is_tampil','=',True)]).mapped('skor')

        #     if rec.siswa_id:    
        #         rec.total_skor_ibadah = sum(ibadah)

        #     kebersihan = self.env['cdn.mutabaah'].search([
        #         ('kategori','=', 'kebersihan'),
        #         ('is_tampil','=',True)]).mapped('skor')

        #     if rec.siswa_id:    
        #         rec.total_skor_kebersihan = sum(kebersihan)

 
    
    


    

    