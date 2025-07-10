import requests
import json
import logging
import os
from datetime import datetime


class SAPIntegration:

    def __init__(self):
        self.base_url = os.environ.get('SAP_B1_URL',
                                       'https://192.168.1.5:50000/b1s/v1/')
        self.company_db = os.environ.get('SAP_B1_COMPANY_DB',
                                         'EINV-TESTDB-LIVE-HUST')
        self.username = os.environ.get('SAP_B1_USERNAME', 'manager')
        self.password = os.environ.get('SAP_B1_PASSWORD', '1422')
        self.session_id = None
        self.session_timeout = None
        self.session_id = None
        self.session_timeout = None

    def login(self):
        """Login to SAP B1 Service Layer"""
        try:
            login_data = {
                'CompanyDB': self.company_db,
                'UserName': self.username,
                'Password': self.password
            }

            response = requests.post(f"{self.base_url}Login",
                                     json=login_data,
                                     verify=False,
                                     timeout=30)

            if response.status_code == 200:
                self.session_id = response.cookies.get('B1SESSION')
                self.session_timeout = response.cookies.get('ROUTEID')
                logging.info("Successfully logged in to SAP B1")
                return True
            else:
                logging.error(f"SAP B1 login failed: {response.status_code}")
                return False

        except Exception as e:
            logging.error(f"SAP B1 login error: {e}")
            return False

    def logout(self):
        """Logout from SAP B1 Service Layer"""
        if self.session_id:
            try:
                cookies = {
                    'B1SESSION': self.session_id,
                    'ROUTEID': self.session_timeout
                }

                response = requests.post(f"{self.base_url}Logout",
                                         cookies=cookies,
                                         verify=False,
                                         timeout=30)

                if response.status_code == 204:
                    logging.info("Successfully logged out from SAP B1")

            except Exception as e:
                logging.error(f"SAP B1 logout error: {e}")

            finally:
                self.session_id = None
                self.session_timeout = None

    def post_grpo_to_sap(self, grpo):
        """Post GRPO to SAP B1 as Purchase Receipt"""
        try:
            if not self.login():
                return None

            # Prepare GRPO data for SAP B1
            grpo_data = {
                'CardCode': grpo.purchase_order.supplier_code,
                'DocDate': grpo.receipt_date.isoformat(),
                'DocDueDate': grpo.receipt_date.isoformat(),
                'Comments': grpo.remarks or f"GRPO {grpo.grn_number}",
                'DocumentLines': []
            }

            # Add GRPO lines
            for line in grpo.grpo_lines:
                po_line = line.po_line
                grpo_line = {
                    'ItemCode': po_line.item_code,
                    'Quantity': float(line.received_quantity),
                    'Price': float(line.unit_price),
                    'WarehouseCode': po_line.warehouse_code,
                    'BaseType': 22,  # Purchase Order
                    'BaseEntry': grpo.purchase_order.sap_doc_entry,
                    'BaseLine':
                    po_line.line_number - 1  # SAP uses 0-based indexing
                }

                # Add batch information if available
                if line.batch_number:
                    grpo_line['BatchNumbers'] = [{
                        'BatchNumber':
                        line.batch_number,
                        'Quantity':
                        float(line.received_quantity),
                        'ExpiryDate':
                        line.expiry_date.isoformat()
                        if line.expiry_date else None
                    }]

                grpo_data['DocumentLines'].append(grpo_line)

            # Post to SAP B1
            cookies = {
                'B1SESSION': self.session_id,
                'ROUTEID': self.session_timeout
            }

            response = requests.post(f"{self.base_url}PurchaseReceipts",
                                     json=grpo_data,
                                     cookies=cookies,
                                     verify=False,
                                     timeout=60)

            if response.status_code == 201:
                result = response.json()
                doc_entry = result.get('DocEntry')
                logging.info(
                    f"GRPO {grpo.grn_number} posted to SAP B1 as DocEntry {doc_entry}"
                )
                return doc_entry
            else:
                logging.error(
                    f"SAP B1 GRPO posting failed: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logging.error(f"SAP B1 GRPO posting error: {e}")
            return None

        finally:
            self.logout()

    def get_purchase_orders(self, branch_id=None):
        """Get open purchase orders from SAP B1"""
        try:
            if not self.login():
                return []

            cookies = {
                'B1SESSION': self.session_id,
                'ROUTEID': self.session_timeout
            }

            # Build filter for open POs
            filter_params = "$filter=DocumentStatus eq 'bost_Open'"
            if branch_id:
                filter_params += f" and BPL_IDAssignedToInvoice eq {branch_id}"

            response = requests.get(
                f"{self.base_url}PurchaseOrders?{filter_params}",
                cookies=cookies,
                verify=False,
                timeout=60)

            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                logging.error(
                    f"SAP B1 PO retrieval failed: {response.status_code}")
                return []

        except Exception as e:
            logging.error(f"SAP B1 PO retrieval error: {e}")
            return []

        finally:
            self.logout()

    def sync_purchase_orders(self):
        """Sync purchase orders from SAP B1 to local database"""
        from models import PurchaseOrder, PurchaseOrderLine
        from app import db

        try:
            sap_pos = self.get_purchase_orders()

            for sap_po in sap_pos:
                # Check if PO already exists
                existing_po = PurchaseOrder.query.filter_by(
                    sap_doc_entry=sap_po['DocEntry']).first()

                if not existing_po:
                    # Create new PO
                    po = PurchaseOrder(
                        po_number=sap_po['DocNum'],
                        supplier_code=sap_po['CardCode'],
                        supplier_name=sap_po['CardName'],
                        branch_id=sap_po.get('BPL_IDAssignedToInvoice', '1'),
                        po_date=datetime.strptime(sap_po['DocDate'],
                                                  '%Y-%m-%d').date(),
                        delivery_date=datetime.strptime(
                            sap_po['DocDueDate'], '%Y-%m-%d').date(),
                        total_amount=sap_po['DocTotal'],
                        currency=sap_po['DocCurrency'],
                        sap_doc_entry=sap_po['DocEntry'])

                    db.session.add(po)
                    db.session.flush()  # Get the ID

                    # Add PO lines
                    for line in sap_po['DocumentLines']:
                        po_line = PurchaseOrderLine(
                            po_id=po.id,
                            line_number=line['LineNum'] +
                            1,  # Convert to 1-based
                            item_code=line['ItemCode'],
                            item_description=line['ItemDescription'],
                            ordered_quantity=line['Quantity'],
                            unit_price=line['Price'],
                            unit_of_measure=line['MeasureUnit'],
                            warehouse_code=line['WarehouseCode'])
                        db.session.add(po_line)

            db.session.commit()
            logging.info("Purchase orders synchronized from SAP B1")

        except Exception as e:
            logging.error(f"PO synchronization error: {e}")
            db.session.rollback()
