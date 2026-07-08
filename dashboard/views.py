from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import never_cache

from .forms import ExcelUploadForm
from .utils.excel_parser import parse_excel_in_memory

from django.contrib.auth.views import redirect_to_login

def is_rh_member(user):
    """
    Checks if the user has explicit RH/Departamento Pessoal permission:
    either belongs to group 'RH' / 'Departamento Pessoal' or has the permission 'dashboard.view_rh_dashboard'.
    Admin users (is_staff / is_superuser) do NOT bypass this.
    """
    if not user.is_authenticated:
        return False
    
    in_group = user.groups.filter(name__in=['RH', 'Departamento Pessoal']).exists()
    
    if user.is_superuser:
        # A superuser must be explicitly in the authorized group or have the permission in their direct permissions
        has_explicit_perm = user.groups.filter(permissions__codename='view_rh_dashboard').exists() or \
                            user.user_permissions.filter(codename='view_rh_dashboard').exists()
        return in_group or has_explicit_perm
        
    return in_group or user.has_perm('dashboard.view_rh_dashboard')

def login_view(request):
    if request.user.is_authenticated:
        if is_rh_member(request.user):
            return redirect('dashboard')
        return redirect('acesso_negado')

    error_msg = None
    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '')
        user = authenticate(username=u, password=p)
        if user is not None:
            login(request, user)
            if is_rh_member(user):
                return redirect('dashboard')
            else:
                return redirect('acesso_negado')
        else:
            error_msg = "Usuário ou senha incorretos."

    return render(request, 'login.html', {'error_msg': error_msg})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')

def acesso_negado(request):
    # Ensure standard context check so headers can render correctly
    is_rh = is_rh_member(request.user) if request.user.is_authenticated else False
    response = render(request, 'acesso_negado.html', {'is_rh_user': is_rh}, status=403)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    return response

def dashboard_view(request):
    # 1. Access validation
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path(), 'login')

    is_rh = is_rh_member(request.user)
    if not is_rh:
        return redirect('acesso_negado')

    context = {
        'form': ExcelUploadForm(),
        'parsed_data': None,
        'error_msg': None,
        'is_rh_user': True
    }

    response_status = 200

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            behavior = form.cleaned_data['default_unit_behavior']
            
            try:
                file_content = excel_file.read()
                # Parse Excel in memory
                result = parse_excel_in_memory(file_content, default_unit_behavior=behavior)
                
                if result.get('success'):
                    context['parsed_data'] = result
                else:
                    context['error_msg'] = result.get('error_msg')
                    context['form'] = form
            except Exception:
                # Privacy-compliant: Do not log or show personal file path / trace to user
                context['error_msg'] = "Ocorreu um erro ao processar o arquivo. Verifique o formato."
                context['form'] = form
        else:
            context['form'] = form

    response = render(request, 'dashboard.html', context, status=response_status)
    # Strictly configure Cache-Control to prevent client storage of medical data
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    return response
