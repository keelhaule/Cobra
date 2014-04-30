from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
import json
from apps.admin.utils.decorator import access_required
from apps.admin.utils.exception_handling import ExceptionHandler
from django.views.decorators.csrf import csrf_exempt
from apps.seller.models.seller import Seller
from apps.seller.models.product import Product
from apps.seller.models.custom_order import CustomOrder
from settings.people import Tom, Dan
from apps.communication.controller.email_class import Email

def estimate(request):
  try:
    product = Product.objects.get(id=request.GET['product_id'])

    product.length = product.length if product.length else 1
    product.height = product.height if product.height else 1
    product.width  = product.width  if product.width  else 1
    old_volume = product.length * product.width * product.height

    #sort dimensions and update two biggest ones
    dimensions = [product.length, product.width, product.height]
    dimensions.sort() #sort numbers smallest to biggest
    dimensions.reverse() #reverse order, so now biggest first

    if request.GET.get('length') and int(request.GET['length']) > 0:
      dimensions[0] = int(request.GET['length'])
    if request.GET.get('width') and int(request.GET['width'])>0:
      dimensions[1]  = int(request.GET['width'])

    #get ratio from volume difference
    new_volume = dimensions[0] * dimensions[1] * dimensions[2]
    ratio = float(new_volume)/old_volume

    #scale ratio with quantity
    if request.GET.get('quantity') and request.GET['quantity'] > 1:
      ratio = ratio * int(request.GET['quantity'])

    #use ratio to scale price, weight
    product.price = int(round(product.price * ratio))
    product.weight = int(round(product.weight * ratio))
    #increase weight a bit to bump estimate to next shipping price tier if close
    product.weight = int(round((product.weight * 1.05) + 100)) #add 5% + 100grams

    response = {'display_price_estimate': product.display_price}
    product.pk = None #DO NOT SAVE!!!
    return HttpResponse(json.dumps(response), content_type='application/json')

  except Exception as e:
    ExceptionHandler(e, "error in product.custom_order_estimate")
    return HttpResponse(status=500)

@csrf_exempt
def request(request):
  if request.method == 'POST' and request.POST.get('email'):
    try:
      data = {
        'product':        Product.objects.get(id=request.POST['product_id']),
        'email':          request.POST['email'],
        'size':           request.POST.get('size', ""),
        'quantity':       request.POST.get('quantity', ""),
        'description':    request.POST.get('description', ""),
        'estimate':       request.POST.get('estimate', ""),
      }

      Email('custom_order/request', data).sendTo([Dan.email, data['email']])
      return HttpResponse(status=200)

    except Exception as e:
      ExceptionHandler(e, "error in custom_order.createCustomOrder")
      print str(e)
      return HttpResponse(status=500)

  else:
    return HttpResponse(status=400)
