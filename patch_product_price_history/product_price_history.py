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

from openerp.osv import orm, osv


class product_product(orm.Model):
    _inherit = "product.product"

    def do_change_standard_price(self, cr, uid, ids, datas, context=None):
        """ Changes the Standard Price of Product and creates an account move accordingly.
        @param datas : dict. contain default datas like new_price, stock_output_account, stock_input_account, stock_journal
        @param context: A standard dictionary
        @return:

        overwrite this function to only go through locations belong to own company
        and create accout moves acordingly.
        """
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        if context is None:
            context = {}

        new_price = datas.get('new_price', 0.0)
        stock_output_acc = datas.get('stock_output_account', False)
        stock_input_acc = datas.get('stock_input_account', False)
        journal_id = datas.get('stock_journal', False)
        product_obj=self.browse(cr, uid, ids, context=context)[0]
        account_valuation = product_obj.categ_id.property_stock_valuation_account_id
        account_valuation_id = account_valuation and account_valuation.id or False
        if not account_valuation_id: raise osv.except_osv(_('Error!'), _('Specify valuation Account for Product Category: %s.') % (product_obj.categ_id.name))
        move_ids = []
        #<<<<< here we modify the domain.
        # get the company_id
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        loc_ids = location_obj.search(
            cr, uid,
            [('usage', '=', 'internal'), ('company_id', '=', company_id), ('active', '=', True)])
        for rec_id in ids:
            for location in location_obj.browse(cr, uid, loc_ids, context=context):
                c = context.copy()
                c.update({
                    'location': location.id,
                    'compute_child': False
                })

                product = self.browse(cr, uid, rec_id, context=c)
                qty = product.qty_available
                diff = product.standard_price - new_price
                if not diff: raise osv.except_osv(_('Error!'), _("No difference between standard price and new price!"))
                if qty > 0:
                    # company_id = location.company_id and location.company_id.id or False
                    # if not company_id: raise osv.except_osv(_('Error!'), _('Please specify company in Location.'))
                    #
                    # Accounting Entries
                    #
                    if not journal_id:
                        journal_id = product.categ_id.property_stock_journal and product.categ_id.property_stock_journal.id or False
                    if not journal_id:
                        raise osv.except_osv(_('Error!'),
                            _('Please define journal '\
                              'on the product category: "%s" (id: %d).') % \
                                (product.categ_id.name,
                                    product.categ_id.id,))
                    move_id = move_obj.create(cr, uid, {
                                'journal_id': journal_id,
                                'company_id': company_id
                                })
                    move_ids.append(move_id)

                    if diff > 0:
                        if not stock_input_acc:
                            stock_input_acc = product.\
                                property_stock_account_input.id
                        if not stock_input_acc:
                            stock_input_acc = product.categ_id.\
                                    property_stock_account_input_categ.id
                        if not stock_input_acc:
                            raise osv.except_osv(_('Error!'),
                                    _('Please define stock input account ' \
                                            'for this product: "%s" (id: %d).') % \
                                            (product.name,
                                                product.id,))
                        amount_diff = qty * diff
                        move_line_obj.create(cr, uid, {
                                    'name': product.name,
                                    'account_id': stock_input_acc,
                                    'debit': amount_diff,
                                    'move_id': move_id,
                                    })
                        move_line_obj.create(cr, uid, {
                                    'name': product.categ_id.name,
                                    'account_id': account_valuation_id,
                                    'credit': amount_diff,
                                    'move_id': move_id
                                    })
                    elif diff < 0:
                        if not stock_output_acc:
                            stock_output_acc = product.\
                                property_stock_account_output.id
                        if not stock_output_acc:
                            stock_output_acc = product.categ_id.\
                                    property_stock_account_output_categ.id
                        if not stock_output_acc:
                            raise osv.except_osv(_('Error!'),
                                    _('Please define stock output account ' \
                                            'for this product: "%s" (id: %d).') % \
                                            (product.name,
                                                product.id,))
                        amount_diff = qty * -diff
                        move_line_obj.create(cr, uid, {
                                        'name': product.name,
                                        'account_id': stock_output_acc,
                                        'credit': amount_diff,
                                        'move_id': move_id
                                    })
                        move_line_obj.create(cr, uid, {
                                        'name': product.categ_id.name,
                                        'account_id': account_valuation_id,
                                        'debit': amount_diff,
                                        'move_id': move_id
                                    })

            self.write(cr, uid, [rec_id], {'standard_price': new_price})
        return move_ids
