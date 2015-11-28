## Module Name
*chian_location_invoice

### Requirement
* IF set multi chain location for SO, only the out-picking(Delivery Order) can generate Invoice
* SO WKf,When all Delivery Order done, the SO action to Done 
updated by Alex 2014-08-15: According to Julien (sarment), the SO action to done when the first move is finished.

### Definitions

### Assumptions

### Implementation 

##### Fields

##### Views

##### Report

##### Process
*	Sale Order
	** 	Workflow
	    transition 'trans_ship_end_done' add condition check_invoice_picking_done
	** 	Function Process:
	    check_invoice_picking_done, check the SO can be done or not
*	Stock Picking
	** Function  action_done, when a DO is done, try to Done the relation Sale Order.
	
*	Stock Move
    ** Function _prepare_chained_picking, only the 'out' picking can generate Invoice.
        Careful, If you set mutli chain location type = 'out', only the latest out picking
        can generate Invoice

##### Access Rights

















Quotation/Sale Order (Original Report) 
Requirements:
Reports should show the taxes applied to the SO.
Report should be bilingual, label in this report should have Chinese and English. Check reference.
shows the Original Price, the Discount, Final Price and the Subtotal.

Description
Quantity
UoM
Original Price
Discount
Final Price
Sub Total


Figure 4.3 Sale Order report 2 Requirement


ACL Requirements
The Sales Person can only review his / her own SO and quotation.
The Sales Administrative can check all SO.
Constraints.
None