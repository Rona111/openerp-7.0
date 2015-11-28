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
from openerp.osv import osv, fields
from hashlib import sha1
from random import random
import requests
import urllib2
import time
import json
import logging
_logger = logging.getLogger(__name__)


class product_product(osv.osv):
    _inherit = 'product.product'

    def _get_tax_code(self, prod):
        taxes = ''
        if prod and prod.taxes_id:
            for tax in prod.taxes_id:
                taxes += tax.description + ' '
        return taxes

    def _get_product_value(self, prod, field):
        if hasattr(prod, field):
            return getattr(prod, field) or ''
        else:
            return ""

    def _prepare_product_values(self, cr, uid, prod, context=None):
        #TODO sync product's QoH.
        values = {
            "ProductID": self._get_product_value(prod, 'tradevine_product_id'),
            "OrganisationID": "",
            "Code": self._get_product_value(prod, 'default_code'),
            "Name": prod.name or '',
            "Description": "",
            "AlternateCode": self._get_product_value(prod, 'default_code'),
            "UnitOfMeasure": prod and prod.uom_id and prod.uom_id.name or '',
            "Barcode": self._get_product_value(prod, 'ean13'),
            "InternalNotes": "",
            "ExternalNotes": "",
            "ProductCategoryID": prod and prod.categ_id and prod.categ_id.name
            or '',
            # "Weight": self._get_product_value(prod, 'weight'),
            # "Length": self._get_product_value(prod, 'length'),
            # "Width": self._get_product_value(prod, 'width'),
            # "Height": self._get_product_value(prod, 'height'),
            "Currency": "",
            "TaxClassID": "",
            "TaxCode": self._get_tax_code(prod),
            "WarehouseStock": "",
            "QuantityAvailableToSell": "",
            "QuantityAvailableToShip": "",
            "CostPrice": self._get_product_value(prod, 'standard_price'),
            "SellPriceIncTax": "",
            "SellPriceExTax": "",
            "MinimumStockQuantity": "",
            "OverrideSalesGLAccountCode": "",
            "OverrideSalesGLAccountName": "",
            "OverridePurchaseGLAccountCode": "",
            "OverridePurchaseGLAccountName": "",
            "PhotoIdentifier": "",
            "IsManualOrderApprovalNeeded": "",
            "CreatedDate": "",
            "CreatedBy": "",
            "ModifiedDate": "",
            "ModifiedBy": ""
        }
        return values

    def sync_tradevine_product_id(self, default_code):
        if not default_code:
            return 0, None
        #see if tradevine already has this porduct.
        url = 'https://api.tradevine.com/v1/Product/'
        nonce_val = sha1(str(random())).hexdigest()
        ts = time.time()
        url1 = url + '?code='
        url1 = url1 + str(default_code)
        url1 = url1 + '&oauth_token=95a4f5c8-6e47-4ce7-80d4-c1ad260e546d&oauth_nonce='
        url1 = url1 + nonce_val
        url1 = url1 + '&oauth_consumer_key=50fddadb-9d7e-4d13-84da-4f9aa8483cc4&oauth_signature_method=PLAINTEXT&oauth_timestamp='
        url1 = url1 + str(round(ts)).rstrip('0').rstrip('.')
        url1 = url1 + '&oauth_version=1.0&oauth_signature=c39cd0c9-7aa5-4c92-a948-53ed00571848%25263ccb1e80-adae-4040-8de4-2c1353e261b2'
        content = urllib2.urlopen(url1)
        result = json.load(content)
        if result:
            return result['TotalCount'], result['List']
        return 0, None

    def sync_with_tradevine(self, cr, uid, ids, context=None):

        """first check if the product is already exist on tradevine ,
        if so, read the ProductID on tradevine
        if not, create a new one on tradevine then
            write back ProductID on tradevine to OpenERP
        Parameters
        ----------
        Returns
        -------
        """
        try:
            context = context or {}
            url = 'https://api.tradevine.com/v1/Product/'
            headers = {'content-type': 'application/json'}
            for prod in self.browse(cr, uid, ids, context):
                values = self._prepare_product_values(cr, uid, prod, context)
                nonce_val = sha1(str(random())).hexdigest()
                ts = time.time()
                params = {
                    'oauth_token': 'd6ed94aa-78d0-4744-a58f-1227a053afe9',
                    'oauth_nonce': nonce_val,
                    'oauth_consumer_key': '40a99dbb-4fee-4fb3-8f68-72760d7471de',
                    'oauth_signature_method': 'PLAINTEXT',
                    'oauth_timestamp': str(round(ts)).rstrip('0').rstrip('.'),
                    'oauth_version': '1.0',
                    'oauth_signature': 'c58c3086-38dc-45e8-ad9f-092cca71818a%2526b67dd513-d5ed-4a18-9a38-ca4560d29ab7'
                }

                #check if tradevine already has this product code.
                count, result = self.sync_tradevine_product_id(
                    prod.default_code)
                if count:
                    tradevine_product_id = result[0].get('ProductID', '')
                    #write back the tradevineID to OpenERP
                    self.write(
                        cr, uid, [prod.id],
                        {'tradevine_product_id': str(tradevine_product_id)},
                        context)
                    if count > 1:
                        _logger.debug(
                            '***There are %d products share the same SKU!,'
                            'product SKU:%s\n' % (
                                count, prod.default_code))
                    continue
                #if not create a new one on tradevine.
                #if so overwrite it.
                #TODO will the TV create a new product even has the same code?
                if not prod.tradevine_product_id:
                    del values['ProductID']
                else:
                    url += values.get('ProductID', '')
                response = requests.post(
                    url, params=params, data=json.dumps(values),
                    headers=headers, verify=False)
                if response.status_code == 200:
                    result = response.json()
                    if result["ProductID"]:
                        self.write(
                            cr, uid, [prod.id],
                            {'tradevine_product_id': str(result["ProductID"])},
                            context)
            return True
        except Exception, e:
            _logger.error(
                'Error occurs when sync product to TV!\n Error: %s' % str(e))

    _columns = {
        'tradevine_product_id': fields.char('Tradevine Product Id'),
    }
