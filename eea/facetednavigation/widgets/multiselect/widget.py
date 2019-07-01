""" MultiSelect widget
"""
from plone.i18n.normalizer import urlnormalizer as normalizer
from Products.CMFCore.utils import getToolByName

from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import lowercase
from eea.facetednavigation.widgets.multiselect.interfaces import (
    DefaultSchemata,
    LayoutSchemata,
    CountableSchemata,
    DisplaySchemata,
)
from eea.facetednavigation.widgets.widget import CountableWidget
from eea.facetednavigation import EEAMessageFactory as _
import six


class Widget(CountableWidget):
    """ Widget
    """
    widget_type = 'multiselect'
    widget_label = _('Multi Select')

    groups = (
        DefaultSchemata,
        LayoutSchemata,
        CountableSchemata,
        DisplaySchemata
    )

    index = ViewPageTemplateFile('widget.pt')

    @property
    def css_class(self):
        """ Widget specific css class
        """
        css_type = self.widget_type
        css_title = normalizer.normalize(self.data.title)
        return ('faceted-multiselect-widget '
                'faceted-{0}-widget section-{1}').format(css_type, css_title)

    @property
    def default(self):
        """ Get default values
        """
        default = super(Widget, self).default
        if not default:
            return []

        if isinstance(default, (str, six.text_type)):
            default = [default, ]

        res = []
        for x in default:
            if six.PY2 and isinstance(x, six.text_type):
                x = x.encode('utf-8')
            res.append(x)
        return res

    def selected(self, key):
        """ Return True if key in self.default
        """
        default = self.default
        if not default:
            return False
        for item in default:
            if lowercase(key) == lowercase(item):
                return True
        return False

    @property
    def operator_visible(self):
        """ Is operator visible for anonymous users
        """
        return self.data.get('operator_visible', False)

    @property
    def operator(self):
        """ Get the default query operator
        """
        return self.data.get('operator', 'and')

    def query(self, form):
        """ Get value from form and return a catalog dict query
        """
        query = {}
        index = self.data.get('index', '')
        if six.PY2:
            index = index.encode('utf-8', 'replace')

        if not self.operator_visible:
            operator = self.operator
        else:
            operator = form.get(self.data.getId() + '-operator', self.operator)

        if six.PY2:
            operator = operator.encode('utf-8', 'replace')

        if not index:
            return query

        if self.hidden:
            value = self.default
        else:
            value = form.get(self.data.getId(), '')

        if not value:
            return query

        catalog = getToolByName(self.context, 'portal_catalog')
        catalog_index = catalog.Indexes.get(index)
        operator_supported = True
        if catalog_index:
            if catalog_index.meta_type == 'BooleanIndex':
                if value == 'False':
                    value = False
                elif value == 'True':
                    value = True
            operator_supported = 'operator' in getattr(
                catalog_index, 'query_options', [])

        query[index] = {'query': value}
        if operator_supported:
            query[index]['operator'] = operator
        return query
