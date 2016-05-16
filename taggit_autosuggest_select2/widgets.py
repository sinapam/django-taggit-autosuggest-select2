import copy

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from taggit_autosuggest_select2.utils import edit_string_for_tags


MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_SELECT2_MAX_SUGGESTIONS', 20)


class TagAutoSuggest(forms.TextInput):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, str):
            tags = [o.tag for o in value.select_related("tag")]
            value = edit_string_for_tags(tags)

        result_attrs = copy.copy(attrs)
        result_attrs['type'] = 'hidden'
        result_html = super(TagAutoSuggest, self).render(name,
                                                         value,
                                                         result_attrs)
        widget_attrs = copy.copy(attrs)
        widget_attrs['id'] += '__tagautosuggest'
        widget_html = super(TagAutoSuggest, self).render(name,
                                                         value,
                                                         widget_attrs)

        start_text = self.attrs.get('start_text') or _("Enter Tag Here")
        empty_text = self.attrs.get('empty_text') or _("No Results")
        prompt_text = self.attrs.get('prompt_text') or _("Enter a tag")
        limit_text = self.attrs.get('limit_text') or _('No More Selections Are Allowed')

        context = {
            'result_id': result_attrs['id'],
            'widget_id': widget_attrs['id'],
            'url': reverse('taggit_autosuggest_select2-list-all'),
            'start_text': start_text,
            'prompt_text': prompt_text,
            'empty_text': empty_text,
            'limit_text': limit_text,
            'retrieve_limit': MAX_SUGGESTIONS,
        }
        js = render_to_string('taggable_input.html', context)

        return result_html + widget_html + mark_safe(js)

    class Media:
        js_base_url = getattr(settings, 'TAGGIT_AUTOSUGGEST_SELECT2_STATIC_BASE_URL', '%s' % settings.STATIC_URL)
        select2_css_url = getattr(settings,'TAGGIT_AUTOSUGGEST_SELECT2_CSS_URL','%scss/select2.css' % js_base_url)
        select2_js_url = getattr(settings,'TAGGIT_AUTOSUGGEST_SELECT2_JS_URL','%sjs/select2.min.js' % js_base_url)
        css = {'all': (select2_css_url,)}
        js = (select2_js_url,)
