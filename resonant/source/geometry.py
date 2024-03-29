import math

class SphericalPt:
    def __init__(self, radius, polar_angle, azimuth_angle=0):
        """The polar angle represents the rotation along the xy plane. Azimuth represents
        3D component from xy"""
        self.radius = radius
        self.polar = polar_angle
        self.azimuth = azimuth_angle
    
    @classmethod
    def angle_only(cls, polar_angle):
        return SphericalPt(1, polar_angle, 0)

    def __str__(self):
        return f"Radius: {self.radius} -- Polar: {self.polar} -- Azimuth: {self.azimuth}"

    @classmethod
    def copy(cls, pt: 'SphericalPt') -> 'SphericalPt':
        return SphericalPt(pt.radius, pt.polar, pt.azimuth)

    def to_cartesian(self):
        x = self.radius * math.cos(self.azimuth) * math.cos(self.polar)
        y = self.radius * math.cos(self.azimuth) * math.sin(self.polar)
        z = self.radius * math.sin(self.azimuth)

        return (x, y, z)

    def __eq__(self, pt):
        return (self.radius == pt.radius) and (self.polar == pt.polar) and (self.azimuth == pt.azimuth)

    def within_margin(self, margin: 'SphericalPt', other_pt: 'SphericalPt'):
        """Returns whether or not the other point is within the specified margin. 0 margin angle means ignore.
        THIS DOES NOT TAKE THE RADIUS OF BOTH POINTS INTO ACCOUNT!"""
        in_polar = (abs(self.polar - other_pt.polar) <= margin.polar) or margin.polar == 0
        in_azimuth = (abs(self.azimuth - other_pt.azimuth) <= margin.azimuth) or margin.azimuth == 0
        return in_polar and in_azimuth





