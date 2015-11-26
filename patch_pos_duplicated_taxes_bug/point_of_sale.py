# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Alex Duan <alex.duan@elico-corp.com>
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
from openerp.osv import orm, fields


class pos_order_line(orm.Model):
    _inherit = 'pos.order.line'

    def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
        return super(pos_order_line, self)._amount_line_all(
            cr, uid, ids, field_names, arg, context=context)

    _columns = {
        'price_subtotal': fields.function(
            _amount_line_all,
            multi='pos_order_line_amount',
            string='Subtotal w/o Tax'),
        'price_subtotal_incl': fields.function(
            _amount_line_all,
            multi='pos_order_line_amount',
            string='Subtotal'),
    }
