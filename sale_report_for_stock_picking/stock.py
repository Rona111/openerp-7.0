# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Jon Chow <jon.chow@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _


class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    _columns = {
    }
    _defaults = {
    }

    def print_sale_report(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order of stock picking
        '''
        assert len(ids) == 1, 'This option should only be used for\
         a single id at a time'
        sale_pool = self.pool.get('sale.order')

        picking = self.read(cr, uid, ids[0], ['origin'], context=context)
        sale_ids = sale_pool.search(cr, uid,
                                    [('name', '=', picking['origin'])],
                                    context=context)
        if len(sale_ids) != 1:
            raise osv.except_osv(_('No Sale Report'),
                                 _("There should be one sale order\
                                  linked to this picking."))
        # check by line before
        # assert len(sale_ids) == 1,
        # 'There should be one sale order linked to this picking.'
        datas = {'model': 'sale.order',
                 'ids': sale_ids,
                 'form': sale_pool.read(cr, uid, sale_ids[0], context=context),
                 }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'sale.order.without.discount',
                'datas': datas, 'nodestroy': True}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
