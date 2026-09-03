"""
Smart Home Platform — Philips Hue CIE-1931 (xy Color Gamut to sRGB) Hardware Adapter
Performs bi-directional chromaticity conversions, wide-gamut clamping (Gamut A/B/C), and Hue Bridge REST API handling.
"""

from typing import Tuple, Dict, Any, Optional, List
import math
from pydantic import BaseModel, Field

# Philips Hue Color Gamut Triangles (CIE 1931 chromaticity coordinates)
HUE_GAMUTS = {
    # Gamut A (Hue LivingColors, early bulbs)
    "A": {
        "red": (0.704, 0.296),
        "green": (0.2151, 0.7106),
        "blue": (0.138, 0.08)
    },
    # Gamut B (Hue White & Color Ambiance Gen 1 & Gen 2)
    "B": {
        "red": (0.675, 0.322),
        "green": (0.409, 0.518),
        "blue": (0.167, 0.04)
    },
    # Gamut C (Hue White & Color Ambiance Gen 3+, Lightstrip Plus, Hue Go)
    "C": {
        "red": (0.692, 0.308),
        "green": (0.17, 0.70),
        "blue": (0.153, 0.048)
    }
}

class HueLightState(BaseModel):
    on: bool = True
    bri: int = Field(default=254, ge=0, le=254)
    hue: Optional[int] = Field(default=None, ge=0, le=65535)
    sat: Optional[int] = Field(default=None, ge=0, le=254)
    xy: Optional[List[float]] = None
    ct: Optional[int] = Field(default=None, ge=153, le=500)  # Mired color temperature (2000K to 6500K)
    alert: str = "none"  # "none", "select", "lselect"
    effect: str = "none"  # "none", "colorloop"
    transitiontime: int = 4  # in multiples of 100ms (4 = 400ms)
    reachable: bool = True

class PhilipsHueCIE1931Adapter:
    """Enterprise Philips Hue Hardware Protocol Adapter with Color Space Math."""

    def __init__(self, bridge_ip: str = "192.168.1.50", api_user: str = "smarthome_master_token"):
        self.bridge_ip = bridge_ip
        self.api_user = api_user
        self.lights_db: Dict[str, HueLightState] = {
            "1": HueLightState(on=True, bri=254, xy=[0.692, 0.308]),
            "2": HueLightState(on=True, bri=200, xy=[0.17, 0.70]),
            "3": HueLightState(on=False, bri=128, xy=[0.153, 0.048])
        }

    # =========================================================================
    # CIE-1931 COLOR SPACE CONVERSIONS & GAMUT CLAMPING
    # =========================================================================

    @staticmethod
    def rgb_to_xy_brightness(r: int, g: int, b: int, gamut_type: str = "C") -> Tuple[float, float, int]:
        """Convert standard 24-bit sRGB (0-255) to CIE-1931 xy coordinates and Hue brightness (0-254)."""
        # 1. Normalize RGB to [0.0, 1.0]
        r_norm = max(0.0, min(1.0, r / 255.0))
        g_norm = max(0.0, min(1.0, g / 255.0))
        b_norm = max(0.0, min(1.0, b / 255.0))

        # 2. Gamma correction to linear RGB
        r_lin = ((r_norm + 0.055) / 1.055) ** 2.4 if r_norm > 0.04045 else (r_norm / 12.92)
        g_lin = ((g_norm + 0.055) / 1.055) ** 2.4 if g_norm > 0.04045 else (g_norm / 12.92)
        b_lin = ((b_norm + 0.055) / 1.055) ** 2.4 if b_norm > 0.04045 else (b_norm / 12.92)

        # 3. Convert linear RGB to XYZ tristimulus (Wide D65 matrix)
        X = r_lin * 0.4124 + g_lin * 0.3576 + b_lin * 0.1805
        Y = r_lin * 0.2126 + g_lin * 0.7152 + b_lin * 0.0722
        Z = r_lin * 0.0193 + g_lin * 0.1192 + b_lin * 0.9505

        # 4. Calculate chromaticity coordinates x, y
        sum_xyz = X + Y + Z
        if sum_xyz == 0:
            cx, cy = 0.3127, 0.3290  # D65 White point default
        else:
            cx = X / sum_xyz
            cy = Y / sum_xyz

        # 5. Clamp chromaticity to designated Gamut triangle
        clamped_x, clamped_y = PhilipsHueCIE1931Adapter._clamp_to_gamut(cx, cy, gamut_type)
        brightness = int(round(Y * 254.0))
        brightness = max(1, min(254, brightness))

        return round(clamped_x, 4), round(clamped_y, 4), brightness

    @staticmethod
    def xy_brightness_to_rgb(x: float, y: float, brightness: int = 254, gamut_type: str = "C") -> Tuple[int, int, int]:
        """Convert CIE-1931 (x, y) chromaticity + Hue brightness (0-254) back to 24-bit sRGB."""
        # 1. Clamp input xy to Gamut
        cx, cy = PhilipsHueCIE1931Adapter._clamp_to_gamut(x, y, gamut_type)
        
        if cy == 0:
            cy = 0.00001
        
        # 2. Reconstruct XYZ from chromaticity and Luminance Y
        Y = max(0.0, min(1.0, brightness / 254.0))
        X = (Y / cy) * cx
        Z = (Y / cy) * (1.0 - cx - cy)

        # 3. Convert XYZ to linear RGB (Wide D65 inverse matrix)
        r_lin = X * 3.2406 - Y * 1.5372 - Z * 0.4986
        g_lin = -X * 0.9689 + Y * 1.8758 + Z * 0.0415
        b_lin = X * 0.0557 - Y * 0.2040 + Z * 1.0570

        # 4. Apply inverse gamma correction
        def _inv_gamma(c: float) -> float:
            c_clamped = max(0.0, c)
            if c_clamped <= 0.0031308:
                return 12.92 * c_clamped
            else:
                return (1.055 * (c_clamped ** (1.0 / 2.4))) - 0.055

        r_norm = _inv_gamma(r_lin)
        g_norm = _inv_gamma(g_lin)
        b_norm = _inv_gamma(b_lin)

        # 5. Scale to 0-255 integers
        r_int = int(round(max(0.0, min(1.0, r_norm)) * 255.0))
        g_int = int(round(max(0.0, min(1.0, g_norm)) * 255.0))
        b_int = int(round(max(0.0, min(1.0, b_norm)) * 255.0))

        return r_int, g_int, b_int

    @staticmethod
    def _clamp_to_gamut(x: float, y: float, gamut_type: str = "C") -> Tuple[float, float]:
        """Verify point-in-triangle or project point onto closest edge of Gamut triangle."""
        gamut = HUE_GAMUTS.get(gamut_type, HUE_GAMUTS["C"])
        p_r = gamut["red"]
        p_g = gamut["green"]
        p_b = gamut["blue"]

        # Vector cross product point-in-triangle test
        def _cross_product(p1: Tuple[float, float], p2: Tuple[float, float], p: Tuple[float, float]) -> float:
            return (p2[0] - p1[0]) * (p[1] - p1[1]) - (p2[1] - p1[1]) * (p[0] - p1[0])

        d1 = _cross_product(p_r, p_g, (x, y))
        d2 = _cross_product(p_g, p_b, (x, y))
        d3 = _cross_product(p_b, p_r, (x, y))

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        # If inside triangle
        if not (has_neg and has_pos):
            return x, y

        # Outside triangle: Project onto closest of 3 triangle line segments
        def _project_to_segment(p1: Tuple[float, float], p2: Tuple[float, float], p: Tuple[float, float]) -> Tuple[float, float]:
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            seg_len_sq = dx * dx + dy * dy
            if seg_len_sq == 0:
                return p1
            t = max(0.0, min(1.0, ((p[0] - p1[0]) * dx + (p[1] - p1[1]) * dy) / seg_len_sq))
            return p1[0] + t * dx, p1[1] + t * dy

        proj_rg = _project_to_segment(p_r, p_g, (x, y))
        proj_gb = _project_to_segment(p_g, p_b, (x, y))
        proj_br = _project_to_segment(p_b, p_r, (x, y))

        def _dist_sq(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
            return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

        d_rg = _dist_sq((x, y), proj_rg)
        d_gb = _dist_sq((x, y), proj_gb)
        d_br = _dist_sq((x, y), proj_br)

        if d_rg <= d_gb and d_rg <= d_br:
            return proj_rg
        elif d_gb <= d_rg and d_gb <= d_br:
            return proj_gb
        else:
            return proj_br

    # =========================================================================
    # HUE BRIDGE REST API HANDLING
    # =========================================================================

    def get_light_state(self, light_id: str) -> Optional[HueLightState]:
        return self.lights_db.get(light_id)

    def set_light_state(self, light_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch REST API state update to light."""
        if light_id not in self.lights_db:
            return {"error": {"type": 3, "address": f"/lights/{light_id}", "description": "resource not found"}}

        current = self.lights_db[light_id]
        if "on" in updates:
            current.on = bool(updates["on"])
        if "bri" in updates:
            current.bri = max(1, min(254, int(updates["bri"])))
        if "xy" in updates and len(updates["xy"]) == 2:
            cx, cy = self._clamp_to_gamut(updates["xy"][0], updates["xy"][1], "C")
            current.xy = [round(cx, 4), round(cy, 4)]
        if "ct" in updates:
            current.ct = max(153, min(500, int(updates["ct"])))
        if "alert" in updates:
            current.alert = updates["alert"]

        return {
            "success": {
                f"/lights/{light_id}/state/on": current.on,
                f"/lights/{light_id}/state/bri": current.bri,
                f"/lights/{light_id}/state/xy": current.xy
            }
        }

philips_hue_adapter = PhilipsHueCIE1931Adapter()
