import io
import openpyxl
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile

from .utils.excel_parser import parse_excel_in_memory, parse_quantity, parse_date, normalize_inss_value

def create_in_memory_xlsx(headers, rows, sheet_name="Planilha1"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(headers)
    for row in rows:
        ws.append(row)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()

class DashboardAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
        self.acesso_negado_url = reverse('acesso_negado')
        
        # Create standard user
        self.user = User.objects.create_user(username='colaborador', password='password123')
        
        # Create superuser / staff
        self.superuser = User.objects.create_superuser(username='admin', password='password123')
        
        # Create Departamento Pessoal user
        self.dp_user = User.objects.create_user(username='dp_analista', password='password123')
        self.dp_group, _ = Group.objects.get_or_create(name='Departamento Pessoal')
        self.dp_user.groups.add(self.dp_group)

        # Create legacy RH group user to verify backwards compatibility
        self.rh_user = User.objects.create_user(username='rh_analista', password='password123')
        self.rh_group, _ = Group.objects.get_or_create(name='RH')
        self.rh_user.groups.add(self.rh_group)

    def test_unauthenticated_user_redirected(self):
        """Unauthenticated user trying to access dashboard is redirected to login."""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.dashboard_url}")

    def test_standard_user_blocked(self):
        """Authenticated user without DP group is redirected to access denied."""
        self.client.login(username='colaborador', password='password123')
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, self.acesso_negado_url, target_status_code=403)
        
        # Checking status code for access denied page
        response = self.client.get(self.acesso_negado_url)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Departamento Pessoal", status_code=403)
        self.assertNotContains(response, "RH", status_code=403)

    def test_admin_blocked_without_explicit_authorized_group(self):
        """Superuser/staff user without DP/RH group is redirected to access denied."""
        self.client.login(username='admin', password='password123')
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, self.acesso_negado_url, target_status_code=403)

    def test_dp_user_allowed(self):
        """Authenticated user in the Departamento Pessoal group can access the dashboard."""
        self.client.login(username='dp_analista', password='password123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Painel do Departamento Pessoal")
        self.assertNotContains(response, "Painel do RH")

    def test_legacy_rh_user_allowed(self):
        """Legacy users belonging to group 'RH' are still allowed to access (backwards compatibility)."""
        self.client.login(username='rh_analista', password='password123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Painel do Departamento Pessoal")


class ExcelParserTests(TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date(datetime.date(2026, 7, 8)), datetime.date(2026, 7, 8))
        self.assertEqual(parse_date("08/07/2026"), datetime.date(2026, 7, 8))
        self.assertEqual(parse_date("2026-07-08"), datetime.date(2026, 7, 8))
        self.assertIsNone(parse_date("invalid-date"))
        self.assertIsNone(parse_date(None))

    def test_parse_quantity(self):
        # Numeric values without unit
        self.assertEqual(parse_quantity(3, "reject"), (None, None))
        self.assertEqual(parse_quantity(3.5, "days"), (3.5, "days"))
        self.assertEqual(parse_quantity(8, "hours"), (8.0, "hours"))
        
        # String values with explicit unit
        self.assertEqual(parse_quantity("2 dias"), (2.0, "days"))
        self.assertEqual(parse_quantity("1 dia"), (1.0, "days"))
        self.assertEqual(parse_quantity("4 horas"), (4.0, "hours"))
        self.assertEqual(parse_quantity("4h"), (4.0, "hours"))
        self.assertEqual(parse_quantity("8:30"), (8.5, "hours"))
        
        # Edge cases / Invalid formats
        self.assertEqual(parse_quantity("invalid quantity"), (None, None))
        self.assertEqual(parse_quantity(None), (None, None))

    def test_normalize_inss_value(self):
        # SIM values
        self.assertEqual(normalize_inss_value("SIM"), ("SIM", None))
        self.assertEqual(normalize_inss_value("Sim"), ("SIM", None))
        self.assertEqual(normalize_inss_value("sim"), ("SIM", None))
        self.assertEqual(normalize_inss_value("s"), ("SIM", None))
        self.assertEqual(normalize_inss_value(" sim  "), ("SIM", None))

        # NÃO values
        self.assertEqual(normalize_inss_value("NÃO"), ("NÃO", None))
        self.assertEqual(normalize_inss_value("Não"), ("NÃO", None))
        self.assertEqual(normalize_inss_value("não"), ("NÃO", None))
        self.assertEqual(normalize_inss_value("NAO"), ("NÃO", None))
        self.assertEqual(normalize_inss_value("Nao"), ("NÃO", None))
        self.assertEqual(normalize_inss_value("nao"), ("NÃO", None))
        self.assertEqual(normalize_inss_value("n"), ("NÃO", None))
        self.assertEqual(normalize_inss_value(" não  "), ("NÃO", None))

        # Empty/Blank values
        self.assertEqual(normalize_inss_value(None), ("NÃO INFORMADO", None))
        self.assertEqual(normalize_inss_value(""), ("NÃO INFORMADO", None))
        self.assertEqual(normalize_inss_value("   "), ("NÃO INFORMADO", None))

        # Invalid values
        val, warn = normalize_inss_value("talvez")
        self.assertEqual(val, "NÃO INFORMADO")
        self.assertIsNotNone(warn)
        self.assertIn("inválido", warn)

    def test_parse_excel_inss_headers_and_aggregation(self):
        # Test various equivalent headers for INSS
        headers_variants = [
            "Houve Afastamento Pelo INSS?",
            "Houve afastamento pelo INSS",
            "HOUVE AFASTAMENTO PELO INSS?",
            "Houve Afastamento Pelo INSS ?",
            " Houve \n afastamento \t pelo INSS? "
        ]
        
        for head in headers_variants:
            headers = ["Nome do colaborador", "Função do colaborador", "Data inicial do atestado", "CID", "Quantidade de dias/ HORAS", head]
            rows = [
                ["Ana Silva", "Analista", "01/07/2026", "M54.5", "2 dias", "Sim"],
                ["Carlos Souza", "Gerente", "02/07/2026", "J11", "4 horas", "Não"],
                ["Bruno Alves", "Suporte", "03/07/2026", "F43", "1 dia", ""], # Empty
                ["Daniel Santos", "Dev", "04/07/2026", "Z00", "1 dia", "talvez"], # Invalid
            ]
            content = create_in_memory_xlsx(headers, rows)
            result = parse_excel_in_memory(content, default_unit_behavior="reject")
            
            self.assertTrue(result["success"])
            self.assertTrue(result["inss_available"])
            self.assertEqual(result["indicators"]["inss_sim_count"], 1) # Ana
            self.assertEqual(result["indicators"]["inss_nao_count"], 1) # Carlos
            self.assertEqual(result["indicators"]["inss_nao_informado_count"], 2) # Bruno (empty) + Daniel (invalid)
            
            # Percentual calculated only on SIM + NÃO: (1 / (1 + 1)) * 100 = 50.0%
            self.assertEqual(result["indicators"]["inss_percentage_sim"], 50.0)
            
            # Invalid value Daniel must generate an inconsistency warning but not skip the row
            self.assertEqual(result["valid_count"], 4)
            self.assertEqual(len(result["inconsistencies"]), 1)
            self.assertEqual(result["inconsistencies"][0]["erro"], "Valor inválido na coluna do INSS")
            self.assertIn("talvez", result["inconsistencies"][0]["detalhe"])

    def test_parse_excel_old_format_compatibility(self):
        # 5 columns spreadsheet without INSS column
        headers = ["Nome do colaborador", "Função do colaborador", "Data inicial do atestado", "CID", "Quantidade de dias/ HORAS"]
        rows = [
            ["Ana Silva", "Analista", "01/07/2026", "M54.5", "2 dias"],
            ["Carlos Souza", "Gerente", "02/07/2026", "J11", "4 horas"],
        ]
        content = create_in_memory_xlsx(headers, rows)
        result = parse_excel_in_memory(content, default_unit_behavior="reject")
        
        self.assertTrue(result["success"])
        self.assertFalse(result["inss_available"])
        self.assertEqual(result["valid_count"], 2)
        # Should not throw errors and should have N/A indicators
        self.assertEqual(result["indicators"]["inss_sim_count"], 0)
        self.assertEqual(result["indicators"]["inss_nao_count"], 0)
        self.assertEqual(result["indicators"]["inss_nao_informado_count"], 0)
        self.assertEqual(result["indicators"]["inss_percentage_sim"], 0.0)

    def test_absence_aggregation_and_combined_representation(self):
        # Fictional collaborator "Pessoa Teste" with 1 day, 1 day, and 4 hours
        headers = ["Nome do colaborador", "Função do colaborador", "Data inicial do atestado", "CID", "Quantidade de dias/ HORAS", "INSS"]
        rows = [
            ["Pessoa Teste", "Operador", "01/07/2026", "A10", "1 dia", "Não"],
            ["Pessoa Teste", "Operador", "02/07/2026", "A10", "1 dia", "Não"],
            ["Pessoa Teste", "Operador", "03/07/2026", "A10", "4 horas", "Sim"],
        ]
        content = create_in_memory_xlsx(headers, rows)
        result = parse_excel_in_memory(content, default_unit_behavior="reject")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["valid_count"], 3)
        
        # Verify collaborator summary table details
        colab_summary = next(item for item in result["summary_table"] if item["colaborador"] == "Pessoa Teste")
        self.assertEqual(colab_summary["atestados_count"], 3)
        self.assertEqual(colab_summary["total_dias"], 2.0)
        self.assertEqual(colab_summary["total_horas"], 4.0)
        self.assertEqual(colab_summary["inss_sim_count"], 1)
        self.assertEqual(colab_summary["inss_nao_count"], 2)


class PrivacyAndCacheTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dp_user = User.objects.create_user(username='dp_user', password='password123')
        self.dp_group, _ = Group.objects.get_or_create(name='Departamento Pessoal')
        self.dp_user.groups.add(self.dp_group)

    def test_cache_control_headers(self):
        """Dashboard view must return Cache-Control: no-store, private to protect health details."""
        self.client.login(username='dp_user', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        cache_control = response.get('Cache-Control')
        self.assertIn('no-store', cache_control)
        self.assertIn('private', cache_control)

    def test_no_model_exists_for_atestados(self):
        """Verify that indeed no persistent models exist for atestados."""
        from django.apps import apps
        dashboard_app = apps.get_app_config('dashboard')
        models = list(dashboard_app.get_models())
        self.assertEqual(len(models), 0)
