from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import simplejson
from apps.admin.controller.decorator import access_required
from django.views.decorators.csrf import csrf_exempt
from apps.seller.models import Seller
from apps.seller.controller.product_class import Product

def checkInventory(seller):
  #preferred method
  #incomplete_products = seller.product_set.filter('is_complete' = False)
  #if len(incomplete_products) > 1:
  #  incomplete_products[1:].delete()

  #hacked method
  try:
    keep = 1
    for product in seller.product_set.all():
      if not product.is_complete():
        if keep <= 0:
          product.delete()
        keep -= 1
  except:
    return False
  else:
    return True

@access_required('seller')
def create(request):
  seller = Seller.objects.get(id=request.session['seller_id'])
  checkInventory(seller)
  try:
    edit_this_product = None
    for product in seller.product_set.all():
      if not product.is_complete():
        edit_this_product = product

    if edit_this_product:
      request.product_id = edit_this_product.id
    product = Product(request)

    return redirect( str(product.product.id) + '/edit')

  except Exception as e:
    context = {'exception': e}
    from apps.seller.controller.management import home
    return home(request, context)
    #return redirect('')

@access_required('seller')
def edit(request, product_id):
  from apps.seller.controller.forms import ProductEditForm, PhotoForm
  from apps.seller.controller.management import signForm

  request.product_id = product_id
  product = Product(request)

  #if request.method == 'POST':
  #  try:
  #    product_form = ProductEditForm(request.POST)
  #    if product_form.is_valid():
  #      product_data = product_form.cleaned_data
  #      product.clear()
  #
  #      product.update('price',   product_data['price'])
  #      product.update('length',  product_data['length'])
  #      product.update('width',   product_data['width'])
  #      product.update('height',  product_data['height'])
  #      product.update('weight',  product_data['weight'])
  #
  #      asset_ids = product_data['assets'].split(" ")
  #      while '' in asset_ids: asset_ids.remove('') #remove empty instances
  #      for asset_id in asset_ids:
  #        product.addAsset(asset_id)
  #
  #      shipping_option_ids = product_data['shipping_options'].split(" ")
  #      while '' in shipping_option_ids: shipping_option_ids.remove('') #remove empty instances
  #      for shipping_option_id in shipping_option_ids:
  #        product.addShippingOption(shipping_option_id)
  #
  #      color_ids = product_data['colors'].split(" ")
  #      while '' in color_ids: color_ids.remove('') #remove empty instances
  #      for color_id in color_ids:
  #        product.addColor(color_id)
  #
  #      messages.success(request, "product saved")
  #      return redirect('seller:home')
  #
  #    else:
  #      context = {'problem': "form did not validate"}
  #
  #  except Exception as e:
  #    context = {'except': e}
  #
  #else:
  product_form = ProductEditForm()
  product_form.fields['price'].initial  = product.get('price')
  product_form.fields['length'].initial = product.get('length')
  product_form.fields['width'].initial  = product.get('width')
  product_form.fields['height'].initial = product.get('height')
  product_form.fields['weight'].initial = product.get('weight')

  for asset in product.product.assets.all():
    product_form.fields['assets'].initial += str(asset.id)+" "

  for color in product.product.colors.all():
    product_form.fields['colors'].initial += str(color.id)+" "

  for shipping_option in product.product.shipping_options.all():
    product_form.fields['shipping_options'].initial += str(shipping_option.id)+" "
  #end else

  product_form.fields['product_id'].initial = product.product.id
  # we want additional ranks going up to 5 photos
  add_ranks_range = range(product.product.photo_set.count()+1, 6)
  product.product.photos = product.product.photo_set.all()

  context = {
    'product':          product.product,
    'product_form':     product_form,
    'photo_form':       PhotoForm(),
    'add_ranks_range':  add_ranks_range
  }
  return render(request, 'inventory/edit.html', context)

@access_required('seller') #it's the 'r' in crud, but is it even needed?
def detail(request, product_id):
  return render(request, 'inventory/detail.html')

@access_required('seller')
def remove(request, product_id): #archive product and return to management home
  try:
    request.product_id = product_id
    product = Product(request)
    if product.remove():
      messages.success(request, "product %d removed." % product.product.id)
    else:
      messages.error(request, "cannot not remove that product")
  except Exception as e:
    context = {'exception':e}

  return redirect('seller:management home')

@access_required('seller')
def delete(request, id): #permenantly delete product and return to management home
  try:
    product = Product.objects.filter(seller_id=request.session['seller_id']).get(id=product_id)
    product.delete()
    messages.success(request, "product " + product.id + " (" + product.name + ") deleted.")
  except Product.DoesNotExist:
    messages.error(request, "could not find that seller's product")
  except Exception as e:
    context = {'exception': e}

  return redirect('seller:management home')

@access_required('seller')
@csrf_exempt
def saveProduct(request): #ajax requests only, not asset-aware
  context = {}

  if request.method == 'GET': # it must be an ajax GET to work
    try:
      request.product_id = request.GET['product_id']
      product = Product(request)

      attribute = request.GET['attribute']
      if 'status' in request.GET:
        status = request.GET['status']
      else:
        status = None

      if attribute == "asset":
        if status == "active":
          context['asset'] = product.addAsset(request.GET['asset_id'])
        else:
          context['asset'] = product.removeAsset(request.GET['asset_id'])

      elif attribute == "shipping option":
        if status == "active":
          context['shipping_option'] = product.addShippingOption(request.GET['shipping_option_id'])
        else:
          context['shipping_option'] = product.removeShippingOption(request.GET['shipping_option_id'])

      elif attribute == "color":
        if status == "active":
          context['color'] = product.addColor(request.GET['color_id'])
        else:
          context['color'] = product.removeColor(request.GET['color_id'])

      elif attribute == "photo":
        try:
          photo_id = request.GET['photo_id']
          if not photo_id:
            photo_id = None
          rank = request.GET['rank']
          url = request.GET['value']
          photo = product.addPhoto(url, rank, photo_id)
        except:
          contet['photo'] = "error saving photo"
        else:
          context['photo_id'] = photo.id
          context['photo'] = "saved photo at rank " + rank

      else:
        success_message = product.update(attribute, request.GET['value'])
        context['success'] = success_message

    except Exception as e:
      context = {'exception': e}

  else:
    context['problem'] = "not GET"

  response = context
  return HttpResponse(simplejson.dumps(response), mimetype='application/json')
  #return HttpResponse(context['exception'])
