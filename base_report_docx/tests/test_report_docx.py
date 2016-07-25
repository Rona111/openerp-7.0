# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from openerp.addons.base_report_docx.report.report_docx \
    import ReportDocx


class TestReportDocx(common.TransactionCase):
    def setUp(self):
        super(TestReportDocx, self).setUp()

    def test_generate_docx_data_with_empty(self):
        self.assertEqual([{}], ReportDocx(
            "report.testing.not.data", "testing").generate_docx_data(
            self.cr, 1, [1], {}))
