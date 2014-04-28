
#    MF=1 contains descriptive and miscellaneous data,
#    MF=2 contains resonance parameter data,
#    MF=3 contains reaction cross sections vs energy,
#    MF=4 contains angular distributions,
#    MF=5 contains energy distributions,
#    MF=6 contains energy-angle distributions,
#    MF=7 contains thermal scattering data,
#    MF=8 contains radioactivity data
#    MF=9-10 contain nuclide production data,
#    MF=12-15 contain photon production data, and
#    MF=30-36 contain covariance data.


class CrossSection:

    def __init__(self):
        self.energy = []
        self.value = []
        

class Isotope:

    def __init__(self):
        self.zaid = 00000
        pass


class Element:

    def __init__(self):
        pass


class Material:

    def __init__(self):
        pass