from django.shortcuts import render

# Create your views here.


app_name= 'noumatch'

def index(request):
    return render(request, 'noumatch/index.html')








def term_of_use(request):
    return render(request, 'noumatch/term_of_use.html')







def privacy_policy(request):
    return render(request, 'noumatch/privacy_policy.html')



