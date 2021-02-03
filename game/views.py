from django.shortcuts import render

# Create your views here.


def lobby(request):
    numRow = 20
    numCol = 20
    context = {'numRow': range(numRow), 'numCol': range(numCol)}
    return render(request, 'game/index.html', context)
