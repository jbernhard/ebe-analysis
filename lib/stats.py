"""
Statistics.
"""


from numpy import exp
from scipy.stats import rv_continuous
from scipy.special import gamma


class grw_gen(rv_continuous):
    """
    Generalized Reverse Weibull distribution.

    PDF:
        
        a/gamma(g) * x^(a*g-1) * exp(-x^a)

    for x,a,g >= 0

    """

    def _pdf(self,x,a,g):
        return a/gamma(g) * pow(x,a*g-1) * exp(-pow(x,a))

    def _fitstart(self,data):
        return (2.0,1.0,0.0,0.02)

grw = grw_gen(a=0.0, name='grw', shapes='a,g')
