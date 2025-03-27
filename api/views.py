import os
import json
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Serve index.html from templates folder
def index(request):
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def find_drugs(request):
    try:
        body = json.loads(request.body)
        disease = body.get("disease", "")
        response = requests.get(
            "https://api.fda.gov/drug/event.json",
            params={
                "search": f'patient.drug.drugindication:"{disease}"',
                "limit": 5,
            },
        )
        data = response.json()
        results = []
        if "results" in data:
            for event in data["results"]:
                drug = event.get("patient", {}).get("drug", [{}])[0].get("medicinalproduct", "")
                reaction = event.get("patient", {}).get("reaction", [{}])[0].get("reactionmeddrapt", "")
                results.append({"drug": drug, "reaction": reaction})
        return JsonResponse({"drugs": results})
    except Exception as e:
        print("Ошибка при обращении к OpenFDA API:", str(e))
        return JsonResponse({"error": "Ошибка при поиске лекарств"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_symptoms_analysis(request):
    try:
        body = json.loads(request.body)
        symptoms = body.get("symptoms", "")
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Вы полезный медицинский помощник."},
                {"role": "user", "content": f"Вот мои симптомы: {symptoms}. Скажи названия 3 потенциальных заболевании и нужные действия и лекарства.Ответ не больше 75 слов без звездочек и оглавлении"},
            ],
        }
        headers = {
            "Authorization": f'Bearer {os.environ.get("API_KEY")}',
            "Content-Type": "application/json",
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        data = response.json()
        analysis = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return JsonResponse({"analysis": analysis})
    except Exception as e:
        print("Ошибка при общении с OpenAI API:", str(e))
        return JsonResponse({"error": "Что-то пошло не так!"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def find_pharmacies(request):
    try:
        body = json.loads(request.body)
        latitude = body.get("latitude")
        longitude = body.get("longitude")
        radius = 1000
        overpassUrl = f"https://overpass-api.de/api/interpreter?data=[out:json];(node[\"amenity\"=\"pharmacy\"](around:{radius},{latitude},{longitude}););out;"
        response = requests.get(overpassUrl)
        data = response.json()
        pharmacies = []
        if "elements" in data:
            for pharmacy in data["elements"]:
                name = pharmacy.get("tags", {}).get("name", "Без названия")
                pharmacies.append({
                    "name": name,
                    "lat": pharmacy.get("lat"),
                    "lon": pharmacy.get("lon"),
                })
        return JsonResponse(pharmacies, safe=False)
    except Exception as e:
        print("Ошибка при получении аптек:", str(e))
        return JsonResponse({"error": "Не удалось найти аптеки."}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_disease(request):
    try:
        body = json.loads(request.body)
        symptoms = body.get("symptoms", "")
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Вы медицинский помощник. Укажите одну наиболее вероятную болезнь по введённым симптомам."},
                {"role": "user", "content": f"Вот мои симптомы: {symptoms}. выведи одно наиболее вероятное заболевание в формате одного слова на английском. Например 'flu'."},
            ],
        }
        headers = {
            "Authorization": f'Bearer {os.environ.get("API_KEY")}',
            "Content-Type": "application/json",
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        data = response.json()
        disease = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return JsonResponse({"disease": disease})
    except Exception as e:
        print("Ошибка при обращении к OpenAI API:", str(e))
        return JsonResponse({"error": "Что-то пошло не так!"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_familiar_drug(request):
    try:
        body = json.loads(request.body)
        drug = body.get("drug", "")
        print(f"Запрос на получение знакомого лекарства: {drug}")
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Вы полезный медицинский помощник."},
                {"role": "user", "content": f"Приведи более знакомую для обычных людей версию этого лекарства. Выведи в формате одного слова. Например если вывод TENOFOVIR DISOPROXIL FUMARATE то выведи Тенофовир: {drug}."},
            ],
        }
        headers = {
            "Authorization": f'Bearer {os.environ.get("API_KEY")}',
            "Content-Type": "application/json",
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        data = response.json()
        familiar_version = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return JsonResponse({"familiar_version": familiar_version})
    except Exception as e:
        print("Ошибка при обработке названия лекарства:", str(e))
        return JsonResponse({"error": "Не удалось преобразовать название лекарства."}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def translate(request):
    try:
        body = json.loads(request.body)
        text = body.get("text", "")
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Вы переводчик. Переведите следующий текст на русский язык."},
                {"role": "user", "content": text},
            ],
        }
        headers = {
            "Authorization": f'Bearer {os.environ.get("API_KEY")}',
            "Content-Type": "application/json",
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        data = response.json()
        translated_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return JsonResponse({"translated_text": translated_text})
    except Exception as e:
        print("Ошибка при переводе текста:", str(e))
        return JsonResponse({"error": "Не удалось выполнить перевод."}, status=500)
