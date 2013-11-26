from django.core.cache import cache
from apps.seller.models import Product
from apps.admin.utils.decorator import postpone

#async?
def invalidate_cache(fragment_name, *vary_on):
  try:
    cache_key = template_cache_key(fragment_name, *vary_on)
    cache.delete(cache_key)
  except:
    return False
  else:
    return True

def template_cache_key(fragment_name, *vary_on):
  # Builds a cache key for a template fragment
  from django.utils.hashcompat import md5_constructor
  from django.utils.http import urlquote

  base_cache_key = "template.cache.%s" % fragment_name
  args = md5_constructor(u":".join([urlquote(var) for var in vary_on]))
  return "%s.%s" % (base_cache_key, args.hexdigest())

@postpone
def invalidate_product_cache(product_id):
  product = Product.objects.get(id=product_id)

  invalidate_cache('public_product_header',
                   product.id, product.is_approved, product.is_sold)

  invalidate_cache('public_product_content',
                   product.id, product.is_approved, product.is_sold,
                   product.is_recently_sold)

  invalidate_cache('public_product_extras',
                   product.id)

@postpone
def invalidate_seller_cache(seller_id):
  seller = Seller.objects.get(id=seller_id)

  invalidate_cache('public_store_header', seller.id, seller.updated_at)
  invalidate_cache('public_store_content', seller.id, seller.updated_at)

@postpone
def rebuildRankings():
  from apps.public.controller.product_ranking import updateRankings

  products = Product.objects.filter(sold_at=None,
                                    approved_at__lte=timezone.now(),
                                    active_at__lte=timezone.now(),
                                    seller__approved_at__lte=timezone.now(),
                                    seller__deactive_at=None,
                                    deactive_at=None)

  for product in products:
    try:
      updateRankings(product, except_ratings=True)
    except:
      updateRankings(product)
