from django.http import HttpResponse, HttpResponseServerError,\
    HttpResponseBadRequest
from gitstack.models import Repository, User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json, re

# user rest api
@csrf_exempt
def rest_user(request):
    try:
        # create user
        if request.method == 'POST':
            # get the username/password from the request
            username = request.POST['username']
            password = request.POST['password']
            user = User(username, password)
            user.create()
            return HttpResponse("User created")
        # get retrieve_all the users
        if request.method == 'GET':
            # convert list of objects to list of strings
            user_list_str = []
            user_list_obj = User.retrieve_all()
            for user in user_list_obj:   
                user_list_str.append(user.username)
            json_reply = json.dumps(user_list_str)
            return HttpResponse(json_reply)
        # update the user
        if request.method == 'PUT':
            # retrieve the credentials from the json
            credentials = json.loads(request.raw_post_data)
            # create an instance of the user and update it
            user = User(credentials['username'], credentials['password'])
            user.update()
            return HttpResponse("User successfully updated")
        
    except Exception as e:
        return HttpResponseServerError(e)

# web interface (gitweb) rest api
@csrf_exempt
def rest_repo_web_interface(request, repo_name):
    try:
        repo = Repository(repo_name)
        # get if the web interface is enabled
        if request.method == 'GET':
            # create a dictionary with the enabled parameter
            permissions = {'enabled' : repo.web_interface}
    
            json_reply = json.dumps(permissions)
            return HttpResponse(json_reply)
        # update the web interface permissions
        if request.method == 'PUT':
            # retrieve the dictionary from the request
            web_interface_dic = json.loads(request.raw_post_data)
            # update the repository
            repo.web_interface = web_interface_dic['enabled']
            repo.save()
            # create the message
            if repo.web_interface:
                message = "Web interface successfully enabled"
            else:
                message = "Web interface successfully disabled"
            return HttpResponse(message)
        
    except Exception as e:
        return HttpResponseServerError(e)


def rest_user_action(request, username):
    try:
        if request.method == 'DELETE':
            # retrieve the username from the json
            user = User(username)
            # delete the user
            user.delete()
            return HttpResponse(username + " has been deleted")
    except Exception as e:
        return HttpResponseServerError(e)


# create a repository
def rest_repository(request):
    # Add new repository
    if request.method == 'POST':
        name=request.POST['name']
        try:
            # check the repo name
            matcher = re.compile("^[A-Za-z]\w{2,}$")
            if matcher.match(name) is None:
                raise Exception("Please enter an alphanumeric name without spaces")
            if(name == ""):
                raise Exception("Please enter a non empty name")
            # create the repo
            repository = Repository(name)
            repository.create()
        except WindowsError as e:
            return HttpResponseServerError(e.strerror)
        except Exception as e:
            return HttpResponseServerError(e)
        
        return HttpResponse("The repository has been successfully created")
    # List retrieve_all repositories
    if request.method == 'GET':
        try:
            # change to the repository directory
            repositories = Repository.retrieve_all()
            # remove the .git at the end
            repositories_name = map(lambda foo: foo.__unicode__(), repositories)
            json_reply = json.dumps(repositories_name)
            return HttpResponse(json_reply)
        except WindowsError as e:
            return HttpResponseServerError(e.strerror)
        

# delete a repository
def rest_repo_action(request, repo_name):
    try:
        if request.method == 'DELETE':
            repo = Repository(repo_name)
            # delete the repo
            repo.delete()
            return HttpResponse(repo.name + " has been deleted")
    except Exception as e:
        return HttpResponseServerError(e)

# Add/Remove users on a repository
@csrf_exempt
def rest_repo_user(request, repo_name, username):
    repo = Repository(repo_name)
    user = User(username)

    # Add user
    if request.method == 'POST':
        # Get the repository and add the user
        repo.add_user(user)
        repo.add_user_read(user)
        repo.add_user_write(user)
        repo.save()
        return HttpResponse("User " + username + " added to " + repo_name)
    # Delete the user
    if request.method == 'DELETE':
        # Remove the user from the repository
        repo.remove_user(user)
        repo.save()
        return HttpResponse(username + " removed from " + repo_name)
    # Get the user permissions
    if request.method == 'GET':
        permissions = {'read' : False, 'write' : False}
        # retrieve the list of read and write users
        user_read_list = repo.user_read_list
        user_write_list = repo.user_write_list
        # check if the user has read and write access
        if user in user_read_list:
            permissions['read'] = True
        if user in user_write_list:
            permissions['write'] = True
            
        # reply with the json permission object
        json_reply = json.dumps(permissions)
        return HttpResponse(json_reply)
    
    if request.method == 'PUT':
        # retrieve the credentials from the json
        permissions = json.loads(request.raw_post_data)

        # Get the old password and new password
        if 'read' in permissions:
            # add the read permission to the repo
            if permissions['read']:
                repo.add_user_read(user)
            else:
                repo.remove_user_read(user)

        if 'write' in permissions:
            # add the write permission to the repo
            if permissions['write']:
                repo.add_user_write(user)
            else:
                repo.remove_user_write(user)
                
        repo.save()
        return HttpResponse(user.username + "'s permissions updated")


    
# Get all the users on a specific repository
@csrf_exempt
def rest_repo_user_all(request, repo_name):
    # Get the repository and add the user
    repo = Repository(repo_name)
    users = repo.user_list
    users_name = map(lambda foo: foo.__unicode__(), users)
    json_reply = json.dumps(users_name)
    return HttpResponse(json_reply)
    
# change admin password
def rest_admin(request):
    # update the user
    if request.method == 'PUT':
        # retrieve the credentials from the json
        passwords = json.loads(request.raw_post_data)
        # Get the old password and new password
        old_password = passwords['oldPassword']
        new_password = passwords['newPassword']
        # Check of the old password is correct 
        user = authenticate(username='admin', password=old_password)
        if user is not None:
            # Change the password
            user.set_password(new_password)
            user.save()
            return HttpResponse("User successfully updated")
        else:
            return HttpResponseServerError("Your current administrator password is not correct.")





