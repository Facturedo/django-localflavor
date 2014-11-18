"""
Chile specific form helpers.
"""

from __future__ import absolute_import, unicode_literals

from django import forms
from django.core.validators import EMPTY_VALUES
from django.forms.fields import RegexField, Select
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text

from .cl_territory import REGION_CHOICES, PROVINCE_CHOICES, COMMUNE_CHOICES


class CLRegionSelect(Select):
    """
    A Select widget that uses a list of Chilean Regions (Regiones)
    as its choices.
    """
    def __init__(self, attrs=None):
        super(CLRegionSelect, self).__init__(attrs, choices=REGION_CHOICES)


class CLProvinceSelect(Select):
    """
    A Select widget that uses a list of Chilean Provinces (Provincias)
    as its choices.
    """
    def __init__(self, attrs=None):
        super(CLProvinceSelect, self).__init__(attrs, choices=PROVINCE_CHOICES)


class CLCommuneSelect(Select):
    """
    A Select widget that uses a list of Chilean Communes (Comunas)
    as its choices.
    """
    def __init__(self, attrs=None):
        super(CLCommuneSelect, self).__init__(attrs, choices=COMMUNE_CHOICES)


class CLLocationField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        error_messages = {
            'incomplete': 'Enter a valid location.',
            }
        fields = (
            forms.CharField(),
            forms.CharField(),
            forms.CharField()
            )
        super(CLLocationField, self).__init__(error_messages=error_messages,
                                              fields=fields,
                                              require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        return data_list[-1]


class CLLocationWidget(forms.widgets.MultiWidget):
    def __init__(self, attrs=None):
        _widgets = (
            CLRegionSelect(),
            CLProvinceSelect(),
            CLCommuneSelect(),
            )
        super(CLLocationWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return [value[:2], value[:3], value]
        else:
            return []

    class Media:
        js = ('localflavor/cl/js/cl_location_widget.js',)


class CLRutField(RegexField):
    """
    Chilean "Rol Unico Tributario" (RUT) field. This is the Chilean national
    identification number.

    Samples for testing are available from
    https://palena.sii.cl/cvc/dte/ee_empresas_emisoras.html
    """
    default_error_messages = {
        'invalid': _('Enter a valid Chilean RUT.'),
        'strict': _('Enter a valid Chilean RUT. The format is XX.XXX.XXX-X.'),
        'checksum': _('The Chilean RUT is not valid.'),
    }

    def __init__(self, *args, **kwargs):
        if 'strict' in kwargs:
            del kwargs['strict']
            super(CLRutField, self).__init__(r'^(\d{1,2}\.)?\d{3}\.\d{3}-[\dkK]$',
                                             error_message=self.default_error_messages['strict'],
                                             *args, **kwargs)
        else:
            # In non-strict mode, accept RUTs that validate but do not exist in
            # the real world.
            super(CLRutField, self).__init__(r'^[\d\.]{1,11}-?[\dkK]$', *args, **kwargs)

    def clean(self, value):
        """
        Check and clean the Chilean RUT.
        """
        super(CLRutField, self).clean(value)
        if value in EMPTY_VALUES:
            return ''
        rut, verificador = self._canonify(value)
        if self._algorithm(rut) == verificador:
            return self._format(rut, verificador)
        else:
            raise forms.ValidationError(self.error_messages['checksum'])

    def _algorithm(self, rut):
        """
        Takes RUT in pure canonical form, calculates the verifier digit.
        """
        suma = 0
        multi = 2
        for r in rut[::-1]:
            suma += int(r) * multi
            multi += 1
            if multi == 8:
                multi = 2
        return '0123456789K0'[11 - suma % 11]

    def _canonify(self, rut):
        """
        Turns the RUT into one normalized format. Returns a (rut, verifier)
        tuple.
        """
        rut = smart_text(rut).replace(' ', '').replace('.', '').replace('-', '')
        return rut[:-1], rut[-1].upper()

    def _format(self, code, verifier=None):
        """
        Formats the RUT from canonical form to the common string representation.
        If verifier=None, then the last digit in 'code' is the verifier.
        """
        if verifier is None:
            verifier = code[-1]
            code = code[:-1]
        while len(code) > 3 and '.' not in code[:3]:
            pos = code.find('.')
            if pos == -1:
                new_dot = -3
            else:
                new_dot = pos - 3
            code = code[:new_dot] + '.' + code[new_dot:]
        return '%s-%s' % (code, verifier)
