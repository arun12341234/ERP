"""
Consolidated Inventory & Procurement router.
Implements all 15 inventory & procurement business processes (16-30).
"""
from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_admin
from app.core.config import settings
from app.models.user import User
from app.models.product import Product
from app.models.bom import BOMItem
from app.models.vendor import Vendor
from app.models.purchase_requisition import PurchaseRequisition, PRStatus
from app.models.vendor_quotation import VendorQuotation
from app.models.purchase_order import PurchaseOrder, POStatus
from app.models.goods_receipt import GoodsReceiptNote, GRNStatus
from app.models.quality_inspection import QualityInspection
from app.models.stock_location import StockLocation, StockItem
from app.models.stock_transfer import StockTransfer, TransferStatus
from app.models.stock_count import StockCount, StockCountStatus

router = APIRouter(tags=["inventory"])


def apply_tenant_filter(query, model, user: User):
    if settings.ENABLE_TENANCY and hasattr(user, "tenant_id"):
        query = query.filter(getattr(model, "tenant_id") == user.tenant_id)
    return query


# ============= PRODUCTS (Process 16: Item Master Creation) =============

@router.post("/products", status_code=201)
def create_product(
    name: str,
    sku: str,
    product_type: str = "finished_good",
    cost_price: float = 0.0,
    selling_price: float = 0.0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 16: Item Master Creation - Create SKU and item master."""
    # Check SKU uniqueness
    existing = db.query(Product).filter(Product.sku == sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")

    product = Product(
        sku=sku,
        name=name,
        product_type=product_type,
        cost_price=cost_price,
        selling_price=selling_price
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        product.tenant_id = current_user.tenant_id

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products")
def list_products(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    query = apply_tenant_filter(query, Product, current_user)
    return query.offset(skip).limit(limit).all()


# ============= BOM (Process 17: BOM Definition) =============

@router.post("/bom", status_code=201)
def create_bom_item(
    product_id: int,
    component_id: int,
    quantity: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 17: BOM Definition - Define bill of materials."""
    # Validate hierarchy (prevent circular references)
    if product_id == component_id:
        raise HTTPException(status_code=400, detail="Product cannot be its own component")

    bom_item = BOMItem(
        product_id=product_id,
        component_id=component_id,
        quantity=quantity
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        bom_item.tenant_id = current_user.tenant_id

    db.add(bom_item)
    db.commit()
    db.refresh(bom_item)
    return bom_item


@router.get("/products/{product_id}/bom")
def get_product_bom(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get BOM for a product."""
    query = db.query(BOMItem).filter(BOMItem.product_id == product_id)
    query = apply_tenant_filter(query, BOMItem, current_user)
    return query.all()


# ============= VENDORS (Process 18: Vendor Registration) =============

@router.post("/vendors", status_code=201)
def create_vendor(
    name: str,
    email: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 18: Vendor Registration - Create vendor master."""
    # Auto-generate vendor code
    count = db.query(Vendor).count()
    vendor_code = f"V-{count + 1:05d}"

    vendor = Vendor(
        vendor_code=vendor_code,
        name=name,
        email=email
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        vendor.tenant_id = current_user.tenant_id

    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("/vendors")
def list_vendors(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Vendor)
    query = apply_tenant_filter(query, Vendor, current_user)
    return query.offset(skip).limit(limit).all()


@router.post("/vendors/{vendor_id}/evaluate")
def evaluate_vendor(
    vendor_id: int,
    rating: float,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Process 21: Vendor Evaluation - Score and rate vendor."""
    query = db.query(Vendor).filter(Vendor.id == vendor_id)
    query = apply_tenant_filter(query, Vendor, current_user)
    vendor = query.first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    vendor.rating = max(0, min(5, rating))  # 0-5 stars
    db.commit()
    db.refresh(vendor)
    return vendor


# ============= PURCHASE REQUISITIONS (Process 19) =============

@router.post("/purchase-requisitions", status_code=201)
def create_purchase_requisition(
    product_id: int,
    quantity: float,
    purpose: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 19: Purchase Requisition - Create PR from stock shortage."""
    count = db.query(PurchaseRequisition).count()
    pr_number = f"PR-{datetime.now().year}-{count + 1:05d}"

    pr = PurchaseRequisition(
        pr_number=pr_number,
        product_id=product_id,
        quantity=quantity,
        purpose=purpose,
        requested_by_id=current_user.id,
        status=PRStatus.DRAFT
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        pr.tenant_id = current_user.tenant_id

    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr


@router.post("/purchase-requisitions/{pr_id}/approve")
def approve_purchase_requisition(
    pr_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve purchase requisition."""
    query = db.query(PurchaseRequisition).filter(PurchaseRequisition.id == pr_id)
    query = apply_tenant_filter(query, PurchaseRequisition, current_user)
    pr = query.first()

    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")

    pr.status = PRStatus.APPROVED
    pr.approved_by_id = current_user.id
    pr.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(pr)
    return pr


# ============= VENDOR QUOTATIONS (Process 20) =============

@router.post("/vendor-quotations", status_code=201)
def create_vendor_quotation(
    vendor_id: int,
    product_id: int,
    quantity: float,
    unit_price: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 20: Vendor Quotation - Receive quotes from vendors."""
    count = db.query(VendorQuotation).count()
    quotation_number = f"VQ-{count + 1:05d}"

    quotation = VendorQuotation(
        quotation_number=quotation_number,
        vendor_id=vendor_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        total_price=quantity * unit_price
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        quotation.tenant_id = current_user.tenant_id

    db.add(quotation)
    db.commit()
    db.refresh(quotation)
    return quotation


# ============= PURCHASE ORDERS (Process 22: PO Creation) =============

@router.post("/purchase-orders", status_code=201)
def create_purchase_order(
    vendor_id: int,
    product_id: int,
    quantity: float,
    unit_price: float,
    pr_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 22: PO Creation - Create purchase order from approved PR."""
    count = db.query(PurchaseOrder).count()
    po_number = f"PO-{datetime.now().year}-{count + 1:05d}"

    po = PurchaseOrder(
        po_number=po_number,
        vendor_id=vendor_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=quantity * unit_price,
        pr_id=pr_id,
        created_by_id=current_user.id,
        status=POStatus.DRAFT
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        po.tenant_id = current_user.tenant_id

    db.add(po)
    db.commit()
    db.refresh(po)
    return po


@router.post("/purchase-orders/{po_id}/approve")
def approve_purchase_order(
    po_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve and send PO to vendor."""
    query = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id)
    query = apply_tenant_filter(query, PurchaseOrder, current_user)
    po = query.first()

    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    po.status = POStatus.APPROVED
    po.approved_by_id = current_user.id
    po.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(po)
    return po


# ============= GOODS RECEIPT (Process 23: GRN) =============

@router.post("/goods-receipts", status_code=201)
def create_goods_receipt(
    po_id: int,
    received_quantity: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 23: Goods Receipt - Inspect and verify delivery."""
    count = db.query(GoodsReceiptNote).count()
    grn_number = f"GRN-{datetime.now().year}-{count + 1:05d}"

    grn = GoodsReceiptNote(
        grn_number=grn_number,
        po_id=po_id,
        received_quantity=received_quantity,
        received_by_id=current_user.id,
        status=GRNStatus.PENDING
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        grn.tenant_id = current_user.tenant_id

    db.add(grn)
    db.commit()
    db.refresh(grn)

    # Update PO status
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if po:
        if received_quantity >= po.quantity:
            po.status = POStatus.FULLY_RECEIVED
        else:
            po.status = POStatus.PARTIALLY_RECEIVED
        db.commit()

    return grn


# ============= QUALITY INSPECTION (Process 24) =============

@router.post("/quality-inspections", status_code=201)
def create_quality_inspection(
    grn_id: int,
    inspected_quantity: float,
    passed_quantity: float,
    rejected_quantity: float,
    findings: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 24: Quality Inspection - Check quality of received goods."""
    count = db.query(QualityInspection).count()
    inspection_number = f"QI-{count + 1:05d}"

    inspection = QualityInspection(
        inspection_number=inspection_number,
        grn_id=grn_id,
        inspected_quantity=inspected_quantity,
        passed_quantity=passed_quantity,
        rejected_quantity=rejected_quantity,
        passed=(rejected_quantity == 0),
        findings=findings,
        inspected_by_id=current_user.id
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        inspection.tenant_id = current_user.tenant_id

    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    # Update GRN
    grn = db.query(GoodsReceiptNote).filter(GoodsReceiptNote.id == grn_id).first()
    if grn:
        grn.status = GRNStatus.INSPECTED
        grn.quality_check_passed = inspection.passed
        db.commit()

    return inspection


# ============= STOCK MANAGEMENT (Processes 25-27) =============

@router.post("/stock-locations", status_code=201)
def create_stock_location(
    location_code: str,
    warehouse: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create warehouse location."""
    location = StockLocation(
        location_code=location_code,
        warehouse=warehouse
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        location.tenant_id = current_user.tenant_id

    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.post("/stock-items/put-away")
def put_away_stock(
    grn_id: int,
    location_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 25: Inventory Put-Away - Assign bin and update stock."""
    grn = db.query(GoodsReceiptNote).filter(GoodsReceiptNote.id == grn_id).first()
    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")

    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == grn.po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    # Find or create stock item
    stock_item = db.query(StockItem).filter(
        StockItem.product_id == po.product_id,
        StockItem.location_id == location_id
    ).first()

    if stock_item:
        stock_item.quantity += grn.received_quantity
    else:
        stock_item = StockItem(
            product_id=po.product_id,
            location_id=location_id,
            quantity=grn.received_quantity,
            unit_cost=po.unit_price
        )
        db.add(stock_item)

    # Update GRN status
    grn.status = GRNStatus.PUT_AWAY
    db.commit()
    db.refresh(stock_item)
    return stock_item


@router.post("/stock-transfers", status_code=201)
def create_stock_transfer(
    product_id: int,
    from_location_id: int,
    to_location_id: int,
    quantity: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 26: Stock Transfer - Move inventory between locations."""
    count = db.query(StockTransfer).count()
    transfer_number = f"ST-{count + 1:05d}"

    transfer = StockTransfer(
        transfer_number=transfer_number,
        product_id=product_id,
        from_location_id=from_location_id,
        to_location_id=to_location_id,
        quantity=quantity,
        requested_by_id=current_user.id,
        status=TransferStatus.DRAFT
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        transfer.tenant_id = current_user.tenant_id

    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


@router.post("/stock-transfers/{transfer_id}/complete")
def complete_stock_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Complete stock transfer and update locations."""
    transfer = db.query(StockTransfer).filter(StockTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    # Deduct from source
    from_stock = db.query(StockItem).filter(
        StockItem.product_id == transfer.product_id,
        StockItem.location_id == transfer.from_location_id
    ).first()

    if not from_stock or from_stock.quantity < transfer.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    from_stock.quantity -= transfer.quantity

    # Add to destination
    to_stock = db.query(StockItem).filter(
        StockItem.product_id == transfer.product_id,
        StockItem.location_id == transfer.to_location_id
    ).first()

    if to_stock:
        to_stock.quantity += transfer.quantity
    else:
        to_stock = StockItem(
            product_id=transfer.product_id,
            location_id=transfer.to_location_id,
            quantity=transfer.quantity
        )
        db.add(to_stock)

    transfer.status = TransferStatus.COMPLETED
    transfer.completed_at = datetime.utcnow()
    db.commit()
    return transfer


@router.post("/stock-counts", status_code=201)
def create_stock_count(
    product_id: int,
    location_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 27: Stock Count - Physical inventory count."""
    # Get system quantity
    stock_item = db.query(StockItem).filter(
        StockItem.product_id == product_id,
        StockItem.location_id == location_id
    ).first()

    system_quantity = stock_item.quantity if stock_item else 0.0

    count = db.query(StockCount).count()
    count_number = f"SC-{count + 1:05d}"

    stock_count = StockCount(
        count_number=count_number,
        product_id=product_id,
        location_id=location_id,
        system_quantity=system_quantity,
        status=StockCountStatus.PLANNED
    )

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        stock_count.tenant_id = current_user.tenant_id

    db.add(stock_count)
    db.commit()
    db.refresh(stock_count)
    return stock_count


@router.post("/stock-counts/{count_id}/record")
def record_stock_count(
    count_id: int,
    physical_quantity: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record physical count and reconcile."""
    stock_count = db.query(StockCount).filter(StockCount.id == count_id).first()
    if not stock_count:
        raise HTTPException(status_code=404, detail="Stock count not found")

    stock_count.physical_quantity = physical_quantity
    stock_count.variance = physical_quantity - stock_count.system_quantity
    stock_count.counted_by_id = current_user.id
    stock_count.count_date = datetime.utcnow()
    stock_count.status = StockCountStatus.COMPLETED

    db.commit()
    db.refresh(stock_count)
    return stock_count


# ============= STOCK SUMMARY =============

@router.get("/stock-summary")
def get_stock_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 30: Inventory Valuation - Get stock levels and values."""
    query = db.query(StockItem)
    query = apply_tenant_filter(query, StockItem, current_user)

    stock_items = query.all()
    total_value = sum(item.quantity * item.unit_cost for item in stock_items)

    return {
        "total_items": len(stock_items),
        "total_value": total_value,
        "items": stock_items
    }
