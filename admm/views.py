from django.utils.dateparse import parse_datetime
import random
from django.views import generic
from .models import *
from django.shortcuts import render,redirect,get_object_or_404,get_list_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.forms.models import model_to_dict
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.apps import apps
from django.http import request, HttpRequest
from .forms import *
from django.db.models import Max,Sum
from django.core.mail import send_mail
from reportlab.pdfgen import canvas
import io
from django.http import FileResponse,JsonResponse
import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# Create your views here.


# def index(request):
#     return render(request,'admm/index.html')
# def detail(request):
#     all_adv=Advertisement._check_fields
#     adObj=Advertisement()
#     return render(request,'admm/detailPage.html')

# def getQueryString(request):
#    super.tmp= request.GET.get('objname', 'Area')

# def show(request,object_id):
#     object=FooForm(data=model_to_dict(Foo.objects.get(pk=object_id)))
#     return render_toresponse()
# def login(request):
#     return render(request,'admm/loginPage.html')
@login_required
def subCatInit(request):
    cat = Category.objects.get(id=int(request.GET.get('id')))
    subCats = list(cat.subcategory_set.values('id', 'subcatname','commission'))
    # print(subCats)
    # data=serializers.serialize('json',subCats)
    # print('heythere')
    data={
        'subCats':subCats,
        'catid':cat.id,
    }
    # print(data)
    return JsonResponse(data)

@login_required
def validateCoupon(request):
    cpn=request.GET.get('coupon')
    print(cpn)
    print('hey')
    try:
        Coupondetail.objects.get(couponcode=str(cpn))
        msg='succeed'
        messages.info(request,msg)
    except ObjectDoesNotExist:
        msg='not succeed'
        messages.info(request,msg)
    data={
        'msg':msg
    }
    return JsonResponse(data)

@login_required
def commission(request):
    # Order.objects.filter(orderdatetime=datetime.datetime.now())
    return render(request,'admm/cmishan.html')
#//Userr side here to..

@login_required
def cart(request):
    cartAdvs=Cartdetail.objects.filter(auth_user=get_object_or_404(User,email=request.user.email))
    # listOfAdv=[]
    # for adv in cartAdvs:
    #     listOfAdv.append(str(adv.id))
    # for adv in cartAdvs:
    #     cartAdvs['dwps']=(adv.id.durationwisepricing_set.all())
    # context=Cartdetail.advertisement_set.filter(auth_user=get_object_or_404(User,email=request.user.email))
    return render(request,'admm/cart.html',context={'cartAdvs':cartAdvs})

@login_required
def cartAdvRemove(request,pk):
    cartAdv=Cartdetail.objects.get(id=int(pk))
    cartAdv.delete()
    return redirect('admm:cart')

@login_required
def saveCart(request,cnt):
    for i in range(1,cnt+1):
        adv=get_object_or_404(Cartdetail,id=int(request.POST['adv'+str(i)]))
        adv.startdate=request.POST['sdate'+str(i)]
        adv.enddate=request.POST['edate'+str(i)]
        adv.price=request.POST['price'+str(i)]
        adv.save()
    return redirect('admm:ordrSummery')

@login_required
def ordrSummery(request):
    cartAdvs = Cartdetail.objects.filter(auth_user=get_object_or_404(User, email=request.user.email))
    return render(request,'admm/ordrSummery.html',{'cartAdvs':cartAdvs})

@login_required
def saveOrdr(request):
    objTmp = Order.objects.aggregate(Max('id'))
    if objTmp['id__max'] == None:
        objTmp['id__max'] = 0
    newOrdr = Order(id=objTmp['id__max'] + 1,auth_user=User.objects.get(email=request.user.email),orderdatetime=datetime.datetime.now(),emipayment=0,gst_amount=0)
    newOrdr.save()
    ordrdAdvList=[]
    lst=(request.POST['advIdList']).split(' ')
    for advId in lst:
        if advId is not '':
            ordrdAdvList.append(Cartdetail.objects.get(id=int(advId)))
    for adv in ordrdAdvList:
        newOrdrDtl=Orderdetails(id=newOrdr,advertisement_advid=adv.id,advprice=adv.price,advstartdate=adv.startdate,advenddate=adv.enddate)
        newOrdrDtl.save(force_insert=True)
    return redirect('admm:list_orders')
#..here//

@login_required
def reportBasicView(request):
    buffer=io.BytesIO()
    p=canvas.Canvas(buffer)
    p.drawString(100,100,'hello world!')
    p.setTitle('titleBabe')
    p.drawCentredString(500,500,'Title')
    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer,as_attachment=False,filename='hell.pdf')

@login_required
def adminprofile(request):
    # request.user.get_deferred_fields()
    return render(request,'admm/profile.html')

def newPwd(request):
    isFrgt=int(request.POST.get('isFromFrgtPage',default=0))
    try:
        usr = User.objects.get(email=request.POST['email'],secque=request.POST['secque'],secqans=request.POST['secans'])
        # if request.user.password==request.POST['passwrd'] & usr.secque== & usr.secqans==:
        if usr is not None:
            if isFrgt==0:
                return render(request, 'login/newPwd.html')
            else:
                send_mail(
                    'BC Apu',
                    "Tya su kare chhe??!!!!",
                    'seeyouatthetop42@gmail.com',
                    [request.POST['email']],
                    fail_silently=False
                )
                return render(request,'login/emailOTP.html')
    except ObjectDoesNotExist:
        messages.info(request,'Invalid credentials.')
    if isFrgt==1:
        return redirect('login:frgtPwd')
    return redirect('login:chngPwd')

@login_required
def listOrders(request):
    flag = int(request.POST.get('srvdOnes', default=0))
    # objects = Order.objects.all()
    # if flag == 1:
    #
    #     ordrObjects=Order.objects.all()
    # elif flag == 0:
    ordrObjects = Order.objects.all()
    lst_ordrObjects = []
    if flag == 0:
        for ordr in ordrObjects:
            if ordr.orderdetails_set.filter(served=0,cancellationdatetime=None).count() == 0 :
                continue
            ordr.totalAmnt = (Orderdetails.objects.filter(id=ordr,cancellationdatetime=None).aggregate(Sum('advprice')))['advprice__sum']
            ordr.noOfAdvs = Orderdetails.objects.filter(id=ordr,cancellationdatetime=None).count
            lst_ordrObjects.append(ordr)
    elif flag == 1:
        for ordr in ordrObjects:
            if ordr.orderdetails_set.filter(served=1,cancellationdatetime=None).count() == ordr.orderdetails_set.all().count() :
                ordr.totalAmnt = (Orderdetails.objects.filter(id=ordr,cancellationdatetime=None).aggregate(Sum('advprice')))['advprice__sum']
                ordr.noOfAdvs = Orderdetails.objects.filter(id=ordr,cancellationdatetime=None).count
                lst_ordrObjects.append(ordr)
    return render(request,'admm/orderList.html',{'ordrObjects':lst_ordrObjects,'flagIsSrvd':flag})

@login_required
def listCncldOrdrs(request):
    flag=int(request.POST.get('flagRforN',default = 0))
    objects=None
    if flag==1:
        objects=Orderdetails.objects.filter(~Q(cancellationdatetime=None),~Q(refundedamount=None))
    elif flag==0:
        objects = Orderdetails.objects.filter(~Q(cancellationdatetime=None),refundedamount=None)

    # lst_ordrObjects = []
    # for ordr in objects:
    #     if ordr.orderdetails_set.filter(cancellationdatetime=None).count() == 0:
    #         # lst_ordrObjects.remove(ordr)
    #         continue
    #     ordr.totalAmnt = (Orderdetails.objects.filter(id=ordr, cancellationdatetime=None).aggregate(Sum('advprice')))[
    #         'advprice__sum']
    #     ordr.noOfAdvs = Orderdetails.objects.filter(id=ordr, cancellationdatetime=None).count
    #     lst_ordrObjects.append(ordr)
    # for ordr in objects:
        # odrDtls=Orderdetails.objects.all()
        # for odr_dtl in odrDtls:
        #     odr_dtl.cancellationofordadv_set.all()
        # ordr.oId=oIds.id

    # print(Objects)
    # for ordr in Objects:
    #     for odtl in ordr.orderdetails_set.all():
    #         ordr.ordrId = (Order.objects.get(id=odtl.id[0],advertisement_advid=ordr.advrtid[0]))
    return render(request, 'admm/cncldOdrList.html', {'Objects': objects,'flagRforNot':flag})

@login_required
def saveRefnd(request):
    obj=Orderdetails.objects.get(id=int(request.POST['odrId']),advertisement_advid=int(request.POST['advId']))
    obj.refundedamount=request.POST['refndAmnt']
    obj.paymentdatetime=datetime.datetime.now()
    obj.paymentrefid=random.randint(a=0,b=9999999999)
    obj.save()
    return redirect('admm:list_cncld_odrs')

@login_required
def ordr_detail(request,pk):
    ordrObj=get_object_or_404(Order,id=int(pk))
    ordrAdvs=Orderdetails.objects.filter(id=ordrObj)
    return render(request, 'admm/orderDetail.html', {'ordrObj': ordrObj,'ordrAdvs':ordrAdvs})

# def cnclordr_detail(request,pk):
#     ordrObj=get_object_or_404(Order,id=int(pk))
#     ordrAdvs=Cancellationofordadv.objects.filter(id=ordrObj)
#     return render(request, 'admm/orderDetail.html', {'ordrObj': ordrObj,'ordrAdvs':ordrAdvs})

@login_required
def coupon_detail(request,pk):
    return  render(request, 'admm/couponDetail.html', {'cpnObj': Coupondetail.objects.get(id=pk)})

# @login_required
class CouponLstOrAdd(View):
    def get(self, request):
        if request.user.is_authenticated:
            cpnObjects=None
            lst=[]
            flag=int(request.GET.get('actvOnes',default=1))
            if flag == 1:#active
                cpnObjects= Coupondetail.objects.filter(couponenddate__gte=datetime.date.today())
                for cpnObj in cpnObjects:
                    if cpnObj.order_set.all().count()==0:
                        lst.append(cpnObj)
            elif flag == 0:#used
                cpnObjects = Coupondetail.objects.all()
                for cpnObj in cpnObjects:
                    if cpnObj.order_set.all().count() == 1 or cpnObj.couponenddate<datetime.date.today():
                        lst.append(cpnObj)
            # elif flag == 2:#expired
            #     cpnObjects = Coupondetail.objects.filter(couponenddate__lt=datetime.datetime.now())
            #     for cpnObj in cpnObjects:
            #         if cpnObj.order_set.all().count() == 1:
            #             lst.append(cpnObj)
            buyers=User.objects.filter(userroleid=3)
            cpn_form = CouponForm(instance=Coupondetail())
            template = 'admm/couponListOrCreate.html'
            context = {'cpn_form': cpn_form,'lst':lst,'buyers':buyers,'flag':flag}#,'usrObjects':usrObjects}#, 'cart_forms': cart_forms}
            return render(request, template, context)
        else:
            return redirect('login:log_in')

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login:log_in')
        cpn_form = CouponForm(request.POST, instance=Coupondetail())
        if cpn_form.is_valid():# and all([cart_form.is_valid() for cart_form in cart_forms]):
            new_cpn = cpn_form.save(commit=False)
            # objTmp = Coupondetail.objects.aggregate(Max('id'))
            # if objTmp['id__max'] == None:
            #     objTmp['id__max'] = 0
            # new_cpn.id = objTmp['id__max'] + 1
            # new_cpn.couponcode=request.POST['code']
            # new_cpn.coupondescription = request.POST['desc']
            # new_cpn.coupondiscount = int(request.POST['discount'])
            # new_cpn.couponstartdate = request.POST['sdate']
            # new_cpn.couponenddate = request.POST['edate']
            # new_cpn.mincartvalue = int(request.POST['minval'])
            # new_cpn.auth_user = User.objects.get(id=int(request.POST['usr']))
            new_cpn.auth_user=User.objects.get(id=int(request.POST['byrId']))
            new_cpn.couponcode=request.POST['cpnCode']
            new_cpn.save()
            return redirect("admm:couponsListOrAdd")
        cpnObjects= Coupondetail.objects.all()
        messages.info(request,'Something bad happened..')
        context = {'cpn_form': cpn_form, 'cpnObjects': cpnObjects}
        return render(request, 'admm/couponListOrCreate.html', context)


@login_required
def listAdv(request):
    advObjs = []
    if request.user.is_staff==1:
        if request.method=='POST' and request.POST.get('isowned',default='1')=='0':
            # print('post here')
            OwnedOnes=False
            for usr in User.objects.filter(userroleid=2):
                for adv in Advertisement.objects.filter(auth_user=usr):
                    advObjs.append(adv)
        else:
            # print('coming')
            OwnedOnes=True
            for usr in User.objects.filter(is_staff=1):
                for adv in Advertisement.objects.filter(auth_user=usr):
                    advObjs.append(adv)

    else:
        advObjs=Advertisement.objects.filter(auth_user=User.objects.get(email=request.user.email))
        # if advObjs.length:
        # print(len(advObjs))

    return render(request,'admm/advList.html',{'advObjs':advObjs,'pipeAdv':'Advertisement','OwnedOnes':OwnedOnes})

@login_required
def adv_detail(request,pk):
    advObj=get_object_or_404(Advertisement,advid=pk)
    advImgObjects =Advimgs.objects.filter(id=advObj)
    priceObjects=Durationwisepricing.objects.filter(advertisement_advid=advObj)
    return render(request,'admm/advDetail.html',{'advObj':advObj,'advImgObjects':advImgObjects,'priceObjects':priceObjects,'catid':advObj.subcategory_subcatid.catid.id})

@login_required
def delAdv(request,pk):
    adv = Advertisement.objects.get(advid=pk)
    try:
        adv.delete()
        messages.info(request, "Advertisement deleted.")
        return redirect('admm:listadv')
    except:
        messages.info(request,"Can't delete advertisement, it's related to other orders..")
        return redirect('admm:listadv')

@login_required
def adv_edit(request,pk):
    advObj=get_object_or_404(Advertisement,advid=pk)
    advImgObjects = Advimgs.objects.filter(id=advObj)
    priceObjects = Durationwisepricing.objects.filter(advertisement_advid=advObj)
    areaObjects=Area.objects.all()
    cityObjects=City.objects.all()
    subCatObjects=Subcategory.objects.all()
    # indx=0
    return render(request,'admm/advEdit.html',{'advObj': advObj,
                                               'advImgObjects': advImgObjects,
                                               'priceObjects': priceObjects,
                                               'catid':advObj.subcategory_subcatid.catid.id,
                                               'areaObjects':areaObjects,
                                               'cityObjects': cityObjects,
                                               'subCatObjects':subCatObjects,})

@login_required
def adv_save(response,pk):
    advObj=get_object_or_404(Advertisement,advid=pk)
    if advObj.subcategory_subcatid.catid.id == 1:
        advObj.advregno = response.GET['regno']
        advObj.height = response.GET['height']
        advObj.width = response.GET['width']
        # advObj.maxdays = int(request.POST['maxdays'])
        advObj.addressline1 = response.GET['address']
        advObj.area_areaid = Area.objects.get(id=response.GET['area'])
        advObj.subcategory_subcatid = Subcategory.objects.get(id=response.GET['subcategory'])

    elif advObj.subcategory_subcatid.catid.id == 2:
        advObj.city_cityid = City.objects.get(id=response.GET('city'))
        advObj.minquantity = int(response.GET('min_qn'))
        advObj.stock = int(response.GET('stock'))

    priceObjects = Durationwisepricing.objects.filter(advertisement_advid=advObj)
    for priceObj in priceObjects:
        priceObj.delete()
    for i in range(1,int(response.GET['DWPcount'])+1):
        new_price=Durationwisepricing(advertisement_advid=advObj,noofdays=response.GET['day'+str(i)],price = response.GET['price' + str(i)])
        # new_price.noofdays=request.POST['day'+str(i)]
        new_price.save(force_insert=True)
    # i=1
    # for adimg in Advimgs.objects.filter(id=advObj):
    #     if adimg.adv_img == imgsListForDel[i]:
    #         adimg.delete()
    #     i+=1
    # for img in imgsListForDel:
    #     print(img)
    #     if img=='bingo':
    #         continue
    imgsListForDel=response.GET['imgsList'].split('?')
    for adimg in Advimgs.objects.filter(id=advObj):
        if str(adimg.adv_img) in imgsListForDel and str(adimg.adv_img) is not 'bingo':
            print('deleted'+str(adimg.adv_img))
            adimg.delete()

    for filename, file in response.FILES.items():
        # for i in range(adv_imgs_count):
        # print(filename)
        new_advimg = Advimgs(id=advObj, adv_img=file)
        # print(new_advimg.adv_img2)
        new_advimg.save(force_insert=True)

    if advObj.auth_user.is_staff==1:
        advObj.auth_user=User.objects.get(email=response.user.email)
    advObj.save()
    # return redirect('/adminsite/adv/'+str(advObj.advid))
    return redirect('admm:adv_save',pk=advObj.advid)

@login_required
def fdbckOrCmplntList(request,objname):
    if objname=='feedbacks':
        mdl=Orderfeedback
    elif objname=='complaints':
        mdl=Complaintdetail
    else:
        return redirect('/adminsite/buyers/responses/'+objname+'/')
    return render(request,'admm/fdbckOrCmplnt.html',{'object_list':(mdl.objects.all()).order_by('-datetime'),'objname':objname})

@login_required
def fdbkRcmplnt_save(request,isFdbk):
    if isFdbk==1:
        model=Orderfeedback
    else:
        model=Complaintdetail
    # dtime=datetime.datetime()
    # print(dtime)
    Complaintdetail.objects.all()
    Obj=model.objects.get(id=request.GET.get('id'),datetime=request.GET.get('dtime'))
    Obj.resDatetime=datetime.datetime.now()
    Obj.responsetext=request.GET.get('rspns')
    Obj.auth_user=User.objects.get(email=request.user.email)
    Obj.save()
    data={
        'msg':'done dana',
        'datetime':Obj.resDatetime,
        'rspns':Obj.responsetext,
    }
    return JsonResponse(data)

@login_required
def packOfferList(request,packOrOffr):
    if request.method=='GET':
        if packOrOffr=='package':
            object_list=Package.objects.all()
            isPack= 1
        elif packOrOffr=='offer':
            object_list=Offerdetail.objects.all()
            isPack = 0
        else:
            return redirect('/adminsite/'+packOrOffr+'/listing/')
        return render(request,'admm/packOfferList.html',{'object_list':object_list,'isPack':isPack,'packOffr':packOrOffr})

@login_required
def packOfferDetail(request,packOrOffr,pk):
    if packOrOffr=='package':
        mdl=Package
        subMdl=PackageHasAdv
    else:
        mdl = Offerdetail
        subMdl = Offercoveringadvs
    obj=get_object_or_404(mdl,id=int(pk))
    subObjs=subMdl.objects.filter(id=obj)
    return render(request, 'admm/packOrOfferDetail.html', {'obj': obj,'subObjs':subObjs,'packOffr':packOrOffr})

@login_required
def packOffrEdit(request,packOrOffr,pk):
    pass

@login_required
def packOffrDel(request,packOrOffr,pk):
    if packOrOffr == 'package':
        mdl=Package
    else:
        mdl=Offerdetail
    obj=mdl.objects.get(id=int(pk))
    obj.delete()
    return redirect('/adminsite/'+packOrOffr+'/listing/')

@login_required
def packOrOffer_create(request):
    if int(request.POST['isPack'])==1:
        mdl=Package
        mdl2=PackageHasAdv
        messages.info(request, 'Package created successfully!')
    else:
        mdl=Offerdetail
        mdl2 = Offercoveringadvs
        messages.info(request, 'Offer created successfully!')
    obj=mdl(description=request.POST['description'],startdate=request.POST['startdate'],enddate=request.POST['enddate'],discount=request.POST['discount'])
    objTmp = mdl.objects.aggregate(Max('id'))
    if objTmp['id__max'] == None:
        objTmp['id__max'] = 0
    obj.id = objTmp['id__max'] + 1
    obj.save()
    for i in range(1,(int(request.POST['selectedAdvCnt']))+1):
        packAdvObj=mdl2(id=obj,advertisement_advid=Advertisement.objects.get(advid=int(request.POST['selectedAdv'+str(i)])))
        if int(request.POST['isPack'])==1:
            packAdvObj.quantity=0
        packAdvObj.save(force_insert=True)
    return redirect('admm:listadv')

# @login_required
class randomObjAddView(CreateView):
    fields = []
    sai = 'dd'
    if 'df':
        model = Advertisement

    def get_queryset(self):
        if self.kwargs.get('objname') == 'Advertisement':
            model = Advertisement
        elif self.kwargs.get('objname') == 'Category':
            model = Category
        elif self.kwargs.get('objname') == 'Subcategory':
            model = Subcategory
        # elif self.kwargs.get('objname') == 'Userdetail':
        #     return Userdetail.objects.all()
        else:
            return Area.objects.all()

    # fields = ['advid', 'advregno', 'height', 'width', 'maxdays', 'minquantity', 'addressline1', 'area_areaid','city_cityid', 'stock', 'defaultimgpath', 'subcategory_subcatid', 'userdetail_userid', 'isowned']

# @login_required
class randomObjUpdView(UpdateView):
    fields = []

    def get_queryset(self):
        if self.kwargs.get('objname') == 'Advertisement':
            return Advertisement.objects.all()
        elif self.kwargs.get('objname') == 'Category':
            return Category.objects.all()
        elif self.kwargs.get('objname') == 'Subcategory':
            return Subcategory.objects.all()
        # elif self.kwargs.get('objname') == 'Userdetail':
        #     return Userdetail.objects.all()
        else:
            return Area.objects.all()
    # fields = ['advid', 'advregno', 'height', 'width', 'maxdays', 'minquantity', 'addressline1', 'area_areaid','city_cityid', 'stock', 'defaultimgpath', 'subcategory_subcatid', 'userdetail_userid', 'isowned']

# @login_required
class randomObjDelView(DeleteView):
    success_url = reverse_lazy('admm:randomObj-detail')

    def get_queryset(self):
        if self.kwargs.get('objname') == 'Advertisement':
            return Advertisement.objects.all()
        elif self.kwargs.get('objname') == 'Category':
            return Category.objects.all()
        elif self.kwargs.get('objname') == 'Subcategory':
            return Subcategory.objects.all()
        elif self.kwargs.get('objname') == 'User':
            return User.objects.all()
        else:
            return Area.objects.all()

# from django.forms.models import
# data = serializers.serialize('xml', Advertisement.objects.all())
# @login_required
class randomObjDetailView(generic.DetailView):
    # model=Advertisement
    template_name = 'admm/detail.html'

    # data = serializers.serialize('python', Advertisement.objects.all(),fields=('advid','defaultimgpath'))
    def get_queryset(self):
        if self.kwargs.get('objname') == 'Advertisement':
            return Advertisement.objects.all()
            # return Advertisement.objects.all()
            # return Advertisement.objects.filter(id=self.kwargs.get('pk')).values()
        # elif self.kwargs.get('objname') == 'Advimgs':
        #     return Advimgs.objects.all()
        elif self.kwargs.get('objname') == 'Area':
            return Area.objects.all()
        elif self.kwargs.get('objname') == 'User':
            return User.objects.all()
        elif self.kwargs.get('objname') == 'Branch':
            return Branch.objects.all()
        # elif self.kwargs.get('objname') == 'Cancellationofordadv':
        #     return Cancellationofordadv.objects.all()
        elif self.kwargs.get('objname') == 'Cartdetail':
            return Cartdetail.objects.all()
        elif self.kwargs.get('objname') == 'Category':
            return Category.objects.all()
        elif self.kwargs.get('objname') == 'City':
            return City.objects.all()
        elif self.kwargs.get('objname') == 'Commissiondetail':
            return Commissiondetail.objects.all()
        elif self.kwargs.get('objname') == 'Company':
            return Company.objects.all()
        elif self.kwargs.get('objname') == 'Complaintdetail':
            return Complaintdetail.objects.all()
        elif self.kwargs.get('objname') == 'Country':
            return Country.objects.all()
        elif self.kwargs.get('objname') == 'Coupondetail':
            return Coupondetail.objects.all()
        elif self.kwargs.get('objname') == 'Durationwisepricing':
            return Durationwisepricing.objects.all()
        elif self.kwargs.get('objname') == 'Offercoveringadvs':
            return Offercoveringadvs.objects.all()
        elif self.kwargs.get('objname') == 'Offerdetail':
            return Offerdetail.objects.all()
        elif self.kwargs.get('objname') == 'Order':
            return Order.objects.all()
        elif self.kwargs.get('objname') == 'Orderfeedback':
            return Orderfeedback.objects.all()
        elif self.kwargs.get('objname') == 'Orderpayment':
            return Orderpayment.objects.all()
        elif self.kwargs.get('objname') == 'Orderdetails':
            return Orderdetails.objects.all()
        elif self.kwargs.get('objname') == 'Package':
            return Package.objects.all()
        elif self.kwargs.get('objname') == 'PackageHasAdv':
            return PackageHasAdv.objects.all()
        elif self.kwargs.get('objname') == 'Sellerdocdetail':
            return Sellerdocdetail.objects.all()
        elif self.kwargs.get('objname') == 'Sellerdoclist':
            return Sellerdoclist.objects.all()
        elif self.kwargs.get('objname') == 'State':
            return State.objects.all()
        elif self.kwargs.get('objname') == 'Subcategory':
            return Subcategory.objects.all()
        elif self.kwargs.get('objname') == 'Updationinorder':
            return Updationinorder.objects.all()
        elif self.kwargs.get('objname') == 'Userrole':
            return Userrole.objects.all()
        elif self.kwargs.get('objname') == 'Wishlistdetail':
            return Wishlistdetail.objects.all()
        else:
            return Area.objects.all()

    def get_context_data(self, **kwargs):
        if self.kwargs.get('objname') == 'Advertisement':
            advobject = model_to_dict(Advertisement.objects.get(advid=self.kwargs.get('pk')))
            modelName = Advertisement
            priceobjects=Durationwisepricing.objects.filter(advertisement_advid=self.kwargs.get('pk'))
            #super.queryset(randomObjDetailView, self).get_context_data()=Advertisement.objects.all()
            return {'object': advobject, 'priceobj':priceobjects,'modelName': modelName, 'spk': self.kwargs.get('pk')}
            # return Advertisement.objects.all()
            # return Advertisement.objects.filter(id=self.kwargs.get('pk')).values()
        # elif self.kwargs.get('objname') == 'Advimgs':
        #     objects = Advimgs.objects.filter(id=self.kwargs.get('pk'))
        #     modelName = Advimgs
        #     return {'advimg_objects': objects, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
            # return Category.objects.all()
        elif self.kwargs.get('objname') == 'Area':
            object = model_to_dict(Area.objects.get(id=self.kwargs.get('pk')))
            modelName = Area
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'User':
            object = model_to_dict(User.objects.get(id=self.kwargs.get('pk')))
            modelName = User
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Branch':
            object = model_to_dict(Branch.objects.get(id=self.kwargs.get('pk')))
            modelName = Branch
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        # elif self.kwargs.get('objname') == 'Cancellationofordadv':
        #     object = model_to_dict(Cancellationofordadv.objects.get(id=self.kwargs.get('pk')))
        #     modelName = Cancellationofordadv
        #     return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Cartdetail':
            object = model_to_dict(Cartdetail.objects.get(id=self.kwargs.get('pk')))
            modelName = Cartdetail
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Category':
            object = model_to_dict(Category.objects.get(id=self.kwargs.get('pk')))
            modelName = Category
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'City':
            object = model_to_dict(City.objects.get(id=self.kwargs.get('pk')))
            modelName = City
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Commissiondetail':
            object = model_to_dict(Commissiondetail.objects.get(id=self.kwargs.get('pk')))
            modelName = Commissiondetail
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Company':
            object = model_to_dict(Company.objects.get(id=self.kwargs.get('pk')))
            modelName = Company
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Complaintdetail':
            object = model_to_dict(Complaintdetail.objects.get(id=self.kwargs.get('pk')))
            modelName = Complaintdetail
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Country':
            object = model_to_dict(Country.objects.get(id=self.kwargs.get('pk')))
            modelName = Country
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Coupondetail':
            object = model_to_dict(Coupondetail.objects.get(id=self.kwargs.get('pk')))
            modelName = Coupondetail
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Durationwisepricing':
            object = model_to_dict(Durationwisepricing.objects.get(id=self.kwargs.get('pk')))
            modelName = Durationwisepricing
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Offercoveringadvs':
            object = model_to_dict(Offercoveringadvs.objects.get(id=self.kwargs.get('pk')))
            modelName = Offercoveringadvs
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Offerdetail':
            object = model_to_dict(Offerdetail.objects.get(id=self.kwargs.get('pk')))
            modelName = Offerdetail
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Order':
            object = model_to_dict(Order.objects.get(id=self.kwargs.get('pk')))
            modelName = Order
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Orderfeedback':
            object = model_to_dict(Orderfeedback.objects.get(id=self.kwargs.get('pk')))
            modelName = Orderfeedback
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Orderpayment':
            object = model_to_dict(Orderpayment.objects.get(id=self.kwargs.get('pk')))
            modelName = Orderpayment
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Orderdetails':
            object = model_to_dict(Orderdetails.objects.get(id=self.kwargs.get('pk')))
            modelName = Orderdetails
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Package':
            object = model_to_dict(Package.objects.get(id=self.kwargs.get('pk')))
            modelName = Package
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'PackageHasAdv':
            object = model_to_dict(PackageHasAdv.objects.get(id=self.kwargs.get('pk')))
            modelName = PackageHasAdv
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Sellerdocdetail':
            object = model_to_dict(Sellerdocdetail.objects.get(id=self.kwargs.get('pk')))
            modelName = Sellerdocdetail
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Sellerdoclist':
            object = model_to_dict(Sellerdoclist.objects.get(id=self.kwargs.get('pk')))
            modelName = Sellerdoclist
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'State':
            object = model_to_dict(State.objects.get(id=self.kwargs.get('pk')))
            modelName = State
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Subcategory':
            object = model_to_dict(Subcategory.objects.get(id=self.kwargs.get('pk')))
            modelName = Subcategory
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Updationinorder':
            object = model_to_dict(Updationinorder.objects.get(id=self.kwargs.get('pk')))
            modelName = Updationinorder
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Userrole':
            object = model_to_dict(Userrole.objects.get(id=self.kwargs.get('pk')))
            modelName = Userrole
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        elif self.kwargs.get('objname') == 'Wishlistdetail':
            object = model_to_dict(Wishlistdetail.objects.get(id=self.kwargs.get('pk')))
            modelName = Wishlistdetail
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
        else:
            object = model_to_dict(Area.objects.get(id=self.kwargs.get('pk')))
            modelName = Area
            return {'object': object, 'modelName': modelName, 'spk': self.kwargs.get('pk')}
    # tmp = ""
    # HttpRequest.GET.get
    # def get_object(self, queryset=None):
    #     pk=self.kwargs.get('pk')
    #     if self.kwargs.get('objname')=='Advertisement':
    #         return self.get_object(Advertisement)
    #     elif self.kwargs.get('objname')=='Category':
    #         return self.get_object(Category)
    #     elif self.kwargs.get('objname')=='Userdetail':
    #         return self.get_object(Userdetail)
    #     return self.get_object(Area)
    # tmp='Advertisement'
    # q = "<class 'admm.models." +  + "'>"
    # mdls = apps.get_app_config('admm').get_models()
    # for mdl in mdls:
    #     if q == str(mdl):
    #         model = mdl

@login_required
def index(request):
        # mdlLst = ['Advertisement', 'Advimgs', 'Area', 'User', 'Branch', 'Cancellationofordadv', 'Cartdetail',
        #           'Category', 'City', 'Commissiondetail', 'Company', 'Complaintdetail', 'Country', 'Coupondetail',
        #           'Durationwisepricing', 'Offercoveringadvs', 'Offerdetail', 'Order', 'Orderfeedback', 'Orderpayment',
        #           'Orderdetails', 'Package', 'PackageHasAdv', 'Sellerdocdetail', 'Sellerdoclist', 'State', 'Subcategory',
        #           'Updationinorder', 'Userrole', 'Wishlistdetail']
        catCnt=Category.objects.count()
        admins=User.objects.filter(userroleid=Userrole.objects.get(roleid=1))
        advOwnd=0
        for admin in admins:
            advOwnd += admin.advertisement_set.count()
        advTtl=Advertisement.objects.count()
        areas=Area.objects.all().count
        cities=City.objects.all().count
        states=State.objects.all().count
        countries=Country.objects.all().count
        buyers=User.objects.filter(userroleid=Userrole.objects.get(roleid=3)).count
        sellers=User.objects.filter(userroleid=Userrole.objects.get(roleid=2)).count
        packsTtl=Package.objects.all().count
        packsAdm=Package.objects.filter().count
        cpnListAdtv=[]
        cpnObjects= Coupondetail.objects.filter(couponenddate__gte=datetime.date.today())
        cpnsTtl=Coupondetail.objects.all().count()
        for cpnObj in cpnObjects:
            if cpnObj.order_set.all().count() == 0:
                cpnListAdtv.append(cpnObj)
        cpnListAdtv=len(cpnListAdtv)

        odrsTtl=Order.objects.all().count()
        todayDateTime=datetime.datetime.today().replace(hour=0,minute=0,second=0)
        odrsTdy=Order.objects.filter(orderdatetime__gte=todayDateTime,orderdatetime__lte=todayDateTime.replace(hour=23,minute=59,second=59)).count()
        todayDate=datetime.date.today().replace(day=1)
        # print(todayDate)
        # print(todayDate.replace(month=int(todayDate.month)+1))
        odrsThisMnth=Order.objects.filter(orderdatetime__gte=todayDate,orderdatetime__lt=todayDate.replace(month=int(todayDate.month)+1)).count()
        return render(request, 'admm/index.html',{
            'pipeHome':'Home',
            'advSlrs':advTtl-advOwnd,'advOwnd':advOwnd,'advTtl':advTtl,
            'catCnt':catCnt,'scatCnt':Subcategory.objects.count(),
            'areas':areas,'cities':cities,'states':states,'countries':countries,
            'buyers':buyers,'sellers':sellers,'admins':admins.count(),
            'cpnsActv':cpnListAdtv,'cpnsTtl':cpnsTtl,'usedORexpired':cpnsTtl-cpnListAdtv,
            'odrsTtl':odrsTtl,'odrsThisMnth':odrsThisMnth,'odrsTdy':odrsTdy
        })

# class Tables(generic.DetailView):

# def tables(request):
#     mdlLst=['Advertisement','Advimgs','Area','User','Branch','Cancellationofordadv','Cartdetail','Category','City','Commissiondetail','Company','Complaintdetail','Country','Coupondetail','Durationwisepricing','Offercoveringadvs','Offerdetail','Order','Orderfeedback','Orderpayment','Orderdetails','Package','PackageHasAdv','Sellerdocdetail','Sellerdoclist','State','Subcategory','Updationinorder','Userrole','Wishlistdetail']
#     return render(request,'admm/index.html',{'mdlLst':mdlLst})

# class Tables(generic.Vi):
#     template_name = 'admm/tables.html'
#     # model = Advertisement
#     def get_context_data(self, **kwargs):
#         mdls = apps.get_app_config('admm').get_models()
#         mdlList=[]
#         for mdl in mdls:
#             mdlList.append(mdl.__name__)
#         return {'mdlList':mdlList,'Gm':'Good Morning'}
# @login_required
class List(generic.ListView):
    template_name = 'admm/list-view.html'

    def get_queryset(self):
        if self.kwargs['objname'] == 'Advertisement':
            # object_list_here2 = model_to_dict(Advertisement.objects.get(advid=self.kwargs.get('pk')))
            # return {'objects':objects,'object_list_here2':object_list_here2}
            return Advertisement.objects.all()
        elif self.kwargs['objname'] == 'advimgs':
            # object_list_here2 = model_to_dict(Advertisement.objects.get(advid=self.kwargs.get('pk')))
            # return {'objects':objects,'object_list_here2':object_list_here2}
            return Advimgs.objects.all()
        elif (self.kwargs['objname'] == 'Category'):
            # objectsHere = Category.objects.all()
            # object_list_here2 = model_to_dict(Category.objects.get(categoryid=self.kwargs.get('pk')))
            # return {'objects': objects, 'object_list_here2': object_list_here2}
            return Category.objects.all()
        elif (self.kwargs['objname'] == 'Offerdetail'):
            objects = Offerdetail.objects.all()
            return objects
        elif self.kwargs['objname'] == 'Package':
            objects = Package.objects.all()
            return objects
        elif (self.kwargs['objname'] == 'Coupondetail'):
            objects = Coupondetail.objects.all()
            return objects
        elif (self.kwargs['objname'] == 'Order'):
            objectsHere = Order.objects.all()
            return objectsHere
        elif (self.kwargs['objname'] == 'Orderfeedback'):
            objects = Orderfeedback.objects.all()
            return objects
        elif (self.kwargs['objname'] == 'Complaintdetail'):
            return Complaintdetail.objects.all()
        elif (self.kwargs['objname'] == 'User'):
            return User.objects.all()
        elif (self.kwargs['objname'] == 'User'):
            return User.objects.all()
        elif (self.kwargs['objname'] == 'Area'):
            return Area.objects.all()
        else:
            return Area.objects.all()

    def get_context_data(self, **kwargs):
        if self.kwargs['objname'] == 'Advertisement':
            # object = model_to_dict(Advertisement.objects.get(advid=self.kwargs.get('pk')))
            modelName = Advertisement
            objectList = []
            for obj in Advertisement.objects.all():
                objectList.append(model_to_dict(obj))
            # objects=model_to_dict(Advertisement.objects.all(),excludde='_meta') #,fields=['advid','advregno','height','width','maxdays','minquantity','addressline1','area_areaid','city_cityid','stock','defaultimgpath','subcatid','auth_user'])
            return {'objectList': objectList, 'modelName': modelName}#, 'spk': self.kwargs.get('pk')}
            # return Advertisement.objects.all()
            # return Advertisement.objects.filter(id=self.kwargs.get('pk')).values()
        elif (self.kwargs['objname'] == 'advimgs'):
            # object = model_to_dict(Advimgs.objects.get(d=self.kwargs.get('pk')))
            modelName = Advimgs
            objectList = []
            for obj in Advimgs.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Advimgs.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Area'):
            # object = model_to_dict(Area.objects.get(d=self.kwargs.get('pk')))
            modelName = Area
            objectList = []
            for obj in Area.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Area.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Branch'):
            # object = model_to_dict(Branch.objects.get(d=self.kwargs.get('pk')))
            modelName = Branch
            objectList = []
            for obj in Branch.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Branch.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Order'):
            # object = model_to_dict(Order.objects.get(d=self.kwargs.get('pk')))
            modelName = Order
            objectList = []
            for obj in Order.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Order.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Orderdetails'):
            # object = model_to_dict(Orderdetails.objects.get(d=self.kwargs.get('pk')))
            modelName = Orderdetails
            objectList = []
            for obj in Orderdetails.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Orderdetails.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        # elif (self.kwargs['objname'] == 'Cancellationofordadv'):
        #     # object = model_to_dict(Cancellationofordadv.objects.get(d=self.kwargs.get('pk')))
        #     modelName = Cancellationofordadv
        #     objectList = []
        #     for obj in Cancellationofordadv.objects.all():
        #         objectList.append(model_to_dict(obj))
        #     # objects = Cancellationofordadv.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Cartdetail'):
            # object = model_to_dict(Cartdetail.objects.get(d=self.kwargs.get('pk')))
            modelName = Cartdetail
            objectList = []
            for obj in Cartdetail.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Cartdetail.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Category'):
            # object = model_to_dict(Category.objects.get(d=self.kwargs.get('pk')))
            modelName = Category
            objectList = []
            for obj in Category.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Category.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'City'):
            # object = model_to_dict(City.objects.get(d=self.kwargs.get('pk')))
            modelName = City
            objectList = []
            for obj in City.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = City.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Commissiondetail'):
            # object = model_to_dict(Commissiondetail.objects.get(d=self.kwargs.get('pk')))
            modelName = Commissiondetail
            objectList = []
            for obj in Commissiondetail.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Commissiondetail.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Company'):
            # object = model_to_dict(Company.objects.get(d=self.kwargs.get('pk')))
            modelName = Company
            objectList = []
            for obj in Company.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Company.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Country'):
            # object = model_to_dict(Country.objects.get(d=self.kwargs.get('pk')))
            modelName = Country
            objectList = []
            for obj in Country.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Country.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Complaintdetail'):
            # object = model_to_dict(Complaintdetail.objects.get(d=self.kwargs.get('pk')))
            modelName = Complaintdetail
            objectList = []
            for obj in Complaintdetail.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Complaintdetail.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Durationwisepricing'):
            # object = model_to_dict(Durationwisepricing.objects.get(d=self.kwargs.get('pk')))
            modelName = Durationwisepricing
            objectList = []
            for obj in Durationwisepricing.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Durationwisepricing.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Offercoveringadvs'):
            # object = model_to_dict(Offercoveringadvs.objects.get(d=self.kwargs.get('pk')))
            modelName = Offercoveringadvs
            objectList = []
            for obj in Offercoveringadvs.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Offercoveringadvs.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Offerdetail'):
            # object = model_to_dict(Offerdetail.objects.get(d=self.kwargs.get('pk')))
            modelName = Offerdetail
            objectList = []
            for obj in Offerdetail.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Offerdetail.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Orderfeedback'):
            # object = model_to_dict(Orderfeedback.objects.get(d=self.kwargs.get('pk')))
            modelName = Orderfeedback
            objectList = []
            for obj in Orderfeedback.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Orderfeedback.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Orderpayment'):
            # object = model_to_dict(Orderpayment.objects.get(d=self.kwargs.get('pk')))
            modelName = Orderpayment
            objectList = []
            for obj in Orderpayment.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Orderpayment.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Package'):
            # object = model_to_dict(Package.objects.get(d=self.kwargs.get('pk')))
            modelName = Package
            objectList = []
            for obj in Package.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Package.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'PackageHasAdv'):
            # object = model_to_dict(Packagehasadv.objects.get(d=self.kwargs.get('pk')))
            modelName = PackageHasAdv
            objectList = []
            for obj in PackageHasAdv.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Packagehasadv.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Sellerdocdetail'):
            # object = model_to_dict(Sellerdocdetail.objects.get(d=self.kwargs.get('pk')))
            modelName = Sellerdocdetail
            objectList = []
            for obj in Sellerdocdetail.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Sellerdocdetail.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Sellerdoclist'):
            # object = model_to_dict(Sellerdoclist.objects.get(d=self.kwargs.get('pk')))
            modelName = Sellerdoclist
            objectList = []
            for obj in Sellerdoclist.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Sellerdoclist.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'State'):
            # object = model_to_dict(State.objects.get(d=self.kwargs.get('pk')))
            modelName = State
            objectList = []
            for obj in State.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = State.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Subcategory'):
            # object = model_to_dict(Subcategory.objects.get(d=self.kwargs.get('pk')))
            modelName = Subcategory
            objectList = []
            for obj in Subcategory.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Subcategory.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Updationinorder'):
            # object = model_to_dict(Updationinorder.objects.get(d=self.kwargs.get('pk')))
            modelName = Updationinorder
            objectList = []
            for obj in Updationinorder.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Updationinorder.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'User'):
            # object = model_to_dict(User.objects.get(d=self.kwargs.get('pk')))
            modelName = User
            objectList = []
            for obj in User.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = User.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Userrole'):
            # object = model_to_dict(Userrole.objects.get(d=self.kwargs.get('pk')))
            modelName = Userrole
            objectList = []
            for obj in Userrole.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Userrole.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        elif (self.kwargs['objname'] == 'Wishlistdetail'):
            # object = model_to_dict(Wishlistdetail.objects.get(d=self.kwargs.get('pk')))
            modelName = Wishlistdetail
            objectList = []
            for obj in Wishlistdetail.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Wishlistdetail.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

        else:
            modelName = Area
            objectList = []
            for obj in Area.objects.all():
                objectList.append(model_to_dict(obj))
            # objects = Wishlistdetail.objects.all()
            return {'objectList': objectList, 'modelName': modelName}  # , 'spk': self.kwargs.get('pk')}

# class AdvDetailView(generic.DetailView):
#     model=Advertisement
#     template_name = 'admm/detail.html'
# class CategoryDetailView(generic.DetailView):
#     model=Category
#     template_name = 'admm/detail.html'
# class AdvImgsDetailView(generic.DetailView):
#     model = Advimgs
#     template_name = 'admm/detail.html'
# class AreaDetailView(generic.DetailView):
#     model = Area
#     template_name = 'admm/detail.html'
# class BranchDetailView(generic.DetailView):
#     model = Branch
#     template_name = 'admm/detail.html'
# class CancellationsDetailView(generic.DetailView):
#     model = Cancellationofordadv
#     template_name = 'admm/detail.html'
# class CartDetailView(generic.DetailView):
#     model = Cartdetail
#     template_name = 'admm/detail.html'
# class CityDetailView(generic.DetailView):
#     model = City
#     template_name = 'admm/detail.html'
# class CommissionDetailView(generic.DetailView):
#     model = Commissiondetail
#     template_name = 'admm/detail.html'
# class CompanyDetailView(generic.DetailView):
#     model = Company
#     template_name = 'admm/detail.html'
# class CouponDetailView(generic.DetailView):
#     model = Coupondetail
#     template_name = 'admm/detail.html'
# class ComplaintDetailView(generic.DetailView):
#     model = Complaintdetail
#     template_name = 'admm/detail.html'
# class CountryDetailView(generic.DetailView):
#     model = Country
#     template_name = 'admm/detail.html'
# class PricingDetailView(generic.DetailView):
#     model = Durationwisepricing
#     template_name = 'admm/detail.html'
# class OfferadvDetailView(generic.DetailView):
#     model = Offercoveringadvs
#     template_name = 'admm/detail.html'
# class OfferDetailView(generic.DetailView):
#     model = Offerdetail
#     template_name = 'admm/detail.html'
# class OrderDetailView(generic.DetailView):
#     model = Order
#     template_name = 'admm/detail.html'
# class OrderdetailDetailView(generic.DetailView):
#     model = Orderdetails
#     template_name = 'admm/detail.html'
# class OrdfdbackDetailView(generic.DetailView):
#     model = Orderfeedback
#     template_name = 'admm/detail.html'
# class OrdpaymntDetailView(generic.DetailView):
#     model = Orderpayment
#     template_name = 'admm/detail.html'
# class PackageDetailView(generic.DetailView):
#     model = Package
#     template_name = 'admm/detail.html'
# class PackadvDetailView(generic.DetailView):
#     model = PackageHasAdv
#     template_name = 'admm/detail.html'
# class SellerdocDetailView(generic.DetailView):
#     model = Sellerdocdetail
#     template_name = 'admm/detail.html'
# class SellerdoclistDetailView(generic.DetailView):
#     model = Sellerdoclist
#     template_name = 'admm/detail.html'
# class StateDetailView(generic.DetailView):
#     model = State
#     template_name = 'admm/detail.html'
# class SubcatDetailView(generic.DetailView):
#     model = Subcategory
#     template_name = 'admm/detail.html'
# class UpdationsDetailView(generic.DetailView):
#     model = Updationinorder
#     template_name = 'admm/detail.html'
# class UserDetailView(generic.DetailView):
#     model = Userdetail
#     template_name = 'admm/detail.html'
# class UserroleDetailView(generic.DetailView):
#     model = Userrole
#     template_name = 'admm/detail.html'
# class WishlistDetailView(generic.DetailView):
#     model = Wishlistdetail
#     template_name = 'admm/detail.html'

@login_required
def userRoleInUserList(request):
    obj = Userrole.objects.aggregate(Max('roleid'))
    if obj['roleid__max'] == None:
        obj['roleid__max'] = 0
    (Userrole(roleid = obj['roleid__max'] + 1,rolename=request.POST['role'])).save()
    return redirect('admm:usersList')

@login_required
def userList(request):
    object_list=None
    if request.method=='GET':
        object_list=User.objects.filter(userroleid=1)
    elif request.method == 'POST':
        object_list=User.objects.filter(userroleid=int(request.POST['usrRoleFilter']))
    return render(request,'admm/user_list.html',{'object_list':object_list,'roles':Userrole.objects.all(),'roleId':int(request.POST.get('usrRoleFilter',default=1))})

# @login_required
class UserDel(generic.DeleteView):
    model = User
    success_url = ''

@login_required
def userDetail(request,pk):
    template_name = 'admm/user_detail.html'
    return render(request,template_name,{'object':get_object_or_404(User,id=pk)})

@login_required
def lockUnlockUser(request,pk,frmBranchPage):
    usr=get_object_or_404(User,id=pk)
    if usr.is_active == 1:
        usr.is_active=0
    else:
        usr.is_active = 1
    usr.save()
    if frmBranchPage == 0:
        return redirect('/adminsite/users/'+str(usr.id)+'/')
    else:
        return redirect('/adminsite/branch/admins/'+str(frmBranchPage))
# class UserEdit(UpdateView):
#     model = User
#     fields = ['first_name', 'last_name', 'mobileno', 'company_companyid']
    # fields = '__all__'

# class UserList(View):
#     pass

# Advertisement

@login_required
def upldImg(request):
    adv=Advertisement.objects.get(id=1)
    advImgObj=Advimgs(id=adv,adv_img=request.POST.get('advImgUpld'))
    advImgObj.save()
    return render(request,'admm/advertisement_form.html',{'advImgObj':advImgObj})

# @login_required
class CartAddLatest(View):
    def get(self,request):
        adv_form=AdvForm(instance=Advertisement())
        cart_forms=[CartForm(prefix=str(x),instance=Cartdetail()) for x in range(2)]
        template='admm/new_cart.html'
        context={'adv_form':adv_form,'cart_forms':cart_forms}
        return render(request,template,context)

    def post(self,request):
        # context = {}
        adv_form=AdvForm(request.POST,instance=Advertisement())
        cart_forms=[CartForm(request.POST,prefix=str(x),
                        instance=Cartdetail()) for x in range(2)]
        if adv_form.is_valid() and all([cart_form.is_valid() for cart_form in cart_forms]):
            new_adv = adv_form.save(commit=False)
            new_adv.auth_user = User.objects.get(email=request.user.email)
            print(new_adv.auth_user.email)
            print(cart_forms)
            new_adv.save()
            for cart_form in cart_forms:
                new_cart=cart_form.save(commit=False)
                new_cart.id=new_adv
                # new_cart.auth_user=User.objects.get(id=1)
                new_cart.save()
                # print(new_cart.noofdays)
            return redirect("/adminsite/list/Cartdetail")
        context={'adv_form':adv_form,'cart_forms':cart_forms}
        return render(request,'admm/new_cart.html',context)

# @login_required
class AdvCreateLatest(View):
    def get(self,request):
        adv_form=AdvForm(instance=Advertisement())
        # price_form=PricingForm(instance=Durationwisepricing())
        template='admm/new_adv.html'
        context={'adv_form':adv_form,'categories':Category.objects.all(),'sts':State.objects.all()}
        return render(request,template,context)

    def post(self,request):
        # context = {}
        # new_adv=None
        # adv_form=AdvForm(request.POST,instance=Advertisement())
        # price_form=PricingForm(request.POST,instance=Durationwisepricing())

        # if price_form.is_valid() and new_adv is not None:
        #     new_price=price_form.save(commit=False)
        #     new_price.advertisement_advid=new_adv
        #     new_price.save(force_insert=True)
        #     return redirect("/adminsite/list/Advertisement")
        # adv_imgs_count = int(request.POST['for_advImg_loop'])
        # addd=request.FILES['advimg1']
        # print(addd)
        # for filename,file
        # request.FILES
        # for i in range(adv_imgs_count):
        # request.POST['advimg' + str(i + 1)
        # print(request.FILES)
        # for filename,file in request.FILES.items():
        # # for i in range(adv_imgs_count):
        #     # print(filename)
        #     new_advimg = Advimgs(id=Advertisement.objects.get(advid=14), adv_img=file)
        #     # print(new_advimg.adv_img2)
        #     new_advimg.save(force_insert=True)
        # if adv_imgs_count is not None:
        #     return redirect('/adminsite/list/advimgs/')
        # if adv_form.is_valid() : #and price_form.is_valid():
        new_adv=Advertisement()

        new_adv.auth_user=User.objects.get(email=request.user.email)

        obj = Advertisement.objects.aggregate(Max('advid'))
        if obj['advid__max'] == None:
            obj['advid__max'] = 0
        new_adv.advid = obj['advid__max'] + 1

        new_adv.advregno=request.POST['advregno']

        height=request.POST['height']
        if height is not '':
            new_adv.height = height

        width = request.POST['width']
        if width is not '':
            new_adv.width = width

        stock = request.POST['stok']
        if stock is not '':
            new_adv.stock= stock

        if request.POST['aria'] is not '':
            new_adv.area_areaid=Area.objects.get(id=request.POST['aria'])

        if request.POST['citi'] is not '':
            new_adv.city_cityid=City.objects.get(id=request.POST['citi'])

        if request.POST['minQntt'] is not '':
            new_adv.minquantity=request.POST['minQntt']

        new_adv.addressline1=request.POST['addrs']
        new_adv.maxdays=0
        new_adv.subcategory_subcatid=Subcategory.objects.get(id=request.POST['subCat'])
        new_adv.save()



        # for i in range(adv_imgs_count):
        #     new_advimg = Advimgs(id=new_adv,adv_img=request.POST['advimg' + str(i)])
        #     new_advimg.save(force_insert=True)
        # setDflt=True
        # print('coming here babr')
        for filename, file in request.FILES.items():
                # print('for loop')
                # if setDflt is True:
                    # print('bad guy')
            new_adv.defaultimgpath = file
            new_adv.save()
            # setDflt=False
            # for i in range(adv_imgs_count):
            # print(filename)
            new_advimg = Advimgs(id=new_adv, adv_img=file)
            # print(new_advimg.adv_img2)
            # new_adv.defaultimgpath=file
            new_advimg.save(force_insert=True)

        priceRowCnt = int(request.POST['for_dwp_loop'])
        for i in range(1,priceRowCnt+1):
            new_price = Durationwisepricing(advertisement_advid=new_adv, noofdays=request.POST['days' + str(i)],price=request.POST['price' + str(i)])
            new_price.save(force_insert=True)
        # new_adv.save()
        return redirect('admm:listadv')

        # context={'adv_form':adv_form}#,'price_form':price_form}

        # messages.info(request,'something went wrong')
        # return render(request,'admm/new_adv.html',)

# @login_required
class PriceCreate(View):
    def post(self,request):
        price_form = PricingForm(request.POST, instance=Durationwisepricing())
        pass

# @login_required
class CmpnyCreate(View):
    def get(self,request):
        objects=Company.objects.all()
        cmpny_form=CompanyForm(instance=Company())
        template='admm/company.html'
        context={'cmpny_form':cmpny_form,'objects':objects}
        return render(request,template,context)

    def post(self,request):
        objects = Company.objects.all()
        cmpny_form=CompanyForm(request.POST,instance=Company())
        if cmpny_form.is_valid():# and all([cart_form.is_valid() for cart_form in cart_forms]):
            new_cmpny = cmpny_form.save(commit=False)
            obj=Company.objects.aggregate(Max('companyid'))
            # print(obj)
            if obj['companyid__max']==None:
                obj['companyid__max']=0
            new_cmpny.companyid = obj['companyid__max']+1
            new_cmpny.save()
            return redirect("/adminsite/company")
        context = {'cmpny_form': cmpny_form, 'objects': objects}
        return render(request,'admm/company.html',context)

# @login_required
def CmpnyEdit(request,cmpnypk,cmpnyname):
    obj = get_object_or_404(Company, companyid=cmpnypk)
    # tmp='doc_Name'+str(sdlpk)
    obj.companyname=cmpnyname
    obj.save()
    return redirect('/adminsite/company')

# @login_required
def CmpnyDel(request,cmpnypk):
    # obj=Sellerdoclist.objects.get()
    obj=get_object_or_404(Company,companyid=cmpnypk)
    obj.delete()
    return redirect('/adminsite/company')

# @login_required
class UserRoleCreate(View):
    def get(self,request):
        objects=Userrole.objects.all()
        userrole_form=UserroleForm(instance=Userrole())
        template='admm/userrole.html'
        context={'userrole_form':userrole_form,'objects':objects}
        return render(request,template,context)

    def post(self,request):
        objects = Userrole.objects.all()
        userrole_form=UserroleForm(request.POST,instance=Userrole())
        if userrole_form.is_valid():# and all([cart_form.is_valid() for cart_form in cart_forms]):
            new_userrole = userrole_form.save(commit=False)
            obj=Userrole.objects.aggregate(Max('roleid'))
            # print(obj)
            if obj['roleid__max']==None:
                obj['roleid__max']=0
            new_userrole.roleid = obj['roleid__max']+1
            new_userrole.save()
            return redirect("/adminsite/userroles")
        context = {'userrole_form': userrole_form, 'objects': objects}
        return render(request,'admm/userrole.html',context)

# @login_required
def UserRoleEdit(request,rlpk,role):
    obj = get_object_or_404(Userrole, roleid=rlpk)
    # tmp='doc_Name'+str(sdlpk)
    obj.rolename=role
    obj.save()
    return redirect('/adminsite/userroles')

@login_required
def UserRoleDel(request,rlpk):
    # obj=Sellerdoclist.objects.get()
    obj=get_object_or_404(Userrole,roleid=rlpk)
    obj.delete()
    return redirect('/adminsite/userroles')

def location(request):
    template='admm/ar_ct_st_cn.html'
    context={'cnobjects':Country.objects.all()}
    return render(request, template, context)
def locationUpdt(request):
    cnId = int(request.GET.get('id'))
    print(cnId)
    print('hey')
    try:
        obj=Country.objects.get(id=str(cnId))
        obj.countryname = request.GET.get('name')
        obj.save()
        msg = 'succeed'
        messages.info(request, msg)
    except ObjectDoesNotExist:
        msg = 'not succeed'
        messages.info(request, msg)
    data = {
        'msg': msg,
        'name': obj.countryname
    }
    return JsonResponse(data)

def locationDel(request):
    cnId = int(request.GET.get('id'))
    print(cnId)
    print('hey')
    try:
        obj=Country.objects.get(id=str(cnId))
        obj.delete()
        msg = 1
    except:
        msg = 0
    data = {
        'msg': msg,
    }
    return JsonResponse(data)

def cityObjs(request):
    stateId = int(request.GET.get('id'))
    # print(stateId)
    # print('hey')
    # stObjs = None
    # try:
    state=State.objects.get(id=int(stateId))
    ctObjs=list(state.city_set.values('id','cityname'))
    print(ctObjs)
    # lst_stObjs=serializers.serialize('json',stObjs,fields=)
    # msg = 1
    # except:
    #     msg = 0
    # strOflist=''
    # for st in stObjs:

    data = {
        'ctObjs':ctObjs,
    }
    return JsonResponse(data)

def areaObjs(request):
    ctId = int(request.GET.get('id'))
    # print(stateId)
    # print('hey')
    # stObjs = None
    # try:
    ct=City.objects.get(id=int(ctId))
    arObjs=list(ct.area_set.values('id','areaname'))
    print(arObjs)
    # lst_stObjs=serializers.serialize('json',stObjs,fields=)
    # msg = 1
    # except:
    #     msg = 0
    # strOflist=''
    # for st in stObjs:

    data = {
        'arObjs':arObjs,
    }
    return JsonResponse(data)

def stateObjs(request):
    cnId = int(request.GET.get('id'))
    print(cnId)
    print('hey')
    stObjs = None
    # try:
    cnObj=Country.objects.get(id=str(cnId))
    stObjs=list(cnObj.state_set.values('id','statename'))
    print(stObjs)
    # lst_stObjs=serializers.serialize('json',stObjs,fields=)
    # msg = 1
    # except:
    #     msg = 0
    # strOflist=''
    # for st in stObjs:

    data = {
        'stObjs':stObjs,
    }
    return JsonResponse(data)
# class LocationViewCreateForm(View):
#     def get(self,request,cn=None,st=None,ct=None):
#         stobjects = ctobjects = arobjects = None
#         if cn is not None:
#             stobjects = State.objects.filter(country_countryid=cn)
#             if st is not None:
#                 ctobjects=City.objects.filter(state_stateid=st)
#                 if ct is not None:
#                     arobjects=Area.objects.filter(city_cityid=ct)
#         # subcat_form = SubcategoryForm(instance=Subcategory())
#         # cat_form=CategoryForm(instance=Category())
#         subcat_form = None
#         cat_form=None
#         template='admm/ar_ct_st_cn.html'
#         context={'cat_form':cat_form,'cnobjects':Country.objects.all(),'stobjects':stobjects,'ctobjects':ctobjects,'arobjects':arobjects,'subcat_form':subcat_form}
#         return render(request,template,context)

class CategoryCreateForm(View):
    def get(self,request):
        if request.user.is_authenticated:
            subcat_form = SubcategoryForm(instance=Subcategory())
            objects=Category.objects.all()
            cat_form=CategoryForm(instance=Category())
            template='admm/categoryLatest.html'
            context={'cat_form':cat_form,'objects':objects,'subcat_form':subcat_form}
            return render(request,template,context)
        return redirect('login:log_in')

    def post(self,request,pk=None):
        objects = Category.objects.all()
        cat_form=CategoryForm(request.POST,instance=Category())
        # subcat_form = SubcategoryForm(instance=Subcategory())
        if cat_form.is_valid():# and all([cart_form.is_valid() for cart_form in cart_forms]):
            new_cat = cat_form.save(commit=False)
            obj=Category.objects.aggregate(Max('id'))
            # print(obj)
            if obj['id__max']==None:
                obj['id__max']=0
            new_cat.id = obj['id__max']+1
            new_cat.save()
            return redirect("/adminsite/categories")
        context = {'cat_form': cat_form, 'objects': objects}#,'subcat_form':subcat_form}
        return render(request,'admm/category.html',context)

@login_required
def catWiseSubcats(request):
    pass

@login_required
def categoryEdit(request):
    try:
        obj = get_object_or_404(Category, id=request.GET.get('id'))
        obj.categoryname=request.GET.get('catName')
        obj.save()
        result=1
    except:
        result=0
    data={
        'result':result
    }
    return JsonResponse(data)

@login_required
def categoryDel(request):
    # obj=Sellerdoclist.objects.get()
    try:
        obj=get_object_or_404(Category,id=request.GET.get('id'))
        obj.delete()
        result=1
    except:
        result=0
    data={
        'result':result,
    }
    return JsonResponse(data)

@login_required
def subCatSave(request):
    # catid=
    # scatname=
    # dscnt=
    obj = Subcategory.objects.aggregate(Max('id'))
    # print(obj)
    try:
        if obj['id__max'] == None:
            obj['id__max'] = 0
        newScat=Subcategory(id=obj['id__max']+1,subcatname=request.GET.get('scat_name'),commission=request.GET.get('cmsn'),catid=Category.objects.get(id=request.GET.get('category_id')))
        newScat.save()
        result = 1
    except:
        result=0
    data ={
        'result':result,
    }
    return JsonResponse(data)
# @login_required
class SubcategoryCreateForm(View):
    # def get(self,request,pk):
    #     subobjects=Subcategory.objects.filter(catid=pk)
    #     subcat_form=SubcategoryForm(instance=Subcategory())
    #     template='admm/subcategory.html'
    #     context={'subcat_form':subcat_form,'objects':objects}
    #     return render(request,template,context)

    def post(self,request,pk):
        # objects = Subcategory.objects.filter(catid=pk)
        subcat_form=SubcategoryForm(request.POST,instance=Subcategory())
        if subcat_form.is_valid():# and all([cart_form.is_valid() for cart_form in cart_forms]):
            new_subcat = subcat_form.save(commit=False)
            obj=Subcategory.objects.aggregate(Max('id'))
            # print(obj)
            if obj['id__max']==None:
                obj['id__max']=0
            new_subcat.id = obj['id__max']+1
            new_subcat.catid = Category.objects.get(id=pk)
            new_subcat.save()
        return redirect("/adminsite/categories/"+str(pk))
        # context = {'subcat_form': subcat_form, 'objects': objects}
        # return render(request,'admm/subcategory.html',context)

@login_required
def subcategoryEdit(request):
    hasNameUpdtd = hasCmsnUpdtd =0
    try:
        obj = get_object_or_404(Subcategory, id=request.GET.get('sid'))
        # tmp='doc_Name'+str(sdlpk)
        if request.GET.get('new_name') is not '':
            obj.subcatname=request.GET.get('new_name')
            hasNameUpdtd=1
        if request.GET.get('new_cmishan') is not '':
            obj.commission=request.GET.get('new_cmishan')
            hasCmsnUpdtd = 1
        obj.save()
        result=1
    except:
        result=0
    data={
        'result':result,
        'hasNameUpdtd':hasNameUpdtd,
        'hasCmsnUpdtd':hasCmsnUpdtd,
    }
    return JsonResponse(data)

@login_required
def subcategoryDel(request):
    # obj=Sellerdoclist.objects.get()
    try:
        obj=Subcategory.objects.get(subcatname=request.GET.get('scat_name'))
        obj.delete()
        result = 1
    except:
        result = 0
    data={
        'result':result,
    }
    return JsonResponse(data)

# @login_required
class SellerDocCreate(View):
    def get(self,request):
        objects=Sellerdoclist.objects.all()
        sellerDocList_form=SellerDocForm(instance=Sellerdoclist())
        template='admm/seller_doc_list.html'
        context={'sellerDocList_form':sellerDocList_form,'objects':objects}
        return render(request,template,context)

    def post(self,request):
        objects = Sellerdoclist.objects.all()
        sellerDocList_form=SellerDocForm(request.POST,instance=Sellerdoclist())
        if sellerDocList_form.is_valid():# and all([cart_form.is_valid() for cart_form in cart_forms]):
            new_sellerDoc = sellerDocList_form.save(commit=False)
            obj=Sellerdoclist.objects.aggregate(Max('docid'))
            # print(obj)
            if obj['docid__max']==None:
                obj['docid__max']=0
            new_sellerDoc.docid = obj['docid__max']+1
            new_sellerDoc.save()
            return redirect("/adminsite/sellerdoclist")
        context = {'sellerDocList_form': sellerDocList_form, 'objects': objects}
        return render(request,'admm/seller_doc_list.html',context)

@login_required
def sellerDocEdit(request,sdlpk,doc):
    obj = get_object_or_404(Sellerdoclist, docid=sdlpk)
    # tmp='doc_Name'+str(sdlpk)
    obj.docname=doc
    obj.save()
    return redirect('/adminsite/sellerdoclist')

@login_required
def sellerDocDel(request,sdlpk):
    # obj=Sellerdoclist.objects.get()
    obj=get_object_or_404(Sellerdoclist,docid=sdlpk)
    obj.delete()
    return redirect('/adminsite/sellerdoclist')

# @login_required
class BranchCreateViewForm(View):
    def get(self,request):
        objects=Branch.objects.all()
        ctObs=City.objects.all()
        branch_form=BranchForm(instance=Branch())
        template='admm/branch.html'
        context={'branch_form':branch_form,'objects':objects,'cmpny':Company.objects.get(companyid=1),'ctObs':ctObs}
        return render(request,template,context)

    def post(self,request):
        objects = Branch.objects.filter(int(request.POST['context']))
        branch_form=BranchForm(request.POST,instance=Branch())
        if branch_form.is_valid():# and all([cart_form.is_valid() for cart_form in cart_forms]):
            new_branch = branch_form.save(commit=False)
            obj=Branch.objects.aggregate(Max('id'))
            # print(obj)
            if obj['id__max']==None:
                obj['id__max']=0
            new_branch.id = obj['id__max']+1
            new_branch.company_companyid=Company.objects.get(companyid=1)
            new_branch.save()
            return redirect("admm:branch_viewadd")
        context = {'branch_form': branch_form, 'objects': objects}
        return render(request,'admm/branch.html',context)

@login_required
def branchEdit(request,pk):
    obj = get_object_or_404(Branch, id=pk)
    obj.branchaddress=request.POST.get('branch_address'+str(pk))
    obj.mobileno=request.POST.get('mobileno'+str(pk))
    obj.save()
    return redirect('/adminsite/branch')

@login_required
def BranchDeleteForm(request,pk):
    # obj=Sellerdoclist.objects.get()
    obj=get_object_or_404(Branch,id=pk)
    obj.delete()
    return redirect('/adminsite/branch')

@login_required
def branchAdmins(request,pk):
    try:
        objects=User.objects.filter(branchid=int(pk))
    except ObjectDoesNotExist:
        messages.info(request,'No admins')
    return render(request,'admm/branchAdmins.html',context={'objects':objects})

# @login_required
class AdvCreate(CreateView):
    model = Advertisement
    # fields = ['id', 'advregno', 'height', 'width', 'maxdays', 'minquantity', 'addressline1', 'area_areaid',
    #           'city_cityid', 'stock', 'defaultimgpath', 'subcategory_subcatid', 'auth_user']
    fields = '__all__'
    # def get_context_data(self, **kwargs):
    #
    #     return {}

# class AdvUpdate(UpdateView):
#     model = Advertisement
#     # fields = ['id', 'advregno', 'height', 'width', 'maxdays', 'minquantity', 'addressline1', 'area_areaid',
#     #           'city_cityid', 'stock', 'defaultimgpath', 'subcategory_subcatid', 'auth_user']
#     # success_url = reverse_lazy('admm:randomObjDetail',kw)
#     fields = '__all__'
#
# class AdvDelete(DeleteView):
#     model = Advertisement
#     success_url = reverse_lazy('admm:index')


# AdvImgs
# @login_required
class AdvImgsCreate(CreateView):
    model = Advimgs
    # fields = ['advertisement_advid', 'imagepath']
    fields = '__all__'

# @login_required
class AdvImgsUpdate(UpdateView):
    model = Advimgs
    # fields = ['advertisement_advid', 'imagepath']
    fields = '__all__'

# @login_required
class AdvImgsDelete(DeleteView):
    model = Advimgs
    success_url = reverse_lazy('admm:index')

# @login_required
# Area
class AreaCreate(CreateView):
    model = Area
    # fields = ['areaid','areaname','city_cityid']
    fields = '__all__'

# @login_required
class AreaUpdate(UpdateView):
    model = Area
    # fields = ['areaid', 'areaname', 'city_cityid']
    fields = '__all__'

# @login_required
class AreaDelete(DeleteView):
    model = Area
    # success_url = 'list/12'
    success_url = reverse_lazy('admm:index')
    # success_url = model.get_absolut_url(12)

# @login_required
# Branch
class BranchCreate(CreateView):
    model = Branch
    # fields = ['branchaddress','mobileno','company_companyid']
    fields = '__all__'

# @login_required
class BranchUpdate(UpdateView):
    model = Branch
    # fields = ['branchid', 'branchaddress', 'mobileno', 'company_companyid']
    fields = '__all__'
# @login_required
class BranchDelete(DeleteView):
    model = Branch
    success_url = reverse_lazy('admm:index')

# @login_required
# Order
class OrderCreate(CreateView):
    model = Order
    # fields = ['orderid','userdetail_userid','orderdatetime','emipayment','emimonths','coupondetail','discountamount','gst_amount']
    fields = '__all__'

# @login_required
class OrderUpdate(UpdateView):
    model = Order
    # fields = ['orderid','userdetail_userid','orderdatetime','emipayment','emimonths','coupondetail','discountamount','gst_amount']
    fields = '__all__'

# @login_required
class OrderDelete(DeleteView):
    model = Order
    success_url = reverse_lazy('admm:index')

# @login_required
# Orderdetails
class OrderdetailsCreate(CreateView):
    model = Orderdetails
    # fields = ['order_orderid', 'advertisement_advid', 'advprice', 'advstartdate', 'quantity']
    fields = '__all__'

# @login_required
class OrderdetailsUpdate(UpdateView):
    model = Orderdetails
    # fields = ['order_orderid', 'advertisement_advid', 'advprice', 'advstartdate', 'quantity']
    fields = '__all__'

# @login_required
class OrderdetailsDelete(DeleteView):
    model = Orderdetails
    success_url = reverse_lazy('admm:index')


# Cancellationofordadv
# class CancellationofordadvCreate(CreateView):
#     model = Cancellationofordadv
#     # fields = ['order_id', 'advrtid', 'cancellationdatetime', 'reasonofcancellation', 'paymentrefid', 'paymentdatetime',
#     #           'refundedamount']
#     fields = '__all__'

# class CancellationofordadvUpdate(UpdateView):
#     model = Cancellationofordadv
#     # fields = ['order_id', 'advrtid', 'cancellationdatetime', 'reasonofcancellation', 'paymentrefid', 'paymentdatetime',
#     #           'refundedamount']
#     fields = '__all__'
#
# class CancellationofordadvDelete(DeleteView):
#     model = Cancellationofordadv
#     success_url = reverse_lazy('admm:index')


# Cartdetail


class CartdetailCreate(CreateView):
    model = Cartdetail
    #fields = ['userdetail_userid', 'advertisement_advid', 'price', 'startdate', 'enddate', 'quantity']
    fields = '__all__'

class CartdetailUpdate(UpdateView):
    model = Cartdetail
    #fields = ['userdetail_userid', 'advertisement_advid', 'price', 'startdate', 'enddate', 'quantity']
    fields='__all__'

class CartdetailDelete(DeleteView):
    model = Cartdetail
    success_url = reverse_lazy('admm:index')

# Category
class CategoryCreate(CreateView):
    model = Category
    # fields = ['categoryid','categoryname']
    fields = '__all__'


class CategoryUpdate(UpdateView):
    model = Category
    # fields = ['categoryid','categoryname']
    fields = '__all__'


class CategoryDelete(DeleteView):
    model = Category
    success_url = reverse_lazy('admm:index')


# City
class CityCreate(CreateView):
    model = City
    # fields = ['cityid', 'cityname', 'state_stateid']
    fields = '__all__'

class CityUpdate(UpdateView):
    model = City
    # fields = ['cityid', 'cityname', 'state_stateid']
    fields = '__all__'

class CityDelete(DeleteView):
    model = City
    success_url = reverse_lazy('admm:index')


# Commissiondetail
class CommissiondetailCreate(CreateView):
    model = Commissiondetail
    # fields = ['advertisement_advid', 'commission', 'createddatetime']
    fields = '__all__'

class CommissiondetailUpdate(UpdateView):
    model = Commissiondetail
    # fields = ['advertisement_advid', 'commission', 'createddatetime']
    fields = '__all__'

class CommissiondetailDelete(DeleteView):
    model = Commissiondetail
    success_url = reverse_lazy('admm:index')


# Company
class CompanyCreate(CreateView):
    model = Company
    # fields = ['companyid', 'companyname', 'logopath']
    fields = '__all__'

class CompanyUpdate(UpdateView):
    model = Company
    # fields = ['companyid', 'companyname', 'logopath']
    fields = '__all__'

class CompanyDelete(DeleteView):
    model = Company
    # success_url = reverse_lazy('admm:index')


# Complaintdetail
class ComplaintdetailCreate(CreateView):
    model = Company
    # fields = ['companyid', 'companyname', 'logopath']
    fields = '__all__'

class ComplaintdetailUpdate(UpdateView):
    model = Company
    # fields = ['companyid', 'companyname', 'logopath']
    fields = '__all__'

class ComplaintdetailDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('admm:index')


# Country
class CountryCreate(CreateView):
    model = Country
    # fields = ['countryid', 'countryname']
    fields = '__all__'

class CountryUpdate(UpdateView):
    model = Country
    # fields = ['countryid', 'countryname']
    fields = '__all__'

class CountryDelete(DeleteView):
    model = Country
    success_url = reverse_lazy('admm:index')


# Coupondetail
class CoupondetailCreate(CreateView):
    model = Coupondetail
    # fields = ['couponid', 'couponcode', 'coupondescription', 'coupondiscount', 'couponstartdate', 'couponenddate',
    #           'mincartvalue', 'userdetail_userid']
    fields = '__all__'

class CoupondetailUpdate(UpdateView):
    model = Coupondetail
    fields = ['couponcode', 'coupondescription', 'coupondiscount', 'couponstartdate', 'couponenddate',
                  'mincartvalue', 'auth_user']
    # fields = '__all__'
    template_name = 'admm/couponEdit.html'
    success_url = reverse_lazy('admm:couponsListOrAdd')

def delCoupon(request):
    try:
        obj = Coupondetail.objects.get(id=request.GET.get('cpnId'))
        obj.delete()
        rslt = 1
    except:
        rslt=0
    data = {
        'result': rslt
    }
    return JsonResponse(data)


# Docdetail
# class DocdetailCreate(CreateView):
#     model = Docdetail
#     fields = ['userdetail_userid','sellerdoclist_docid','docpath']
# class DocdetailUpdate(UpdateView):
#     model = Docdetail
#     fields = ['userdetail_userid','sellerdoclist_docid','docpath']
# class DocdetailDelete(DeleteView):
#     model = Docdetail
#     success_url = reverse_lazy('admm:index')

# Durationwisepricing
class DurationwisepricingCreate(CreateView):
    model = Durationwisepricing
    fields = ['noofdays', 'price']
    # fields = ['advertisement_advid', 'noofdays', 'price']
    # fields = '__all__'

class DurationwisepricingUpdate(UpdateView):
    model = Durationwisepricing
    # fields = ['advertisement_advid', 'noofdays', 'price']
    fields = '__all__'

class DurationwisepricingDelete(DeleteView):
    model = Durationwisepricing
    success_url = reverse_lazy('admm:index')


# Offercoveringadvs
class OffercoveringadvsCreate(CreateView):
    model = Offercoveringadvs
    # fields = ['offerdetail_offerid', 'advertisement_advid']
    fields = '__all__'

class OffercoveringadvsUpdate(UpdateView):
    model = Offercoveringadvs
    # fields = ['offerdetail_offerid', 'advertisement_advid']
    fields = '__all__'

class OffercoveringadvsDelete(DeleteView):
    model = Offercoveringadvs
    success_url = reverse_lazy('admm:index')


# Offerdetail
class OfferdetailCreate(CreateView):
    model = Offerdetail
    # fields = ['offerid', 'description', 'discount', 'offerstartdatetime', 'offerenddatetime']
    fields = '__all__'

class OfferdetailUpdate(UpdateView):
    model = Offerdetail
    # fields = ['offerid', 'description', 'discount', 'offerstartdatetime', 'offerenddatetime']
    fields = '__all__'

class OfferdetailDelete(DeleteView):
    model = Offerdetail
    success_url = reverse_lazy('admm:index')


# Orderfeedback
class OrderfeedbackCreate(CreateView):
    model = Orderfeedback
    # fields = ['orderdetail_orderid', 'feedbackdatetime', 'feedbacktext', 'rating', 'responsedatetime', 'responsetext',
    #           'userdetail_userid']
    fields = '__all__'

class OrderfeedbackUpdate(UpdateView):
    model = Orderfeedback
    # fields = ['orderdetail_orderid', 'feedbackdatetime', 'feedbacktext', 'rating', 'responsedatetime', 'responsetext',
    #           'userdetail_userid']
    fields = '__all__'

class OrderfeedbackDelete(DeleteView):
    model = Orderfeedback
    success_url = reverse_lazy('admm:index')


# Orderpayment
class OrderpaymentCreate(CreateView):
    model = Orderpayment
    fields = '__all__'
    # fields = ['paymentrefid', 'orderdetail_orderid', 'paymentdatetime', 'amount']


class OrderpaymentUpdate(UpdateView):
    model = Orderpayment
    fields = '__all__'
    # fields = ['paymentrefid', 'orderdetail_orderid', 'paymentdatetime', 'amount']


class OrderpaymentDelete(DeleteView):
    model = Orderpayment
    success_url = reverse_lazy('admm:index')


# Package
class PackageCreate(CreateView):
    model = Package
    fields = '__all__'
    # fields = ['packageid', 'packagedescription', 'discount', 'startdate', 'enddate']


class PackageUpdate(UpdateView):
    model = Package
    fields = '__all__'
    # fields = ['packageid', 'packagedescription', 'discount', 'startdate', 'enddate']


class PackageDelete(DeleteView):
    model = Package
    success_url = reverse_lazy('admm:index')


# PackageHasAdv
class PackageHasAdvCreate(CreateView):
    model = PackageHasAdv
    fields = '__all__'
    # fields = ['package_packageid', 'advertisement_advid', 'quantity']


class PackageHasAdvUpdate(UpdateView):
    model = PackageHasAdv
    fields = '__all__'
    # fields = ['package_packageid', 'advertisement_advid', 'quantity']


class PackageHasAdvDelete(DeleteView):
    model = PackageHasAdv
    success_url = reverse_lazy('admm:index')


# Sellerdocdetail
class SellerdocdetailCreate(CreateView):
    model = Sellerdocdetail
    fields = '__all__'
    # fields = ['userdetail_userid', 'sellerdoclist_docid', 'docpath']


class SellerdocdetailUpdate(UpdateView):
    model = Sellerdocdetail
    fields = '__all__'
    # fields = ['userdetail_userid', 'sellerdoclist_docid', 'docpath']


class SellerdocdetailDelete(DeleteView):
    model = Sellerdocdetail
    success_url = reverse_lazy('admm:index')


# Sellerdoclist


class SellerdoclistCreate(CreateView):
    model = Sellerdoclist
    fields = '__all__'
    # fields = ['docid', 'docname']


class SellerdoclistUpdate(UpdateView):
    model = Sellerdoclist
    fields = '__all__'
    # fields = ['docid', 'docname']


class SellerdoclistDelete(DeleteView):
    model = Sellerdoclist
    success_url = reverse_lazy('admm:index')


# State
class StateCreate(CreateView):
    model = State
    fields = '__all__'
    # fields = ['stateid', 'statename', 'country_countryid']


class StateUpdate(UpdateView):
    model = State
    fields = '__all__'
    # fields = ['stateid', 'statename', 'country_countryid']


class StateDelete(DeleteView):
    model = State
    success_url = reverse_lazy('admm:index')


# Subcategory
class SubcategoryCreate(CreateView):
    model = Subcategory
    fields = '__all__'
    # fields = ['subcatid', 'subcatname','catid']


class SubcategoryUpdate(UpdateView):
    model = Subcategory
    fields = '__all__'
    # fields = ['subcatid', 'subcatname', 'catid']


class SubcategoryDelete(DeleteView):
    model = Subcategory
    success_url = reverse_lazy('admm:index')


# Updationinorder
class UpdationinorderCreate(CreateView):
    model = Updationinorder
    # fields = ['orderid', 'advid', 'updationdatetime', 'amount', 'paymentrefid', 'paymentdatetime']
    fields = '__all__'

class UpdationinorderUpdate(UpdateView):
    model = Updationinorder
    # fields = ['orderid', 'advid', 'updationdatetime', 'amount', 'paymentrefid', 'paymentdatetime']
    fields = '__all__'

class UpdationinorderDelete(DeleteView):
    model = Updationinorder
    success_url = reverse_lazy('admm:index')


# Userdetail
class UserdetailCreate(CreateView):
    model = User
    fields = '__all__'


class UserdetailUpdate(UpdateView):
    model = User
    fields = '__all__'


class UserdetailDelete(DeleteView):
    model = User
    success_url = reverse_lazy('admm:index')


# Userrole
class UserroleCreate(CreateView):
    model = Userrole
    fields = '__all__'


class UserroleUpdate(UpdateView):
    model = Userrole
    fields = '__all__'


class UserroleDelete(DeleteView):
    model = Userrole
    success_url = reverse_lazy('admm:index')


# Wishlistdetail
class WishlistdetailCreate(CreateView):
    model = Wishlistdetail
    fields = '__all__'


class WishlistdetailUpdate(UpdateView):
    model = Wishlistdetail
    fields = '__all__'


class WishlistdetailDelete(DeleteView):
    model = Wishlistdetail
    success_url = reverse_lazy('admm:index')
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
