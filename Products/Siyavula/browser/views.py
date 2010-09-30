from Products.Five.browser import BrowserView
from zope.interface import implements
from interfaces import *
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

class SiyavulaView(BrowserView):

    implements(ISiyavulaView)

    def available(self):
        context = aq_inner(self.context)
        pms = getToolByName(context, 'portal_membership')
        pg = getToolByName(context, 'portal_groups')
       
        siyavula_member = pms.getMemberById('siyavula')
        if siyavula_member is None:
            return False
        siyavula_member_groups = pg.getGroupsForPrincipal(siyavula_member)
        if not siyavula_member_groups:
            return False

        auth_member = pms.getAuthenticatedMember()
        auth_member_groups = pg.getGroupsForPrincipal(auth_member)

        # Return true if the auth member belongs to the first siyavula group
        return siyavula_member_groups[0] in auth_member_groups

    __call__ = available

class SiyavulaAccountView(BrowserView):

    implements(ISiyavulaAccountView)

    def available(self):
        context = aq_inner(self.context)
        pms = getToolByName(context, 'portal_membership')
             
        return pms.getAuthenticatedMember().getId() == 'siyavula'

    __call__ = available

class SiyavulaLensCount(BrowserView):

    implements(ISiyavulaLensCount)

    def getSiyavulaLensCount(self):
        """
        Returns the number of lenses in the Siyavula lens organisers
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if portal.lenses.hasObject('siyavula'):
            lensFolder = portal.lenses.siyavula
            if lensFolder:
                lens_tool = getToolByName(portal, 'lens_tool')
                brains = lens_tool.searchResults( 
                        portal_type=lens_tool.getLensTypes(),
                        path='/'.join(lensFolder.getPhysicalPath()))
                return len(brains)
        return 0

    __call__ = getSiyavulaLensCount 

class SiyavulaForum(BrowserView):

    implements(ISiyavulaForum)

    def isSiyavulaForum(self):
        """True if object should have a forum. Possible for Lenses and Workgroups.
        Lenses true iff owned by 'siyavula'.
        WG true iff it has as a member a "siyavula member". A "siyavula member" is a member that
        is in the "siyavula group", the first workgroup of the 'siyavula' member.
        Also must satisfy 'SiyavulaView' criteria (auth member must be "siyavula member": in the "siyavula group")
        """
        context = aq_inner(self.context)
        
        view = SiyavulaView(context, context.REQUEST)
        if not view:   # short circuit to preserve non-Siyavula performance
            return view
        
        pms = getToolByName(context, 'portal_membership')
        pg = getToolByName(context, 'portal_groups')
        context_owner = context.getOwnerTuple()[1]  # 'getOwner' fails for groups on cnx.org at least,
                                                    # so don't use it. Also, this is shorter, probably faster.
       
        # Lens ownership
        siyavula_owned = context_owner == 'siyavula'  # for lenses
        
        # WG membership
        siyavula_wg = False
        context_group = None
        if context.portal_type == 'Workgroup':
            context_group = pg.getGroupById(context.getId())
        if context_group:  # None for group not found (probably normal member), so skip this
            context_members = set(context_group.getAllGroupMemberIds())
            
            siyavula_member = pms.getMemberById('siyavula')
            if siyavula_member:
                siyavula_member_groups = pg.getGroupsForPrincipal(siyavula_member)
                if siyavula_member_groups:
                    special_siyavula_group = siyavula_member_groups[0]
                    special_siyavula_group = pg.getGroupById(special_siyavula_group)
                    siyavula_group_member_ids = set(special_siyavula_group.getAllGroupMemberIds())
                    
                    common_members = siyavula_group_member_ids & context_members
                    if common_members:
                        siyavula_wg = True
        
        return (siyavula_owned or siyavula_wg) and view    # TODO: remove 'view'; see below
        # 'view' is always true, as it needs to be called to evaluate, and currently is checking
        # the existance of an object like '<Products.Siyavula.browser.views.SiyavulaView object at 0xdee992c>'
        # however, this is the behavior we want; apparently we don't care if non-siyavula users see
        # these links. only view state, and not current user state, should count.

    __call__ = isSiyavulaForum
