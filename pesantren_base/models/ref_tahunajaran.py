#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

class ref_tahunajaran(models.Model):

    _name               = "cdn.ref_tahunajaran"
    _description        = "Tabel Referensi Tahun Pelajaran"
    name                = fields.Char( required=True, string="Tahun Ajaran",  help="")
    start_date          = fields.Date('Start Date', required=True)
    end_date            = fields.Date('End Date', required=True)
    term_structure      = fields.Selection([('two_sem', 'Dua Semester'),
                                    ('two_sem_qua', 'Dua Semester - Tiap semester dibagi 2 (Total 4 Quarter)'),
                                    ('two_sem_final', 'Dua Semester - Tiap semester dibagi 2 (Total 4 Quarter) + UAS'),
                                    ('others', 'Lainnya - Custom Termin Akademik')],
                                    string ='Pembagian Termin', default='two_sem',
                                    required=True)
    create_boolean      = fields.Boolean()
    # interval            = fields.Integer(string='Interval')
    
    term_akademik_ids   = fields.One2many(comodel_name='cdn.termin_akademik', inverse_name='tahunajaran_id', string='Termin Akademik')
    periode_tagihan_ids = fields.One2many(comodel_name='cdn.periode_tagihan', inverse_name='tahunajaran_id', string='Periode Tagihan')
    

    company_id          = fields.Many2one('res.company', string='Instansi', default=lambda self: self.env.user.company_id)
    keterangan          = fields.Char( string="Keterangan",  help="")
    biaya_ids           = fields.One2many(comodel_name="cdn.biaya_tahunajaran",  inverse_name="tahunajaran_id",  string="Biaya",  help="")

    _sql_constraints    = [('tahun_ajaran_uniq', 'unique(name)', 'Nama Tahun Ajaran tersebut sudah terdaftar, Pastikan harus unik !')]

    def term_create(self):
        num = 0
        final = 1
        academic_terms = self.env['cdn.termin_akademik'].search([])
        periode_tagihan = self.env['cdn.periode_tagihan'].search([])

        self.create_boolean = True
        self.create_periode_tagihan()

        if self.term_structure == 'two_sem':
            for record in self:
                if not record.term_akademik_ids:
                    from_d  = self.start_date
                    to_d    = self.end_date
                    delta   = to_d - from_d
                    res     = []
                    day     = (delta.days + 1) / 2
                    vals = {'name': 'Semester 1',
                            'from_date': from_d,
                            'to_date': (from_d + timedelta(days=day))}
                    res.append(vals)
                    vals = {'name': 'Semester 2',
                            'from_date': (from_d + timedelta(days=day + 1)),
                            'to_date': to_d}
                    res.append(vals)
                    for term in res:
                        academic_terms.create({
                            'name'              : term['name'],
                            'term_start_date'   : term['from_date'],
                            'term_end_date'     : term['to_date'],
                            'tahunajaran_id'    : self.id
                        })
        elif self.term_structure == 'two_sem_qua':
            for record in self:
                if not record.term_akademik_ids:
                    from_d  = self.start_date
                    to_d    = self.end_date
                    delta   = to_d - from_d
                    res     = []
                    day     = (delta.days + 1) / 2
                    vals = {'name': 'Semester 1',
                            'from_date': from_d,
                            'to_date': (from_d + timedelta(days=day))}
                    res.append(vals)
                    vals = {'name': 'Semester 2',
                            'from_date': (from_d + timedelta(days=day + 1)),
                            'to_date': to_d}
                    res.append(vals)
                    for term in res:
                        academic_terms.create({
                            'name'              : term['name'],
                            'term_start_date'   : term['from_date'],
                            'term_end_date'     : term['to_date'],
                            'tahunajaran_id'    : self.id
                        })
                        for sub_term in self.term_akademik_ids:
                            sub_from_d  = sub_term.term_start_date
                            sub_to_d    = sub_term.term_end_date
                            delta       = sub_to_d - sub_from_d
                            result      = []
                            day         = (delta.days + 1) / 2
                            vals        = {'name': 'Quarter' + ' ' + str(num+1),
                                    'from_date': sub_from_d,
                                    'to_date': (sub_from_d + timedelta(days=day))}
                            result.append(vals)
                            vals        = {'name': 'Quarter' + ' ' + str(num+2),
                                    'from_date': (sub_from_d + timedelta(days=day + 1)),
                                    'to_date': sub_to_d}
                            result.append(vals)
                        num = num + 2

                        for in_terms in result:
                            academic_terms.create({
                                'name'              : in_terms['name'],
                                'term_start_date'   : in_terms['from_date'],
                                'term_end_date'     : in_terms['to_date'],
                                'tahunajaran_id'    : self.id,
                                'parent_term'       : sub_term.id
                            })

        elif self.term_structure == 'two_sem_final':
            for record in self:
                if not record.term_akademik_ids:
                    from_d      = self.start_date
                    to_d        = self.end_date
                    delta       = to_d - from_d
                    res         = []
                    day     = (delta.days + 1) / 2
                    vals    = {'name'   : 'Semester 1',
                            'from_date' : from_d,
                            'to_date'   : (from_d + timedelta(days=day))}
                    res.append(vals)
                    vals    = {'name'   : 'Semester 2',
                            'from_date' : (from_d + timedelta(days=day + 1)),
                            'to_date'   : to_d}
                    res.append(vals)

                    for term in res:
                        academic_terms.create({
                            'name'              : term['name'],
                            'term_start_date'   : term['from_date'],
                            'term_end_date'     : term['to_date'],
                            'tahunajaran_id'    : self.id
                        })

                        for sub_term in self.term_akademik_ids:
                            sub_from_d  = sub_term.term_start_date
                            sub_to_d    = sub_term.term_end_date
                            delta       = sub_to_d - sub_from_d
                            result      = []

                            day     = (delta.days + 1) / 2
                            vals    = {'name'   : 'Quarter' + ' ' + str(num+1),
                                    'from_date' : sub_from_d,
                                    'to_date'   : (sub_from_d + timedelta(days=day))}

                            result.append(vals)

                            vals    = {'name'   : 'Quarter' + ' ' + str(num + 2),
                                    'from_date' : (sub_from_d + timedelta(days=day + 1)),
                                    'to_date'   : (sub_from_d + timedelta(days=delta.days - 1))}

                            result.append(vals)

                            vals    = {'name'   : 'Ujian Akhir' + ' ' + str(final),
                                    'from_date' : sub_to_d,
                                    'to_date'   : sub_to_d}
                            result.append(vals)

                        num = num + 2
                        final = final + 1

                        for in_terms in result:
                            academic_terms.create({
                                'name'              : in_terms['name'],
                                'term_start_date'   : in_terms['from_date'],
                                'term_end_date'     : in_terms['to_date'],
                                'tahunajaran_id'    : self.id,
                                'parent_term'       : sub_term.id
                            })
    
    def create_periode_tagihan(self):
        self.ensure_one()
        period_obj = self.env['cdn.periode_tagihan']
        
        # Ubah data dari string
        ds = fields.Date.from_string(self.start_date) if isinstance(self.start_date, str) else self.start_date
        end_date = fields.Date.from_string(self.end_date) if isinstance(self.end_date, str) else self.end_date

        # Ubah mjd tgl 20 untuk periode bayar
        start_period = ds.replace(day=20) - relativedelta(months=1)
        
        while start_period <= end_date:
            # Penghitungan batas bayar tagihan
            period_end = (start_period + relativedelta(months=1)).replace(day=19)

            if period_end > end_date:
                period_end = end_date

            #menentukan field 'name' berdasarkan periode mulai
            if start_period == ds.replace(day=20) - relativedelta(months=1):
                period_name = ds.strftime('%m/%Y')
            else:
                period_name = start_period.strftime('%m/%Y')

            period_obj.create({
                'name': period_name,
                'kode': period_name,
                'start_date': start_period.strftime('%Y-%m-%d'),
                'end_date': period_end.strftime('%Y-%m-%d'),
                'tahunajaran_id': self.id
            })

            # Berpindah ke bulan berikut
            start_period = start_period + relativedelta(months=1)

        return True



class termin_akademik(models.Model):
    _name               = 'cdn.termin_akademik'
    _description        = 'Pembagian Termin Akademik untuk Tahun Pelajaran'

    name                = fields.Char(string='Termin')
    term_start_date     = fields.Date('Tgl Awal', required=True)
    term_end_date       = fields.Date('Tgl Akhir', required=True)
    tahunajaran_id      = fields.Many2one('cdn.ref_tahunajaran', 'Tahun Akademik', required=True)
    parent_term         = fields.Many2one('cdn.termin_akademik', 'Termin induk')

    company_id          = fields.Many2one('res.company', string='Instansi', default=lambda self: self.env.user.company_id)

class periode_tagihan(models.Model):
    _name               = 'cdn.periode_tagihan'
    _description        = 'Periode Tagihan berdasarkan Tahun Akademik'

    name                = fields.Char(string='Periode Tagihan', required=True)
    kode                = fields.Char(string='Kode')
    start_date          = fields.Date('Tgl Awal', required=True)
    end_date            = fields.Date('Tgl Akhir', required=True)
    tahunajaran_id      = fields.Many2one('cdn.ref_tahunajaran', 'Tahun Akademik', required=True)

    def _check_batas_tahun(self):
        for period in self:
            if period.tahunajaran_id.end_date < period.end_date or \
               period.tahunajaran_id.end_date < period.start_date or \
               period.tahunajaran_id.start_date > period.start_date or \
               period.tahunajaran_id.start_date > period.end_date:
                return False
        return True
    
    def _check_duration(self):
        for period in self:
            if period.end_date < period.start_date:
                return False
        return True

    def name_get(self):
        res = []
        for field in self:
            # if self.env.context.get('custom_search', False):
            res.append((field.id,"{} TA: {}".format(field.name,field.tahunajaran_id.name)))
            # else:
                # res.append((field.id, field.name))
        return res


    _constraints = [(_check_duration, 'Error!\n Durasi tanggal awal dan tanggal akhirnya salah', ['end_date']),
        (_check_batas_tahun, 'Error!\n Tanggal Awal dan Akhir tidak sesuai dengan periode Tahun Ajaran', ['end_date']),
    ]

    
    

    
    