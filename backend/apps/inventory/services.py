from django.db.models import Q

from apps.catalog.models import ItemCopy

from .models import InventoryRead


def resolve_item_copy(scanned_code: str):
    normalized = scanned_code.strip()
    if not normalized:
        return None

    return (
        ItemCopy.objects.select_related('bibliographic_record', 'library_branch')
        .filter(
            Q(asset_code__iexact=normalized)
            | Q(barcode__iexact=normalized)
            | Q(rfid_tag__iexact=normalized)
        )
        .first()
    )


def register_scan(*, campaign, scanned_code: str, scan_source: str, session=None, operator=None, device_label: str = ''):
    item_copy = resolve_item_copy(scanned_code)
    match_status = InventoryRead.MatchStatus.MATCHED if item_copy else InventoryRead.MatchStatus.UNMATCHED

    return InventoryRead.objects.create(
        campaign=campaign,
        session=session,
        operator=operator or getattr(session, 'operator', None),
        item_copy=item_copy,
        scanned_code=scanned_code.strip(),
        scan_source=scan_source,
        match_status=match_status,
        device_label=device_label or getattr(session, 'device_label', ''),
    )
