from typing import Literal

# Expanded Entities in Uppercase Vietnamese
legal_entities = Literal[
    "NGƯỜI",            # Person (NGƯỜI)
    "TỔ CHỨC PHÁP LÝ",   # Legal Entity (TỔ CHỨC PHÁP LÝ)
    "HỢP ĐỒNG",          # Contract (HỢP ĐỒNG)
    "VĂN PHÒNG LUẬT",    # Law Firm (VĂN PHÒNG LUẬT)
    "CHÍNH PHỦ",         # Government (CHÍNH PHỦ)
    "THỎA THUẬN",        # Agreement (THỎA THUẬN)
    "NGÂN HÀNG",         # Bank (NGÂN HÀNG)
    "CÔNG TY",           # Company (CÔNG TY)
    "TỔ CHỨC NGOẠI GIAO", # NGO (TỔ CHỨC NGOẠI GIAO)
    "CÔNG DÂN",          # Citizen (CÔNG DÂN)
    "TỔ CHỨC TÀI CHÍNH", # Financial Institution (TỔ CHỨC TÀI CHÍNH)
    "QUỸ ĐẦU TƯ",       # Investment Fund (QUỸ ĐẦU TƯ)
    "CƠ QUAN QUẢN LÝ",   # Regulatory Authority (CƠ QUAN QUẢN LÝ)
    "TỔ CHỨC THƯƠNG MẠI" # Trade Organization (TỔ CHỨC THƯƠNG MẠI)
]

# Expanded Relations in Uppercase Vietnamese
legal_relations = Literal[
    "KÝ BỞI",           # Signed by (KÝ BỞI)
    "LÀM VIỆC CHO",     # Employed by (LÀM VIỆC CHO)
    "LÀ MỘT PHẦN CỦA",  # Part of (LÀ MỘT PHẦN CỦA)
    "ĐẠI DIỆN CHO",     # Represents (ĐẠI DIỆN CHO)
    "PHÊ DUYỆT BỞI",    # Approved by (PHÊ DUYỆT BỞI)
    "CHỨNG THỰC BỞI",   # Endorsed by (CHỨNG THỰC BỞI)
    "ĐỒNG Ý VỚI",       # Agreed to (ĐỒNG Ý VỚI)
    "TRANH CHẤP BỞI",   # Disputed by (TRANH CHẤP BỞI)
    "KÝ THAY CHO",      # Signed on behalf of (KÝ THAY CHO)
    "XÁC NHẬN BỞI",     # Validated by (XÁC NHẬN BỞI)
    "THAM GIA",          # Participated in (THAM GIA)
    "GIÁM SÁT",          # Supervised by (GIÁM SÁT)
    "KIỂM TRA",          # Audited by (KIỂM TRA)
    "THẨM ĐỊNH",         # Appraised by (THẨM ĐỊNH)
    "CUNG CẤP",          # Provided by (CUNG CẤP)
    "TÀI TRỢ BỞI",       # Financed by (TÀI TRỢ BỞI)
    "QUẢN LÝ BỞI",       # Managed by (QUẢN LÝ BỞI)
    "THỪA NHẬN",         # Acknowledged by (THỪA NHẬN)
    "QUYỀN SỞ HỮU",      # Owns (QUYỀN SỞ HỮU)
    "THỰC HIỆN BỞI",     # Executed by (THỰC HIỆN BỞI)
    "THAM DỰ",           # Attended by (THAM DỰ)
    "PHÂN PHỐI",         # Distributed by (PHÂN PHỐI)
]
# Expanded Validation Schema with Uppercase Vietnamese entities and relations
legal_validation_schema = [
    ("NGƯỜI", "KÝ BỞI", "HỢP ĐỒNG"),              # Person signs Contract
    ("TỔ CHỨC PHÁP LÝ", "KÝ BỞI", "HỢP ĐỒNG"),      # Legal Entity signs Contract
    ("NGƯỜI", "LÀM VIỆC CHO", "CÔNG TY"),          # Person works for Company
    ("CÔNG TY", "LÀ MỘT PHẦN CỦA", "TỔ CHỨC PHÁP LÝ"), # Company is part of Legal Entity
    ("VĂN PHÒNG LUẬT", "ĐẠI DIỆN CHO", "NGƯỜI"),    # Law Firm represents Person
    ("NGÂN HÀNG", "PHÊ DUYỆT BỞI", "HỢP ĐỒNG"),     # Bank approves Contract
    ("QUỸ ĐẦU TƯ", "CUNG CẤP", "TỔ CHỨC PHÁP LÝ"),   # Investment Fund provides Legal Entity
    ("CÔNG TY", "TÀI TRỢ BỞI", "NGÂN HÀNG"),        # Company is financed by Bank
    ("TỔ CHỨC NGOẠI GIAO", "THAM GIA", "THỎA THUẬN"), # NGO participates in Agreement
    ("CHÍNH PHỦ", "GIÁM SÁT", "HỢP ĐỒNG"),          # Government supervises Contract
    ("TỔ CHỨC PHÁP LÝ", "KIỂM TRA", "CÔNG TY"),      # Legal Entity audits Company
    ("NGƯỜI", "THẨM ĐỊNH", "HỢP ĐỒNG"),             # Person appraises Contract
    ("CÔNG TY", "QUẢN LÝ BỞI", "CƠ QUAN QUẢN LÝ"),    # Company managed by Regulatory Authority
    ("VĂN PHÒNG LUẬT", "THỪA NHẬN", "HỢP ĐỒNG"),     # Law Firm acknowledges Contract
    ("CÔNG TY", "THỰC HIỆN BỞI", "HỢP ĐỒNG"),        # Company executes Contract
    ("TỔ CHỨC TÀI CHÍNH", "PHÂN PHỐI", "NGÂN HÀNG"),  # Financial Institution distributes Bank
    ("CƠ QUAN QUẢN LÝ", "KÝ THAY CHO", "CHÍNH PHỦ"),   # Regulatory Authority signs on behalf of Government
    ("CÔNG DÂN", "ĐỒNG Ý VỚI", "THỎA THUẬN"),        # Citizen agrees to Agreement
    ("NGƯỜI", "TRANH CHẤP BỞI", "HỢP ĐỒNG"),          # Person disputes Contract
    ("TỔ CHỨC NGOẠI GIAO", "THAM DỰ", "HỢP ĐỒNG")     # NGO attends Contract
]
