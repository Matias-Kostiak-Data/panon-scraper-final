"""
Domain Finder Package
Automated athletics domain discovery for US colleges and universities.

Version: 1.0
Date: 2025-11-15
Author: Matias Kostiak Data
"""

__version__ = "1.0.0"
__author__ = "Matias Kostiak Data"
__email__ = "Matias-Kostiak-Data"
__license__ = "Proprietary"

# Package metadata
__title__ = "Domain Finder"
__description__ = "Automated athletics domain discovery system"
__url__ = "https://github.com/Matias-Kostiak-Data/domain-finder"

# Import main classes for easier access
from .domain_finder import DomainFinder, process_schools_with_resume

__all__ = [
    'DomainFinder',
    'process_schools_with_resume',
    '__version__',
    '__author__',
]