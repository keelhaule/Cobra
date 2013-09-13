from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from apps.admin.controller.decorator import access_required
from django.contrib import messages
from django.forms.models import modelformset_factory
from django.utils import simplejson
from datetime import datetime
from apps.seller.models import Product
from settings.people import Tom
from apps.communication.controller.email_class import Email

@access_required('admin')
def review_products(request):
  products_to_review = (Product.objects.filter(approved_at=None,
                                               active_at__lte=datetime.today(),
                                               in_holding=False)
                        .order_by('updated_at'))

  products_in_holding = (Product.objects.filter(in_holding=True)
                        .order_by('updated_at'))

  context = {'products_to_review': products_to_review,
             'products_in_holding': products_in_holding
            }
  return render(request, 'products/review_products.html', context)

@access_required('admin')
def unrated_products(request):
  from django.db.models import Count
  unrated_products = (Product.objects.filter(sold_at=None,
                                             approved_at__lte=datetime.today())
                      .annotate(rating_count=Count('rating'))
                      .filter(rating_count__lt=3))

  return render(request, 'products/unrated_products.html', {'products':unrated_products})

@access_required('admin')
def approve_product(request): #from AJAX GET request
  from apps.seller.models import Product
  try:
    product_id = request.GET['product_id']
    action = request.GET['action']
    product = Product.objects.get(id=product_id)
    if action == 'approve':
      product.in_holding = False
      product.approved_at = datetime.now()
      product.save()
    elif action == 'hold':
      product.approved_at = None
      product.in_holding = True
      product.save()
    elif action == 'delete':
      product.delete();
    else:
      raise Exception('invalid action: %s' % action)
  except Exception as e:
    response = {'error': str(e)}
    Email(message="error on product approval: "+str(e)).sendTo(Tom.email)
  else:
    response = {'success': "%s %s" % (action, product_id)}

  return HttpResponse(simplejson.dumps(response), mimetype='application/json')

@access_required('admin')
def rate_product(request): #from AJAX GET request
  from apps.seller.models import Product
  from apps.public.models import Rating
  from apps.admin.models import RatingSubject
  try:
    product_id      = request.GET.get('product_id')
    rating_subject  = request.GET.get('subject')
    rating_value    = request.GET.get('value')

    rating_subject_object = RatingSubject.objects.get(name=rating_subject)

    rating = Rating.objects.filter(
              session_key=request.session.session_key,
              subject=rating_subject_object,
              product_id=product_id
            )
    if rating:
      rating[0].value = rating_value
      rating[0].save()
    else:
      rating = Rating(
                  session_key=request.session.session_key,
                  subject=rating_subject_object,
                  product_id=product_id,
                  value = rating_value
                )
      rating.save()

  except Exception as e:
    response = {'error': e}
    Email(message="error in logout function: "+str(e)).sendTo(Tom.email)
  else:
    response = {'success': "%s rated" % product_id}

  return HttpResponse(simplejson.dumps(response), mimetype='application/json')
