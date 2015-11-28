# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#     Jon Chow <jon.chow@elico-corp.com>
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
import openerp.netsvc as netsvc
from openerp import SUPERUSER_ID

class sale_order(orm.Model):
    _inherit = 'sale.order'
    def check_invoice_picking_done(self, cr, uid, ids, context=None):
        """
        if all invoice_picking done, return True.
        """
        assert len(ids) == 1
        so = self.browse(cr, SUPERUSER_ID, ids[0], context=context)
        for pick in so.picking_ids:
            if pick.invoice_state != 'none' and pick.state != 'done':
                return False
        return True
    
class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    def action_done(self, cr, uid, ids, context=None):
        """
        when picking done,try to make the relation SO done
        """
        res = super(stock_picking, self).action_done(cr, SUPERUSER_ID, ids, context=context)
        wf_service = netsvc.LocalService('workflow')
        for picking in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if (picking.sale_id
                and picking.sale_id.order_policy=='picking'):
                wf_service.trg_validate(SUPERUSER_ID, 'sale.order', picking.sale_id.id, None, cr)
        return res


class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    def _prepare_chained_picking(self, cr, uid, picking_name, picking, picking_type, moves_todo, context=None):
        '''
        if chain picking type is out, set this chain picking invoice_state to  '2binvoiced'
        and cancel all before picking invoice_state to 'none'
        '''
        
        picking_pool = self.pool.get('stock.picking')
        res = super(stock_move, self)._prepare_chained_picking(cr, uid, picking_name, picking, picking_type, moves_todo, context=context)
        
        if res.get('type', '') == 'out':
            res.update({'invoice_state':'2binvoiced', })
            picking_2 = picking_pool.browse(cr, SUPERUSER_ID, picking.id, context=None)
            if picking_2.sale_id and picking_2.sale_id.picking_ids:
                for p in picking_2.sale_id.picking_ids:
                    if p.invoice_state == '2binvoiced':
                        picking_pool.write(cr, uid, p.id, {'invoice_state':'none', }) 
            
        return res

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
  
  
