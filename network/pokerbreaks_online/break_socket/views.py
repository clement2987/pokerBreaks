from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json

new_break_events = {
    "events": list()
}
table_breaks = {}
# Create your views here.
def index(request):
    return render(request, "break_socket/index.html", {"table_breaks":table_breaks})


# app api calls
def app_login(request):
    ...

@csrf_exempt
def update_breaks(request):
    if request.method != "POST":
        return JsonResponse({"error","Request must be post"},status=408)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({"error","Invalid JSON format"}, status=400)
    
    if data['key'] != "test_123":
        return JsonResponse({"error","invaalid key"}, status=401)
    
    global table_breaks
    table_breaks = data.get('break_scadual')
    return JsonResponse({"message": "breaks updated successfully"} ,status=200)

def getupdate(request):
    if request.method != "POST":
        return JsonResponse({"error","Request must be post"},status=408)
    
    global new_break_events
    if len(new_break_events["events"]) < 1:
        return JsonResponse({"message": "no new breaks to report"}, status=200)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({"error","Invalid JSON format"}, status=400)
    
    if data['key'] != "test_123":
        return JsonResponse({"error","invaalid key"}, status=401)
    
    if data['message'] != "update_breaks":
        return JsonResponse({"error","This api only updates breaks"},status=408)
    
    return JsonResponse({
        "message": "new breaks attatched",
        "new_breaks": new_break_events["events"]
    }, status=200)
def breaksreceived(request):
    if request.method != "POST":
        return JsonResponse({"error","Request must be post"},status=408)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({"error","Invalid JSON format"}, status=400)
    
    if data['key'] != "test_123":
        return JsonResponse({"error","invaalid key"}, status=401)
    
    global new_break_events
    new_break_events['events'] = list()
    return JsonResponse({"message": "breaks list refreshed successfully"} ,status=200)


# site api calls
def add_break(request):
    if request.method != "POST":
        return JsonResponse({"error","Request must be post"},status=408)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({"error","Invalid JSON format"}, status=400)
    
    new_break_info = data.get("new_break")

    new_break_events["events"].append(new_break_info)
    return JsonResponse({"message": "breaks updated successfully"} ,status=200)