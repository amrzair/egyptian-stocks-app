# Complete list of Egyptian Stock Exchange (EGX) stocks
# Updated list with stock codes

EGYPTIAN_STOCKS = {
    # Banks
    "Commercial International Bank (CIB)": {"symbol": "COMI", "sector": "Banks"},
    "Qatar National Bank Alahli": {"symbol": "QNBA", "sector": "Banks"},
    "Credit Agricole Egypt": {"symbol": "CIEB", "sector": "Banks"},
    "Faisal Islamic Bank": {"symbol": "FAIT", "sector": "Banks"},
    "Abu Dhabi Islamic Bank Egypt": {"symbol": "ADIB", "sector": "Banks"},
    "Bank of Alexandria": {"symbol": "ALEX", "sector": "Banks"},
    "Egyptian Gulf Bank": {"symbol": "EGBE", "sector": "Banks"},
    "Housing & Development Bank": {"symbol": "HDBK", "sector": "Banks"},
    "Export Development Bank": {"symbol": "EXPA", "sector": "Banks"},
    
    # Real Estate
    "Talaat Moustafa Group (TMG)": {"symbol": "TMGH", "sector": "Real Estate"},
    "Palm Hills Development": {"symbol": "PHDC", "sector": "Real Estate"},
    "Madinet Nasr Housing": {"symbol": "MNHD", "sector": "Real Estate"},
    "SODIC": {"symbol": "OCDI", "sector": "Real Estate"},
    "Emaar Misr": {"symbol": "EMFD", "sector": "Real Estate"},
    "Amer Group": {"symbol": "AMER", "sector": "Real Estate"},
    "Porto Group": {"symbol": "PORT", "sector": "Real Estate"},
    "Orascom Development": {"symbol": "ORHD", "sector": "Real Estate"},
    
    # Financial Services
    "EFG Hermes": {"symbol": "HRHO", "sector": "Financial Services"},
    "Fawry": {"symbol": "FWRY", "sector": "Financial Services"},
    "E-Finance": {"symbol": "EFIH", "sector": "Financial Services"},
    "CI Capital": {"symbol": "CICH", "sector": "Financial Services"},
    "Beltone Financial": {"symbol": "BTFH", "sector": "Financial Services"},
    
    # Telecommunications
    "Telecom Egypt": {"symbol": "ETEL", "sector": "Telecommunications"},
    "Vodafone Egypt": {"symbol": "VODE", "sector": "Telecommunications"},
    
    # Healthcare
    "Cleopatra Hospitals": {"symbol": "CLHO", "sector": "Healthcare"},
    "Ibnsina Pharma": {"symbol": "ISPH", "sector": "Healthcare"},
    "Egyptian Pharma (EPICO)": {"symbol": "EPCO", "sector": "Healthcare"},
    "Rameda Pharma": {"symbol": "RMDA", "sector": "Healthcare"},
    "IDH (Integrated Diagnostics)": {"symbol": "IDHC", "sector": "Healthcare"},
    
    # Food & Beverages
    "Eastern Company": {"symbol": "EAST", "sector": "Food & Beverages"},
    "Juhayna": {"symbol": "JUFO", "sector": "Food & Beverages"},
    "Edita Food Industries": {"symbol": "EFID", "sector": "Food & Beverages"},
    "Domty": {"symbol": "DOMT", "sector": "Food & Beverages"},
    "Cairo Poultry": {"symbol": "POUL", "sector": "Food & Beverages"},
    "Delta Sugar": {"symbol": "SUGR", "sector": "Food & Beverages"},
    
    # Construction & Materials
    "Orascom Construction": {"symbol": "ORAS", "sector": "Construction"},
    "Arabian Cement": {"symbol": "ARCC", "sector": "Construction"},
    "Suez Cement": {"symbol": "SUCE", "sector": "Construction"},
    "Sinai Cement": {"symbol": "SCEM", "sector": "Construction"},
    "Ezz Steel": {"symbol": "ESRS", "sector": "Construction"},
    "Egyptian Iron & Steel": {"symbol": "IRON", "sector": "Construction"},
    
    # Chemicals
    "Sidi Kerir Petrochemicals (SIDPEC)": {"symbol": "SKPC", "sector": "Chemicals"},
    "Abu Qir Fertilizers": {"symbol": "ABUK", "sector": "Chemicals"},
    "Egypt Chem": {"symbol": "ECHEM", "sector": "Chemicals"},
    
    # Textiles
    "Oriental Weavers": {"symbol": "ORWE", "sector": "Textiles"},
    "Dice Sport": {"symbol": "DSCW", "sector": "Textiles"},
    
    # Technology
    "Raya Holding": {"symbol": "RAYA", "sector": "Technology"},
    "Elarabia for Information Technology": {"symbol": "AIAT", "sector": "Technology"},
    
    # Transportation
    "Alexandria Container (ALCN)": {"symbol": "ALCN", "sector": "Transportation"},
    "Canal Shipping": {"symbol": "CSAG", "sector": "Transportation"},
    
    # Energy
    "Sidi Kerir Sugar": {"symbol": "SUGR", "sector": "Energy"},
    "Alexandria Mineral Oils": {"symbol": "AMOC", "sector": "Energy"},
    
    # Tourism
    "Orascom Hotels": {"symbol": "OHTV", "sector": "Tourism"},
    "Egyptian Resorts": {"symbol": "EGTS", "sector": "Tourism"},
    
    # Others
    "GB Auto": {"symbol": "AUTO", "sector": "Automotive"},
    "El Sewedy Electric": {"symbol": "SWDY", "sector": "Industrial"},
    "Elsewedy Electric": {"symbol": "SWDY", "sector": "Industrial"},
}

def get_stock_list():
    """Return list of all stock names"""
    return list(EGYPTIAN_STOCKS.keys())

def get_stock_by_sector(sector):
    """Return stocks filtered by sector"""
    return {k: v for k, v in EGYPTIAN_STOCKS.items() if v['sector'] == sector}

def get_all_sectors():
    """Return list of all sectors"""
    return list(set(stock['sector'] for stock in EGYPTIAN_STOCKS.values()))

def get_stock_symbol(stock_name):
    """Return symbol for a stock name"""
    if stock_name in EGYPTIAN_STOCKS:
        return EGYPTIAN_STOCKS[stock_name]['symbol']
    return None