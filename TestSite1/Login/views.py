from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError
from .models import SignUp,Profile
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
from django.contrib.auth.models import auth,User
from django.shortcuts import redirect
# Create your views here.



def Signup(request):
    #context = {'fname_err' : 'Firstname', 'lname_err' : 'Lastname',  'email_err' : 'Email', 'pw_err' : 'Password','repass_err' : 'Confirm Password',
    #            'fname_val' : '', 'lname_val' : '', 'email_val' : '', 'pw_val' : '','repass_val':'','placeholder_color':'black'
    #          }
    if(request.method=='POST'):
        
        
        #is_not_valid = False
        #if len(request.POST.get('fname'))==0:
         #   context['fname_err']='Firstname required'
        #    is_not_valid=True
        #else:
        #    context['fname_val']=request.POST['fname']
        
        #if len(request.POST.get('lname'))==0:
        #    context['lname_err']='Lastname required'
        #    is_not_valid=True
        #else:
        #    context['lname_val']=request.POST.get('lname')
        
        #if len(request.POST.get('email'))==0:
        #    context['email_err']='Email required'
        #    is_not_valid=True
        #else:
        #    context['email_var']=request.POST.get('email')
        #if len(request.POST.get('pwd'))==0:
        #    context['pw_err']='Password Required'
        #    is_not_valid=True
        #else:
        #    context['pw_var']=request.POST.get('pwd')
        #if len(request.POST.get('confpwd'))==0:
        #    context['repass_err']='Confirm Password is required'
        #    is_not_valid=True
        #else:
        #    if request.POST.get('pwd') != request.POST.get('confpwd'):
        #        context['repass_err']='Confirm Password is not same as Password'
        #        is_not_valid=True


        


        #if is_not_valid:
        #    context['placeholder_color'] = 'red'
        #    return render(request, 'index.html', context= context)
        fn=request.POST.get('fname')
        ln=request.POST.get('lname')
        em=request.POST.get('email')
        un=request.POST.get('uname')
        passw=request.POST.get('pwd')
        repassword=request.POST.get('confpwd')
        #sp=SignUp(fname=fn,lname=ln,email=em,password=passw,repass=repassword)
        user =User.objects.create_user(username=un,email=em,password=passw,first_name=fn,last_name=ln)
      
        user.is_active=False
        profile=Profile(profile_pic=f'img/{fn}.jpg',user=user)
        user.save()
        
        profile.save()
        current_site=get_current_site(request)
        email_subject='Activate your Account'
        message=render_to_string('activate.html',
        {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': user.pk,
                            'token': generate_token.make_token(user)
        }
        )

        email_message = EmailMessage(
                            email_subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            [em]

        )
        email_message.send()
        #sp.save()

        uploaded_file=request.FILES['document']

        fs = FileSystemStorage()
        fs.save(f"{user.first_name}.jpg", uploaded_file)
        return render(request,'Linksend.html')
    else:

        return render(request,'index.html')

def login(request):
    if request.method=='GET':

        return render(request,'login.html')
    
    else:
        username=request.POST['un']
        password=request.POST['pwd']
        
        try:
            #obj = SignUp.objects.get(email=em)
            user=auth.authenticate(username=username,password=password)
            if user is not None:
                
                
                if user.is_active==True:



                    im_url=Profile.objects.get(user=user)
                    return render(request,'welcome.html',{'data':user,'imageurl':im_url})
                else:
                    messages.info(request,'Please activate your account first')
                    return render(request,'login.html')
        
            else:
                    messages.info(request,'Invalid Credentials')
                    return render(request,'login.html')
        except(SignUp.DoesNotExist):
            print('not found')
            messages.info(request,'No such User Found')
            return render(request,'login.html')




class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        
        uid=uidb64
        user=User.objects.get(pk=uid)
        
        #except Exception as identifier:
        #    user=None
        
        if user is not None:
            user.is_active=True
            user.save()
            return redirect('http://127.0.0.1:8000/login')
        
        return render(request,'activate_failed.html',status=401)
        #and generate_token.check_token(user,token)