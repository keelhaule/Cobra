from django.db import models
from django import forms
from apps.seller.models.asset import Asset
from apps.seller.models.product import Product
from apps.seller.models.seller import Seller
from apps.seller.models.image import Image
from apps.seller.models.photo import Photo
from apps.admin.models import Category

from django.forms.widgets import TextInput
class NumberInput(TextInput):
  input_type = 'tel'

class SellerEditForm(forms.Form):
  from apps.admin.models import Country

  name          = forms.CharField(required=False)
  email         = forms.EmailField(required=False)
  phone         = forms.CharField(widget=NumberInput(), required=False)

  bank_name     = forms.CharField(required=False)
  bank_account  = forms.CharField(required=False)

  bio           = forms.CharField(
                    widget=forms.Textarea(attrs={'class':"description"}),
                      required=False)
  bio_ol        = forms.CharField(
                    widget=forms.Textarea(attrs={'class':"description"}),
                      required=False)

  city          = forms.CharField(required=False)
  country       = forms.ModelChoiceField(queryset=Country.objects.all())
  coordinates   = forms.CharField(required=False)

  def clean_phone(self):
    import re #regular expressions
    phone = self.cleaned_data['phone']
    phone = re.sub('\D', '', phone)
    if 9 <= len(phone) <= 14:
      return phone
    elif len(phone) == 0:
      return None
    else:
      raise forms.ValidationError("number of digits incorrect")

class AssetForm(forms.Form):
  #this form is never meant to be submitted or validated
  #all editable elements are autosaved with ajax

  #no asset-id required in form
  #with seller_id, ilk, and rank together, the asset is unique
  seller_id   = forms.CharField(
                  widget=forms.TextInput(attrs={'class':"seller-id"}))
  ilk         = forms.CharField(
                  widget=forms.TextInput(attrs={'class':"ilk"}))
  rank        = forms.CharField(
                  widget=forms.TextInput(attrs={'class':"rank"}))

  DELETE      = forms.BooleanField(
                  widget=forms.CheckboxInput(
                    attrs={'class':"delete autosave"}))

  name        = forms.CharField(
                  widget=forms.TextInput(
                    attrs={'class':"name autosave"}),
                    max_length=50, required=False)
  description = forms.CharField(
                  widget=forms.Textarea(
                    attrs={'class':"description autosave"}),
                    required=False)

  name_ol     = forms.CharField(
                  widget=forms.TextInput(
                    attrs={'class':"name autosave"}),
                    max_length=50, required=False)
  description_ol= forms.CharField(
                    widget=forms.Textarea(
                      attrs={'class':"description autosave"}),
                      required=False)

  # choices must be formatted like [('group_title',(('1','opt1'),('2','opt2'))),]
  CATEGORY_ITEMS = []
  parent_categories = [c for c in Category.objects.all() if c.is_parent_category]
  for parent in parent_categories:
    sub_cats = ((str(parent.id),'other %s' % parent.name),)
    for sub in parent.sub_categories.all():
      keyword_string = " (%s)" % sub.keywords if sub.keywords else ""
      sub_cats = ((str(sub.id), "%s%s" % (sub.name,keyword_string)),) + sub_cats

    parent_keyword_string = " (%s)" % parent.keywords if parent.keywords else ""
    group = ("%s%s" % (parent.name, parent_keyword_string), sub_cats)
    CATEGORY_ITEMS.append(group)

  CATEGORY_ITEMS = [('','Category: None')] + CATEGORY_ITEMS

  category    = forms.ChoiceField(
                  widget=forms.Select(attrs={'class':"category autosave"}),
                  choices = CATEGORY_ITEMS,
                  required = False)

  phone       = forms.CharField(
                  widget=NumberInput(
                    attrs={'class':"phone autosave"}),
                    max_length=15, required=False)

class ProductEditForm(forms.Form):
  product_id        = forms.CharField(
                        widget=forms.TextInput(),
                        initial="none")

  assets            = forms.CharField(
                        widget=forms.TextInput(),
                        initial=" ")
  shipping_options  = forms.CharField(
                        widget=forms.TextInput(),
                        initial=" ")
  colors            = forms.CharField(
                        widget=forms.TextInput(),
                        initial=" ")

  price             = forms.CharField(
                        widget=NumberInput(attrs={'class':"autosave giveMeData",
                                            'min':'1', 'max':'30000','step':'1'}))
  length            = forms.CharField(
                        widget=NumberInput(attrs={'class':"autosave giveMeData",
                                            'min':'1', 'max':'30000','step':'1'}))
  width             = forms.CharField(
                        widget=NumberInput(attrs={'class':"autosave giveMeData",
                                            'min':'1', 'max':'30000','step':'1'}))
  height            = forms.CharField(
                        widget=NumberInput(attrs={'class':"autosave giveMeData",
                                            'min':'1', 'max':'30000','step':'1'}))
  weight            = forms.CharField(
                        widget=NumberInput(attrs={'class':"autosave giveMeData",
                                            'min':'1', 'max':'30000','step':'1'}))
