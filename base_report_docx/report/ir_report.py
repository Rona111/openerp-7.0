# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields


class IrActionReportDocx(osv.osv):
    _inherit = 'ir.actions.report.xml'

    def _check_selection_field_value(self, cr, uid, field, value, context=None):
        if field == 'report_type' and value == 'docx':
            return

        return super(IrActionReportDocx, self)._check_selection_field_value(
            cr, uid, field, value, context=context)
