from django.db import IntegrityError
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import User , Project ,Hardware , User_Project
import json
from django.utils import timezone
from datetime import datetime
import logging


# for creating user
@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            contact = data.get('contact')

            if not username or not email or not contact or not password:
                return JsonResponse({'error': 'All fields are required.'}, status=400)
            user = User(username=username, email=email, contact=contact, password=password)
            user.save()

            return JsonResponse({'message': 'User created successfully.'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)



#for login user
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            try:
                user = User.objects.get(username=username)
                
                if user.password == password:
                    return JsonResponse({'success': True, 'message': 'Login successful'}, status=200)
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid username or password'}, status=401)
            
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid username or password'}, status=401)
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid data'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)



#inserting project values to database
@csrf_exempt
def create_project(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check required fields
            required_fields = [
                'user_id',  'total_power', 'kw', 'kva', 
                'power_factor', 'frequency', 'current_l1', 'current_l2', 
                'current_l3', 'volt_l1', 'volt_l2', 'volt_l3', 
                'power_l1', 'power_l2', 'power_l3'
            ]
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing field: {field}'}, status=400)
            
            user = User.objects.get(pk=data['user_id'])
            # hardware = Hardware.objects.get(pk=data['hardware_id'])
            
            project = Project.objects.create(
                user_id=user,
                # hardware_id=hardware,
                total_power=data['total_power'],
                kw=data['kw'],
                kva=data['kva'],
                power_factor=data['power_factor'],
                frequency=data['frequency'],
                current_l1=data['current_l1'],
                current_l2=data['current_l2'],
                current_l3=data['current_l3'],
                volt_l1=data['volt_l1'],
                volt_l2=data['volt_l2'],
                volt_l3=data['volt_l3'],
                power_l1=data['power_l1'],
                power_l2=data['power_l2'],
                power_l3=data['power_l3']
            )
            return JsonResponse({'message': 'Project created successfully', 'project_id': project.project_id}, status=200)
        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=400)
        except Hardware.DoesNotExist:
            return JsonResponse({'error': 'Hardware not found'}, status=400)
        except IntegrityError as e:
            return JsonResponse({'error': f'Integrity error: {str(e)}'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': f'Validation error: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)




#getting current power and voltage values to show in linechart

@csrf_exempt
def latest_project_data(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')

        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)

        try:
            projects = Project.objects.filter(user_id=user_id).order_by('-last_updated')

            if not projects.exists():
                return JsonResponse({'error': 'No projects found for this user'}, status=404)

            current_data = {
                'L1': [],
                'L2': [],
                'L3': []
            }
            voltage_data = {
                'L1': [],
                'L2': [],
                'L3': []
            }
            power_data = {
                'L1': [],
                'L2': [],
                'L3': []
            }

            today_date = datetime.today().date()

            for project in projects:
                try:
                    # Make the project datetime timezone-aware
                    project_datetime = timezone.make_aware(datetime.combine(today_date, project.time))
                    time_ms = int(project_datetime.timestamp() * 1000)

                    current_data['L1'].append([time_ms, float(project.current_l1)])
                    current_data['L2'].append([time_ms, float(project.current_l2)])
                    current_data['L3'].append([time_ms, float(project.current_l3)])

                    voltage_data['L1'].append([time_ms, float(project.volt_l1)])
                    voltage_data['L2'].append([time_ms, float(project.volt_l2)])
                    voltage_data['L3'].append([time_ms, float(project.volt_l3)])

                    power_data['L1'].append([time_ms, float(project.power_l1)])
                    power_data['L2'].append([time_ms, float(project.power_l2)])
                    power_data['L3'].append([time_ms, float(project.power_l3)])
                except Exception as e:
                    return JsonResponse({'error': f'Error processing project data: {str(e)}'}, status=500)

            response_data = {
                'current': [
                    {'name': label, 'data': data}
                    for label, data in current_data.items()
                ],
                'voltage': [
                    {'name': label, 'data': data}
                    for label, data in voltage_data.items()
                ],
                'power': [
                    {'name': label, 'data': data}
                    for label, data in power_data.items()
                ]
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
        
        

#getting whole user data
@csrf_exempt
def get_user_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            if not user_id:
                return JsonResponse({'error': 'User ID is required.'}, status=400)
            
            try:
                user_data = Project.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'error': 'No data found for this user.'}, status=404)
            
            response_data = {
                'user_id': user_id,
                'total_power': user_data.total_power,
                'kw': user_data.kw,
                'kva': user_data.kva,
                'power_factor': user_data.power_factor,
                'frequency': user_data.frequency,
                'current_l1': user_data.current_l1,
                'current_l2': user_data.current_l2,
                'current_l3': user_data.current_l3,
                'volt_l1': user_data.volt_l1,
                'volt_l2': user_data.volt_l2,
                'volt_l3': user_data.volt_l3,
                'power_l1': user_data.power_l1,
                'power_l2': user_data.power_l2,
                'power_l3': user_data.power_l3,
            }
            
            return JsonResponse(response_data, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)




#getting total number of users
@csrf_exempt
def total_uers(request):
    if request.method == 'GET':
        try:
            user_count = User.objects.count()
            return JsonResponse({'total_users' : user_count}, status = 200)
        except Exception as e :
            return JsonResponse({'error' : str(e)}, status = 500)
    return JsonResponse({'error': 'invalid method'}, status = 405)




#getting frequency and power factor
logger = logging.getLogger(__name__)

@csrf_exempt
def get_latest_project_data(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')

        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)

        try:
            latest_project = Project.objects.filter(user_id=user_id).order_by('-last_updated').first()

            if not latest_project:
                return JsonResponse({'error': 'No projects found for this user'}, status=404)

            response_data = {
                'frequency': latest_project.frequency,
                'power_factor': latest_project.power_factor,
                'last_updated': latest_project.last_updated,
            }
            
            # Logging for debugging
            logger.info(f"Latest project data for user {user_id}: {response_data}")

            return JsonResponse(response_data, status=200)

        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
        except Exception as e:
            logger.error(f"Error fetching latest project data: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)




#adding hardware to database
@csrf_exempt  
def add_hardware(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
        
            project_id = data.get('project_id')
            hardware_name = data.get('hardware_name')
            serial_number = data.get('serial_number', '') 
            is_connected = data.get('is_connected', False)  
            
            try:
                project = Project.objects.get(project_id=project_id)
            except Project.DoesNotExist:
                return JsonResponse({"error": "Project not found."}, status=404)
            
            hardware = Hardware.objects.create(
                project_id=project,
                name=hardware_name,
                serial_number=serial_number,
                is_connected=is_connected
            )
            
            return JsonResponse({"message": "Hardware added successfully!", "hardware_id": hardware.hardware_id}, status=201)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)




#getting total number of hardware......
@csrf_exempt
def hardware_count(request , project_id):
    if request.method == 'GET':
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'Error' : 'Project not found'}, status = 404 )
        
        total_hardware = Hardware.objects.filter(project_id=project).count()
        return JsonResponse({'project_id' : project_id , 'hardware_count' : total_hardware})
    return JsonResponse({'Error' : 'invalid method'}, status = 400)
            





#getting connected hardware count
@csrf_exempt
def connected_hardware_count(request , project_id):
    if request.method == 'GET':
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'Error' : 'Project not exist'}, status = 404)
        
        count = Hardware.objects.filter(project_id=project , is_connected=True).count()
        return JsonResponse({'project_id' : project_id , 'count' : count})
    return JsonResponse({'error' : 'invalid request'}, status = 400)
        




#user_project related table view
@csrf_exempt
def user_project(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            project_id = data.get('project_id')
            
            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'Error' : 'User not found'}, status =404)
            
            try:
                project = Project.objects.get(project_id=project_id)
            except Project.DoesNotExist:
                return JsonResponse({'Error' : 'Project not found'}, status = 404)
            
            user_project = User_Project.objects.create(user_id=user , project_id=project)
            return JsonResponse({
                'up_id' : user_project.up_id,
                'user_id' : user_project.user_id.user_id,
                'project_id' : user_project.project_id.project_id
            },status=201)
        except json.JSONDecodeError:
            return JsonResponse({'Error' : 'Invalid json'})
    return JsonResponse({'Error' : 'Invvalid method'},status  = 400)



#getting the whole user
@csrf_exempt
def fetching_users(request):
    users = User.objects.all().values('user_id' , 'username' , 'email' , 'contact')
    
    user_list = list(users)
    return JsonResponse(user_list , safe=False)


#for deleting user
@csrf_exempt
def delete_user(request , user_id):
    if request.method == 'POST':
        try:
            user = get_object_or_404(User , user_id = user_id)
            user.delete()
            return JsonResponse({'message' : 'User Deleted Successfully'}, status=200)
        except Exception as e :
            return JsonResponse({'error' : str(e)}, status= 500)
    return JsonResponse({'error' : 'invalid request method'}, status = 405)
            

#for updating user
@csrf_exempt
def update_user(request , user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            user = get_object_or_404(User , user_id=user_id)
            
            user.username = data.get('username' ,user.username)
            user.email = data.get('email', user.email)
            user.contact = data.get('contact', user.contact)
            user.password = data.get('password', user.password)
            
            user.save()
            
            return JsonResponse({'message' : 'User updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error' : str(e)}, status = 500)
    return JsonResponse({'error' : 'invalid Http method'}, status = 405)
            
            