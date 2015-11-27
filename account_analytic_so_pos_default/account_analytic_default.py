# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _

class account_analytic_account(orm.Model):

    _inherit = 'account.analytic.account'
    _columns = {'so_available': fields.boolean('Available in SO')}

class account_analytic_default(orm.Model):
    _name = "account.analytic.default"
    _description = "Analytic Distribution"
    _rec_name = "analytic_id"
    _order = "sequence"
    _columns = {
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of analytic distribution"),
        'analytic_id': fields.many2one('account.analytic.account', 'Analytic Account', domain="[('so_available', '=', True)]"),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade', help="Select a product which will use analytic account specified in analytic default (e.g. create new customer invoice or Sales order if we select this product, it will automatically take this as an analytic account)"),
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='cascade', help="Select a partner which will use analytic account specified in analytic default (e.g. create new customer invoice or Sales order if we select this partner, it will automatically take this as an analytic account)"),
        'user_id': fields.many2one('res.users', 'User', ondelete='cascade', help="Select a user which will use analytic account specified in analytic default."),
        'company_id': fields.many2one('res.company', 'Company', ondelete='cascade', help="Select a company which will use analytic account specified in analytic default (e.g. create new customer invoice or Sales order if we select this company, it will automatically take this as an analytic account)"),
        'date_start': fields.date('Start Date', help="Default start date for this Analytic Account."),
        'date_stop': fields.date('End Date', help="Default end date for this Analytic Account."),
        'shop_id': fields.many2one('sale.shop', 'Shop', required = True, ondelete='cascade', help="Select a shop which will use analytic account specified in analytic default (e.g. create new customer invoice or Sales order if we select this product, it will automatically take this as an analytic account)"),
        'channel_id': fields.many2one('res.partner.category', 'Channel', required = True, ondelete='cascade', help="Select a channel which will use analytic account specified in analytic default (e.g. create new customer invoice or Sales order if we select this partner, it will automatically take this as an analytic account)"),
    }

    def account_get(self, cr, uid, shop_id=None, channel_id=None, context=None):
        domain = []
        if shop_id:
            domain += ['|',('shop_id', '=', shop_id)]
        domain += [('shop_id','=', False)]
        if channel_id:
            domain += ['|',('channel_id', '=', channel_id)]
        domain += [('channel_id','=', False)]
        best_index = -1
        res = False
        for rec in self.browse(cr, uid, self.search(cr, uid, domain, context=context), context=context):
            index = 0
            if rec.shop_id: index += 1
            if rec.channel_id: index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _get_account_analytic_invoice(self, cursor, user, picking, move_line):
        
        if picking and picking.sale_id:
            return picking.sale_id.project_id.id

        return super(stock_picking, self)._get_account_analytic_invoice(cursor, user, picking, move_line)

class sale_order(orm.Model):

    _inherit = "sale.order"

    _columns = {'project_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True, states={'draft': [('readonly', False)], 
                                              'sent': [('readonly', False)]}, domain="[('so_available', '=', True)]", help="The analytic account related to a sales order."),
                }
    def onchange_channel_id_2(self, cr, uid, ids, channel_id, shop_id, context=None):
        res = {'value': {'credit_limit_control': False}}
        if not channel_id:
            return res
        channel_obj = self.pool.get('res.partner.category')
        channel = channel_obj.browse(cr, uid, channel_id, context=context)
        res['value']['credit_limit_control'] = channel.credit_limit_control or False
        if shop_id and channel_id:
            anal_def_obj = self.pool.get('account.analytic.default')
            analytic_account = anal_def_obj.account_get(cr, uid, shop_id, channel_id, context=context)
            if analytic_account:
                res['value']['project_id'] = analytic_account.analytic_id.id or None
        return res

    def onchange_shop_id_2(self, cr, uid, ids, shop_id, channel_id, context=None):
        v = {}
        if shop_id:
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id, context=context)
            if shop.project_id.id:
                v['project_id'] = shop.project_id.id
            if shop.pricelist_id.id:
                v['pricelist_id'] = shop.pricelist_id.id
        res = {'value': v}
        if res.get('value',{}).get('project_id'):
            del(res['value']['project_id'])
        shop_obj = self.pool.get('sale.shop')
        res['value']['location_id'] = False
        res['value']['is_location'] = False
        if 'pricelist_id' in res['value']:
            res['value'].pop('pricelist_id')
        if shop_id:
            shop = shop_obj.browse(cr, uid, shop_id, context=context)
            res['value']['is_location'] = shop.is_location
            if shop.is_location:
                res['domain'] = {
                    'location_id': [
                        ('location_id', 'child_of', [l.id for l in shop.location_ids]),
                        ('usage', '<>', 'view')
                    ]
                }
        if shop_id and channel_id:
            anal_def_obj = self.pool.get('account.analytic.default')
            analytic_account = anal_def_obj.account_get(cr, uid, shop_id, channel_id, context=context)
            if analytic_account:
                res['value']['project_id'] = analytic_account.analytic_id.id or None
        return res
    def action_button_confirm(self, cr, uid, ids, context=None):
        sale_obj = self.browse(cr, uid, ids, context = context)
        for sale in sale_obj:
            if not sale.project_id:
                raise osv.except_osv(
                    _('Warning'),
                    _("Please set 'Analytic Account'"))
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
 
class sale_order_line(orm.Model):
    _inherit = "sale.order.line"


    def invoice_line_create(self, cr, uid, ids, context=None):
        create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context=context)
        if not ids:
            return create_ids
        sale_line = self.browse(cr, uid, ids[0], context=context)
        inv_line_obj = self.pool.get('account.invoice.line')

        for line in inv_line_obj.browse(cr, uid, create_ids, context=context):
            if sale_line.order_id.project_id:
                inv_line_obj.write(cr, uid, [line.id], {'account_analytic_id': sale_line.order_id.project_id.id}, context=context)
        return create_ids


class pos_order_line(orm.Model):
    _inherit = 'pos.order.line'

    def _get_analytic_account(self, cr, uid, ids, field_name, arg, context=None):
        anal_def_obj = self.pool.get('account.analytic.default')
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            analytic_account = anal_def_obj.account_get(cr, uid, line.order_id.shop_id.id, line.order_id.channel_id.id, context=context)
            if analytic_account:
                res[line.id] = analytic_account.analytic_id.name_get()[0]
            else:
                res[line.id] = None
        return res

    _columns = {'analytic_id': fields.function(_get_analytic_account, type='many2one', string='Analytic Account')}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: