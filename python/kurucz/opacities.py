from .opacity import *

class Opacities:
    """Container class for all opacity types."""
    def __init__(self):
        self.hydrogen = HydrogenOpacity()
        self.helium = HeliumOpacity()
        self.boron = BoronOpacity()
        self.carbon = CarbonOpacity()
        self.aluminum = AluminumOpacity()
        self.oxygen = OxygenOpacity()
        self.calcium = CalciumOpacity()
        self.kalium = KaliumOpacity()
        self.magnesium = MagnesiumOpacity()
        self.silicon = SiliconOpacity()
        self.iron = IronOpacity()
        self.diatomic = DiatomicMolecularOpacity()