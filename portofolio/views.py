from django.shortcuts import render

def show_main(request):
    context = {
        'name': 'Paket Shop',
        'class': 'PBP A',
    }
    return render(request, "main.html", context)