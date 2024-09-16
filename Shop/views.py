from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json


# Create your views here.
def index(request):
    # # return HttpResponse("Index Shop")
    # product = Product.objects.all()
    # print(product)
    # n = len(product)
    # nSlides = n//4 + ceil((n/4) - (n//4))

    allProds = []
    catprods = Product.objects.values("category", "id")
    cats = {item["category"] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    # param = {'no_of_slides': nSlides, 'range': range(1, nSlides), 'product': product}
    # allProds = [[product, range(1, nSlides), nSlides], [product, range(1, nSlides), nSlides]]
    param = {"allProds": allProds}
    return render(request, "Shop/home.html", param)


def about(request):
    # return HttpResponse("We are at about")
    return render(request, "Shop/about.html")


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")
        desc = request.POST.get("desc", "")
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, "Shop/contact.html", {'thank': thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get("orderId", "")
        email = request.POST.get("email", "")
        
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:        
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status": "noitem"}')

        except Exception as e:
            return HttpResponse('{"status": "error"}')
    return render(request, "Shop/tracker.html")

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values("category", "id")
    cats = {item["category"] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    param = {"allProds": allProds, "msg": ""}

    if len(allProds) == 0 or len(query) < 4:
        param = {'msg': "Please make sure to enter relevant search query"}
        
    return render(request, "Shop/search.html", param)


def productView(request, myid):
    # Fetch the products using id
    product = Product.objects.filter(id=myid)

    return render(request, "Shop/prodView.html", {"product": product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get("itemsJson", "")
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        address = request.POST.get("address1", "") + "" + request.POST.get("address2", "")
        city = request.POST.get("city", "")
        state = request.POST.get("state", "")
        zip_code = request.POST.get("zip_code", "")
        phone = request.POST.get("phone", "")
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone,
        )
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id=order.order_id
        return render(request, "Shop/checkout.html", {"thank": thank, 'id': id})
    return render(request, "Shop/checkout.html")
