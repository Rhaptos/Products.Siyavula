from zope.interface import Interface
from zope.app.publisher.interfaces.browser import IBrowserView

class ISiyavulaView(IBrowserView):
    """ 
    Siyavula view
    """

    def available(self):
        """
        Return true if the authenticated member belongs to the 
        Siyavula organisation, false otherwise.
        """

class ISiyavulaAccountView(IBrowserView):
    """ 
    Siyavula account view
    """

    def available(self):
        """
        Return true if the authenticated member is the siyavula
        member, false otherwise.
        """

class ISiyavulaLensCount(IBrowserView):
    """ 
    Siyavula lens count
    """

    def getSiyavulaLensCount(self):
        """
        Returns the number of lenses in the Siyavula lens organisers
        """

class ISiyavulaForum(IBrowserView):
    """ 
    Siyavula ownership view
    """

    def isSiyavulaForum(self):
        """
        Returns True if siyavula user or workgroup owns the object
        """
