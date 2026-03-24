"""
OpenTrack DMS Client — Cox Automotive SOAP/XML API integration for Patty Peck Honda.

Wraps the 5 certified Opentrack APIs:
  1. ServiceTypesLookup
  2. AppointmentAdd
  3. AddRepairOrder
  4. OpenRepairOrderLookup
  5. GetClosedRepairOrderDetails
"""

import logging
import os
import xml.etree.ElementTree as ET

import httpx

logger = logging.getLogger(__name__)

# Namespace constants
SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
WSSE_NS = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
OT_NS = "opentrack.dealertrack.com"
OT_NS_T = "opentrack.dealertrack.com/transitional"

# Config from env
OPENTRACK_URL = os.environ.get("OPENTRACK_URL", "https://otstaging.arkona.com/serviceapi.asmx")
OPENTRACK_USERNAME = os.environ.get("OPENTRACK_USERNAME", "")
OPENTRACK_PASSWORD = os.environ.get("OPENTRACK_PASSWORD", "")
OPENTRACK_COMPANY = os.environ.get("OPENTRACK_COMPANY_NUMBER", "ZE7")
OPENTRACK_ENTERPRISE = os.environ.get("OPENTRACK_ENTERPRISE_CODE", "ZE")


def _build_envelope(body_inner_xml: str) -> str:
    """Build full SOAP envelope with WS-Security header and dealer block baked into body_inner_xml."""
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:ot="opentrack.dealertrack.com">'
        "<soap:Header>"
        f'<wsse:Security xmlns:wsse="{WSSE_NS}">'
        "<wsse:UsernameToken>"
        f"<wsse:Username>{OPENTRACK_USERNAME}</wsse:Username>"
        '<wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/'
        'oasis-200401-wss-username-token-profile-1.0#PasswordText">'
        f"{OPENTRACK_PASSWORD}</wsse:Password>"
        "</wsse:UsernameToken>"
        "</wsse:Security>"
        "</soap:Header>"
        "<soap:Body>"
        f"{body_inner_xml}"
        "</soap:Body>"
        "</soap:Envelope>"
    )


def _dealer_block() -> str:
    """Return the <ot:Dealer> XML fragment."""
    return (
        "<ot:Dealer>"
        f"<ot:CompanyNumber>{OPENTRACK_COMPANY}</ot:CompanyNumber>"
        f"<ot:EnterpriseCode>{OPENTRACK_ENTERPRISE}</ot:EnterpriseCode>"
        "<ot:ServerName></ot:ServerName>"
        "</ot:Dealer>"
    )


def _send(soap_action: str, envelope: str) -> ET.Element:
    """Send SOAP POST request and return parsed XML root. Raises on HTTP or XML errors."""
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": soap_action,
    }
    resp = httpx.post(OPENTRACK_URL, content=envelope.encode("utf-8"), headers=headers, timeout=30.0)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    _check_errors(root)
    return root


def _check_errors(root: ET.Element) -> None:
    """Parse <Errors> block from SOAP response and raise if present."""
    for err in root.iter("Error"):
        code = _text(err, "Code")
        msg = _text(err, "Message") or _text(err, "Description") or "Unknown error"
        raise OpenTrackError(code=code, message=msg)
    for ns in [OT_NS, OT_NS_T]:
        for err in root.iter(f"{{{ns}}}Error"):
            code = _text_ns(err, "Code")
            msg = _text_ns(err, "Message") or _text_ns(err, "Description") or "Unknown error"
            raise OpenTrackError(code=code, message=msg)


def _text(parent: ET.Element, tag: str) -> str:
    """Get text of a child element by local name (no namespace)."""
    el = parent.find(tag)
    if el is None:
        # Try searching all descendants
        for child in parent.iter(tag):
            return (child.text or "").strip()
        return ""
    return (el.text or "").strip()


def _text_ns(parent: ET.Element, tag: str) -> str:
    """Get text of a child element using OpenTrack namespaces."""
    for ns in [OT_NS, OT_NS_T]:
        el = parent.find(f"{{{ns}}}{tag}")
        if el is not None:
            return (el.text or "").strip()
    for ns in [OT_NS, OT_NS_T]:
        for child in parent.iter(f"{{{ns}}}{tag}"):
            return (child.text or "").strip()
    return ""


def _find_result(root: ET.Element, result_tag: str) -> ET.Element | None:
    """Find the result element by local name, with or without namespace."""
    for el in root.iter(result_tag):
        return el
    for ns in [OT_NS, OT_NS_T]:
        for el in root.iter(f"{{{ns}}}{result_tag}"):
            return el
    return None


class OpenTrackError(Exception):
    """Raised when the SOAP response contains an <Errors> block."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"OpenTrack error [{code}]: {message}")


# =============================================================================
# PUBLIC API METHODS
# =============================================================================

def get_service_types() -> dict:
    """Fetch active service types from the dealer's DMS."""
    try:
        body = (
            "<ot:ServiceTypesLookup>"
            f"{_dealer_block()}"
            "<ot:SearchParams><ot:ActiveOnly>Y</ot:ActiveOnly></ot:SearchParams>"
            "</ot:ServiceTypesLookup>"
        )
        root = _send("opentrack.dealertrack.com/ServiceTypesLookup", _build_envelope(body))

        service_types = []
        for st in root.iter("ServiceType"):
            code = _text(st, "ServiceTypeCode") or _text(st, "Code")
            desc = _text(st, "ServiceTypeDescription") or _text(st, "Description")
            if code:
                service_types.append({"code": code, "description": desc})
        # Try namespaced if none found
        if not service_types:
            for st in root.iter(f"{{{OT_NS}}}ServiceType"):
                code = _text_ns(st, "ServiceTypeCode") or _text_ns(st, "Code")
                desc = _text_ns(st, "ServiceTypeDescription") or _text_ns(st, "Description")
                if code:
                    service_types.append({"code": code, "description": desc})

        return {"success": True, "service_types": service_types}
    except OpenTrackError as e:
        logger.error(f"OpenTrack ServiceTypesLookup error: {e}")
        return {"success": False, "error": e.message}
    except Exception as e:
        logger.error(f"ServiceTypesLookup failed: {e}")
        return {"success": False, "error": str(e)}


def add_appointment(
    customer_number: str,
    vin: str,
    date_time: str,
    service_type_code: str,
) -> dict:
    """
    Book a service appointment.

    Args:
        customer_number: DMS customer number (e.g. "1000048")
        vin: Vehicle Identification Number
        date_time: Appointment time in YYYYMMDDHHMI format (e.g. "202603251000")
        service_type_code: Service type code from get_service_types (e.g. "MAS")
    """
    try:
        body = (
            "<ot:AppointmentAdd>"
            f"{_dealer_block()}"
            "<ot:AppointmentAdd>"
            f"<ot:CustomerNumber>{customer_number}</ot:CustomerNumber>"
            f"<ot:VIN>{vin}</ot:VIN>"
            f"<ot:AppointmentDateTime>{date_time}</ot:AppointmentDateTime>"
            f"<ot:ServiceTypeCode>{service_type_code}</ot:ServiceTypeCode>"
            "</ot:AppointmentAdd>"
            "</ot:AppointmentAdd>"
        )
        root = _send("opentrack.dealertrack.com/AppointmentAdd", _build_envelope(body))

        result = _find_result(root, "AppointmentAddResult")
        if result is not None:
            key = _text(result, "AppointmentKey") or _text_ns(result, "AppointmentKey")
            status = _text(result, "Status") or _text_ns(result, "Status")
            return {"success": True, "appointment_key": key, "status": status}

        return {"success": True, "message": "Appointment submitted"}
    except OpenTrackError as e:
        logger.error(f"OpenTrack AppointmentAdd error: {e}")
        return {"success": False, "error": e.message}
    except Exception as e:
        logger.error(f"AppointmentAdd failed: {e}")
        return {"success": False, "error": str(e)}


def add_repair_order(
    customer_number: str,
    vin: str,
    odometer: int,
    service_writer_id: str,
    technician_id: str,
    labor_op_code: str,
    trans_code: str = "CP",
    promised_date_time: str = "",
) -> dict:
    """
    Create a repair order in the DMS.

    Args:
        customer_number: DMS customer number
        vin: Vehicle Identification Number
        odometer: Current odometer reading (must exceed last recorded)
        service_writer_id: Service writer ID (e.g. "SW01")
        technician_id: Technician ID (e.g. "TECH05")
        labor_op_code: Labor operation code (e.g. "LOF")
        trans_code: Transaction code — "CP" (Customer Pay), "WP" (Warranty), etc.
        promised_date_time: Promised completion in ISO format (e.g. "2026-03-25T17:00:00")
    """
    try:
        promised_xml = f"<ot:PromisedDateTime>{promised_date_time}</ot:PromisedDateTime>" if promised_date_time else ""
        body = (
            "<ot:AddRepairOrder>"
            f"{_dealer_block()}"
            "<ot:RepairOrder>"
            f"<ot:CustomerNumber>{customer_number}</ot:CustomerNumber>"
            f"<ot:VIN>{vin}</ot:VIN>"
            f"<ot:OdometerIn>{odometer}</ot:OdometerIn>"
            f"<ot:ServiceWriterID>{service_writer_id}</ot:ServiceWriterID>"
            f"{promised_xml}"
            "<ot:ServiceLines>"
            "<ot:ServiceLine>"
            "<ot:ServiceLineNumber>1</ot:ServiceLineNumber>"
            "<ot:LineType>A</ot:LineType>"
            f"<ot:TechnicianID>{technician_id}</ot:TechnicianID>"
            f"<ot:LaborOpCode>{labor_op_code}</ot:LaborOpCode>"
            f"<ot:TransCode>{trans_code}</ot:TransCode>"
            "</ot:ServiceLine>"
            "</ot:ServiceLines>"
            "</ot:RepairOrder>"
            "</ot:AddRepairOrder>"
        )
        root = _send("opentrack.dealertrack.com/AddRepairOrder", _build_envelope(body))

        result = _find_result(root, "AddRepairOrderResult")
        if result is not None:
            ro_key = _text(result, "RepairOrderKey") or _text_ns(result, "RepairOrderKey")
            status = _text(result, "Status") or _text_ns(result, "Status")
            return {"success": True, "repair_order_key": ro_key, "status": status}

        return {"success": True, "message": "Repair order submitted"}
    except OpenTrackError as e:
        logger.error(f"OpenTrack AddRepairOrder error: {e}")
        return {"success": False, "error": e.message}
    except Exception as e:
        logger.error(f"AddRepairOrder failed: {e}")
        return {"success": False, "error": str(e)}


def get_open_repair_orders(
    customer_number: str = "",
    vin: str = "",
) -> dict:
    """
    Look up open (in-progress) repair orders.

    Provide at least one of customer_number or vin.
    """
    try:
        lookup_params = ""
        if customer_number:
            lookup_params += f"<ot:CustomerNumber>{customer_number}</ot:CustomerNumber>"
        if vin:
            lookup_params += f"<ot:VIN>{vin}</ot:VIN>"

        body = (
            "<ot:OpenRepairOrderLookup>"
            f"{_dealer_block()}"
            f"<ot:LookupParms>{lookup_params}</ot:LookupParms>"
            "</ot:OpenRepairOrderLookup>"
        )
        root = _send("opentrack.dealertrack.com/OpenRepairOrderLookup", _build_envelope(body))

        repair_orders = []
        # Cox uses "Result" elements inside OpenRepairOrderLookupResult
        for tag in ["Result", "RepairOrder",
                     f"{{{OT_NS}}}Result", f"{{{OT_NS}}}RepairOrder",
                     f"{{{OT_NS_T}}}Result", f"{{{OT_NS_T}}}RepairOrder"]:
            for ro in root.iter(tag):
                ro_num = _text(ro, "RepairOrderNumber") or _text_ns(ro, "RepairOrderNumber")
                if not ro_num:
                    continue
                repair_orders.append({
                    "ro_number": ro_num,
                    "vin": _text(ro, "VIN") or _text_ns(ro, "VIN"),
                    "status": _text(ro, "ROStatus") or _text_ns(ro, "ROStatus") or _text(ro, "Status") or _text_ns(ro, "Status"),
                    "customer_name": _text(ro, "CustomerName") or _text_ns(ro, "CustomerName"),
                    "service_writer": _text(ro, "ServiceWriterID") or _text_ns(ro, "ServiceWriterID"),
                    "open_date": _text(ro, "OpenTransactionDate") or _text_ns(ro, "OpenTransactionDate"),
                    "make": _text(ro, "Make") or _text_ns(ro, "Make"),
                    "model": _text(ro, "Model") or _text_ns(ro, "Model"),
                    "year": _text(ro, "ModelYear") or _text_ns(ro, "ModelYear"),
                })
            if repair_orders:
                break

        return {"success": True, "repair_orders": repair_orders}
    except OpenTrackError as e:
        logger.error(f"OpenTrack OpenRepairOrderLookup error: {e}")
        return {"success": False, "error": e.message}
    except Exception as e:
        logger.error(f"OpenRepairOrderLookup failed: {e}")
        return {"success": False, "error": str(e)}


def get_closed_ro_details(ro_number: str) -> dict:
    """
    Get full details of a completed (closed) repair order.

    Args:
        ro_number: Repair order number (e.g. "9001414")
    """
    try:
        body = (
            "<ot:GetClosedRepairOrderDetails>"
            f"{_dealer_block()}"
            f"<ot:RepairOrderNumber>{ro_number}</ot:RepairOrderNumber>"
            "</ot:GetClosedRepairOrderDetails>"
        )
        root = _send("opentrack.dealertrack.com/GetClosedRepairOrderDetails", _build_envelope(body))

        result = _find_result(root, "GetClosedRepairOrderDetailsResult")
        if result is None:
            return {"success": True, "repair_order": None}

        # Find the RO element inside the result
        ro_el = None
        for tag in ["RepairOrder", f"{{{OT_NS}}}RepairOrder", f"{{{OT_NS_T}}}RepairOrder"]:
            ro_el = result.find(tag)
            if ro_el is None:
                for child in result.iter(tag):
                    ro_el = child
                    break
            if ro_el is not None:
                break

        if ro_el is None:
            return {"success": True, "repair_order": None}

        def _val(tag):
            return _text(ro_el, tag) or _text_ns(ro_el, tag)

        # Parse service lines
        service_lines = []
        for tag in ["ServiceLine", f"{{{OT_NS}}}ServiceLine", f"{{{OT_NS_T}}}ServiceLine"]:
            for line in ro_el.iter(tag):
                op = _text(line, "LaborOpCode") or _text_ns(line, "LaborOpCode")
                desc = _text(line, "Description") or _text_ns(line, "Description")
                labor_str = _text(line, "LaborAmount") or _text_ns(line, "LaborAmount")
                parts_str = _text(line, "PartsAmount") or _text_ns(line, "PartsAmount")
                service_lines.append({
                    "op_code": op,
                    "description": desc,
                    "labor": float(labor_str) if labor_str else 0.0,
                    "parts": float(parts_str) if parts_str else 0.0,
                })
            if service_lines:
                break

        def _float_val(tag):
            v = _val(tag)
            try:
                return float(v)
            except (ValueError, TypeError):
                return 0.0

        ro_data = {
            "ro_number": _val("RepairOrderNumber") or ro_number,
            "vin": _val("VIN"),
            "closed_date": _val("ClosedDateTime"),
            "odometer": int(_float_val("OdometerIn")),
            "service_lines": service_lines,
            "total_labor": _float_val("TotalLabor"),
            "total_parts": _float_val("TotalParts"),
            "total_amount": _float_val("TotalAmount"),
        }

        return {"success": True, "repair_order": ro_data}
    except OpenTrackError as e:
        logger.error(f"OpenTrack GetClosedRepairOrderDetails error: {e}")
        return {"success": False, "error": e.message}
    except Exception as e:
        logger.error(f"GetClosedRepairOrderDetails failed: {e}")
        return {"success": False, "error": str(e)}
