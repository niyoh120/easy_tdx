# src/easy_tdx/factor/__init__.py
"""因子研究模块。"""

from easy_tdx.factor.base import FACTORY_REGISTRY, Factor, register_factor

__all__ = ["Factor", "register_factor", "FACTORY_REGISTRY"]
