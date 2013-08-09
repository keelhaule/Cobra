from django import template
register = template.Library()

@register.inclusion_tag('home/home_header.html')
def home_header_tag(request, style): #style options: full, mini, mobile
  (full, mini, mobile) = (False, False, False)

  if style == 'full':
    full = True
  elif style == 'mini':
    mini = True
  elif style == 'mobile':
    mobile = True

  return {'request':request, 'full': full, 'mini':mini, 'mobile':mobile}

@register.inclusion_tag('home/product.html')
def product_tag(product, sans_artisan=False):
  #photos
  product.photos = product.photo_set.order_by('rank').all()

  #artisan information
  if not sans_artisan:
    try: product.artisan = product.assets.filter(ilk='artisan')[0]
    except:pass

  context = {'product': product}
  return context

@register.inclusion_tag('home/search_bar.html')
def search_bar_tag(search_keywords=None):
  from apps.admin.models import Category, Color, Country

  #these should be cached queries!!
  colors = Color.objects.all()
  categories = Category.objects.all()
  countries = Country.objects.all()
  #cached queries!

  context = {
    'colors':colors,
    'categories':categories,
    'countries':countries,
    'search_keywords':search_keywords
  }
